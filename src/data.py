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

# Phase 2 (docs/Decision_log.md, P2-DS001): additional NHANES components
# evaluated for whether richer predictors narrow the range-specific error
# documented for the Version-1 model. Not used by src/pipeline.py's primary
# `build_pipeline()` / the deployed app — only by `build_ml_dataset_v2()`
# and `src/pipeline.build_pipeline_v2()` below.
NHANES_DATASETS_V2_EXTRA = {
    "smoking": {
        "filename": "P_SMQ.XPT",
        "url": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_SMQ.XPT",
    },
    "physical_activity": {
        "filename": "P_PAQ.XPT",
        "url": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_PAQ.XPT",
    },
    "alcohol_use": {
        "filename": "P_ALQ.XPT",
        "url": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_ALQ.XPT",
    },
    "biochemistry_profile": {
        "filename": "P_BIOPRO.XPT",
        "url": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BIOPRO.XPT",
    },
    "glycohemoglobin": {
        "filename": "P_GHB.XPT",
        "url": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_GHB.XPT",
    },
}

# Feature columns the fitted pipeline expects, in a fixed, documented order.
NUMERIC_FEATURES = ["RIDAGEYR", "BMXBMI"]
CATEGORICAL_FEATURES = ["RIAGENDR_label", "DIQ010_label"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET_COLUMN = "Average_SBP"

SEX_CATEGORIES = ["Female", "Male"]
DIABETES_CATEGORIES = ["No", "Borderline", "Yes"]

# Phase 2 additional features (docs/Decision_log.md, P2-FE001-P2-FE005).
# Adult-only: SMQ/PAQ/ALQ are not administered under age 18, and BIOPRO/GHB
# (blood draw) are far sparser under 18 too (see P2-DS001) - so the v2
# cohort is restricted to age >= 18, unlike the age >= 8 v1 cohort.
MIN_AGE_V2 = 18
NUMERIC_FEATURES_V2_EXTRA = ["LBXSCR", "LBXGH"]
CATEGORICAL_FEATURES_V2_EXTRA = ["current_smoker_label", "PAQ650_label", "ALQ111_label"]
NUMERIC_FEATURES_V2 = NUMERIC_FEATURES + NUMERIC_FEATURES_V2_EXTRA
CATEGORICAL_FEATURES_V2 = CATEGORICAL_FEATURES + CATEGORICAL_FEATURES_V2_EXTRA
FEATURE_COLUMNS_V2 = NUMERIC_FEATURES_V2 + CATEGORICAL_FEATURES_V2

YES_NO_CATEGORIES = ["No", "Yes"]


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


def download_raw_data_v2_extra(raw_dir: Path = RAW_DATA_DIR) -> None:
    """Download the Phase 2 NHANES files (docs/Decision_log.md, P2-DS001)."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    for info in NHANES_DATASETS_V2_EXTRA.values():
        destination = raw_dir / info["filename"]
        if destination.exists():
            continue
        response = requests.get(info["url"], timeout=60)
        response.raise_for_status()
        destination.write_bytes(response.content)


def _derive_current_smoker(smq020: float | None, smq040: float | None) -> str | None:
    """SMQ040 (current smoking frequency) is only asked when SMQ020 == 1
    (smoked >=100 cigarettes lifetime), so the two columns must be combined
    to get one clean Yes/No "currently smokes" feature (P2-FE001)."""
    if pd.isna(smq020):
        return None
    if smq020 == 2:  # never smoked >=100 cigarettes lifetime
        return "No"
    if smq020 == 1:
        if smq040 in (1, 2):  # every day / some days
            return "Yes"
        if smq040 == 3:  # not at all (former smoker)
            return "No"
    return None  # refused/don't know on either item


def build_training_cohort_v2(raw_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Phase 2 sensitivity cohort: build_training_cohort() plus smoking,
    physical activity, alcohol use, creatinine, and HbA1c (docs/Decision_log.md,
    P2-DS001-P2-FE005). Restricted to age >= 18 because none of the added
    NHANES items are collected below that age (see module docstring above).
    """
    base_df = build_training_cohort(raw_dir)

    smq = pd.read_sas(raw_dir / "P_SMQ.XPT")[["SEQN", "SMQ020", "SMQ040"]]
    paq = pd.read_sas(raw_dir / "P_PAQ.XPT")[["SEQN", "PAQ650"]]
    alq = pd.read_sas(raw_dir / "P_ALQ.XPT")[["SEQN", "ALQ111"]]
    bio = pd.read_sas(raw_dir / "P_BIOPRO.XPT")[["SEQN", "LBXSCR"]]
    ghb = pd.read_sas(raw_dir / "P_GHB.XPT")[["SEQN", "LBXGH"]]

    v2_df = (
        base_df[base_df["RIDAGEYR"] >= MIN_AGE_V2]
        .merge(smq, on="SEQN", how="left", validate="one_to_one")
        .merge(paq, on="SEQN", how="left", validate="one_to_one")
        .merge(alq, on="SEQN", how="left", validate="one_to_one")
        .merge(bio, on="SEQN", how="left", validate="one_to_one")
        .merge(ghb, on="SEQN", how="left", validate="one_to_one")
    )

    v2_df["current_smoker_label"] = v2_df.apply(
        lambda row: _derive_current_smoker(row["SMQ020"], row["SMQ040"]), axis=1
    )
    v2_df["PAQ650_label"] = v2_df["PAQ650"].map({1: "Yes", 2: "No"})
    v2_df["ALQ111_label"] = v2_df["ALQ111"].map({1: "Yes", 2: "No"})

    return v2_df


def build_ml_dataset_v2(raw_dir: Path = RAW_DATA_DIR) -> tuple[pd.DataFrame, pd.Series]:
    """Phase 2 regression cohort: same exclusions as build_ml_dataset() (M005),
    plus the five added predictors, complete-case only (P2-DS001)."""
    v2_df = build_training_cohort_v2(raw_dir)
    v2_reg_df = v2_df[v2_df["DIQ010"] != 9].copy()

    ml_df = v2_reg_df[[TARGET_COLUMN] + FEATURE_COLUMNS_V2].dropna().copy()
    X = ml_df[FEATURE_COLUMNS_V2]
    y = ml_df[TARGET_COLUMN]
    return X, y


def build_ml_dataset_v1_features_adult_subsample(
    raw_dir: Path = RAW_DATA_DIR,
) -> tuple[pd.DataFrame, pd.Series]:
    """The Version-1 feature set (age, BMI, sex, diabetes only), restricted to
    the same age >= 18, complete-case-on-v2-features population as
    build_ml_dataset_v2(). This isolates the effect of the added predictors
    from the effect of restricting the population to adults: comparing this
    against build_ml_dataset() (age >= 8) would confound "richer features"
    with "different, older population" (P2-M001)."""
    v2_df = build_training_cohort_v2(raw_dir)
    v2_reg_df = v2_df[v2_df["DIQ010"] != 9].copy()

    all_cols = [TARGET_COLUMN] + FEATURE_COLUMNS_V2
    complete_seqn = v2_reg_df[all_cols].dropna().index

    ml_df = v2_reg_df.loc[complete_seqn, [TARGET_COLUMN] + FEATURE_COLUMNS].copy()
    X = ml_df[FEATURE_COLUMNS]
    y = ml_df[TARGET_COLUMN]
    return X, y
