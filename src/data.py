"""
Data acquisition and preparation for the Average-SBP reliability study.

This module reproduces, as reusable functions, the exact data-preparation
steps performed in ``notebook/01-project-notebook-reframed-reliability.ipynb``:
download (if needed) -> load -> merge -> clean -> engineer -> filter to the
Version-1 training cohort. See docs/Decision_log.md for the rationale behind
each step (DE001-DE008, FE001-FE004).

Nothing here re-fits or re-tunes any model; this is strictly the data layer
so that training (src/train.py) and inference (src/predict.py) share one
source of truth instead of duplicating notebook logic.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

NHANES_DATASETS = {
    "demographics": {
        "filename": "P_DEMO.XPT",
        "url": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DEMO.XPT",
    },
    "body_measures": {
        "filename": "P_BMX.XPT",
        "url": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BMX.XPT",
    },
    "blood_pressure": {
        "filename": "P_BPXO.XPT",
        "url": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BPXO.XPT",
    },
    "bp_questionnaire": {
        "filename": "P_BPQ.XPT",
        "url": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BPQ.XPT",
    },
    "diabetes_questionnaire": {
        "filename": "P_DIQ.XPT",
        "url": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DIQ.XPT",
    },
}

# Feature columns the fitted pipeline expects, in a fixed, documented order.
NUMERIC_FEATURES = ["RIDAGEYR", "BMXBMI"]
CATEGORICAL_FEATURES = ["RIAGENDR_label", "DIQ010_label"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET_COLUMN = "Average_SBP"

SEX_CATEGORIES = ["Female", "Male"]
DIABETES_CATEGORIES = ["No", "Borderline", "Yes"]


def download_raw_data(raw_dir: Path = RAW_DATA_DIR) -> None:
    """Download the five NHANES .XPT files if they are not already present."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    for info in NHANES_DATASETS.values():
        destination = raw_dir / info["filename"]
        if destination.exists():
            continue
        response = requests.get(info["url"], timeout=60)
        response.raise_for_status()
        destination.write_bytes(response.content)


def _load_raw(raw_dir: Path = RAW_DATA_DIR) -> dict[str, pd.DataFrame]:
    return {
        "demo": pd.read_sas(raw_dir / "P_DEMO.XPT"),
        "bmx": pd.read_sas(raw_dir / "P_BMX.XPT"),
        "bpxo": pd.read_sas(raw_dir / "P_BPXO.XPT"),
        "bpq": pd.read_sas(raw_dir / "P_BPQ.XPT"),
        "diq": pd.read_sas(raw_dir / "P_DIQ.XPT"),
    }


def build_training_cohort(raw_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Reproduce model_training_df: merged, cleaned, feature-engineered cohort.

    Mirrors DE001-DE008 and FE001-FE004 in docs/Decision_log.md:
    - left-join everything onto Demographics, keyed on SEQN, validated 1:1
    - correct the pandas read_sas() near-zero-age artifact for infants (D001
      in docs/Data_issues.md)
    - engineer Average_SBP / Average_DBP as the mean of available readings
    - keep participants aged >= 8 with a non-missing Average_SBP (the
      supervised-learning cohort; DE006/DE007)
    """
    raw = _load_raw(raw_dir)

    demo_v1 = raw["demo"][["SEQN", "RIDAGEYR", "RIAGENDR"]].copy()
    bmx_v1 = raw["bmx"][["SEQN", "BMXBMI"]].copy()
    bpxo_v1 = raw["bpxo"][
        ["SEQN", "BPXOSY1", "BPXOSY2", "BPXOSY3", "BPXODI1", "BPXODI2", "BPXODI3"]
    ].copy()
    bpq_v1 = raw["bpq"][["SEQN", "BPQ050A"]].copy()
    diq_v1 = raw["diq"][["SEQN", "DIQ010"]].copy()

    model_v1_df = (
        demo_v1.merge(bmx_v1, on="SEQN", how="left", validate="one_to_one")
        .merge(bpxo_v1, on="SEQN", how="left", validate="one_to_one")
        .merge(bpq_v1, on="SEQN", how="left", validate="one_to_one")
        .merge(diq_v1, on="SEQN", how="left", validate="one_to_one")
    )

    # D001 (docs/Data_issues.md): read_sas() represents true zero as a
    # near-zero float (e.g. 5.397605e-79) for infant participants.
    model_v1_df.loc[model_v1_df["RIDAGEYR"] < 0.5, "RIDAGEYR"] = 0

    model_v1_df["Average_SBP"] = model_v1_df[
        ["BPXOSY1", "BPXOSY2", "BPXOSY3"]
    ].mean(axis=1)
    model_v1_df["Average_DBP"] = model_v1_df[
        ["BPXODI1", "BPXODI2", "BPXODI3"]
    ].mean(axis=1)

    model_training_df = model_v1_df[model_v1_df["RIDAGEYR"] >= 8].copy()
    model_training_df = model_training_df.dropna(subset=["Average_SBP"])

    model_training_df["DIQ010_label"] = model_training_df["DIQ010"].map(
        {1: "Yes", 2: "No", 3: "Borderline", 9: "Don't Know"}
    )
    model_training_df["RIAGENDR_label"] = model_training_df["RIAGENDR"].map(
        {1: "Male", 2: "Female"}
    )
    model_training_df["BPQ050A_label"] = model_training_df["BPQ050A"].map(
        {1: "Yes", 2: "No"}
    )

    return model_training_df


def build_ml_dataset(raw_dir: Path = RAW_DATA_DIR) -> tuple[pd.DataFrame, pd.Series]:
    """Reproduce ml_df / X / y: the Primary-Model regression cohort (M006).

    - excludes "Don't Know" diabetes responses (M005)
    - keeps Age, BMI, Sex, Diabetes status and the target
    - drops any remaining missing values (mainly the ~0.9% missing BMI)
    """
    model_training_df = build_training_cohort(raw_dir)
    model_reg_df = model_training_df[model_training_df["DIQ010"] != 9].copy()

    ml_df = model_reg_df[[TARGET_COLUMN] + FEATURE_COLUMNS].dropna().copy()
    X = ml_df[FEATURE_COLUMNS]
    y = ml_df[TARGET_COLUMN]
    return X, y
