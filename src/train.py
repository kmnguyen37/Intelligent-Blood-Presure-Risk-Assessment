"""
Reproducible training entry point (roadmap.md, Track 1.2).

    python -m src.train

Loads the raw NHANES extracts (downloading them if missing), rebuilds the
Version-1 training cohort, fits the pipeline defined in src/pipeline.py on
an 80/20 split (random_state=42, matching the notebooks), and writes:

    models/rf_sbp_pipeline.joblib   the complete preprocessing+model artifact
    models/metrics.json             overall + range-specific held-out metrics

This script contains no analysis, tuning, or exploration - that lives in the
notebooks, which remain the source of record for *why* Random Forest with
these hyperparameters was selected (see docs/Decision_log.md, M003-M006).
This script only reproduces the *result* of that selection as a reusable
artifact.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from src.data import PROJECT_ROOT, RAW_DATA_DIR, build_ml_dataset, download_raw_data
from src.pipeline import RANDOM_STATE, build_pipeline

MODELS_DIR = PROJECT_ROOT / "models"

SBP_RANGE_BINS = [-np.inf, 100, 120, 140, 160, np.inf]
SBP_RANGE_LABELS = ["<100", "100-119", "120-139", "140-159", "160+"]


def _range_reliability_table(y_true: pd.Series, y_pred: np.ndarray) -> list[dict]:
    """Reproduce the README "Reliability across observed SBP ranges" table.

    Residual = actual - predicted; positive means underprediction.
    """
    frame = pd.DataFrame({"y_true": y_true.to_numpy(), "y_pred": y_pred})
    frame["residual"] = frame["y_true"] - frame["y_pred"]
    frame["sbp_range"] = pd.cut(
        frame["y_true"], bins=SBP_RANGE_BINS, labels=SBP_RANGE_LABELS, right=False
    )

    rows = []
    for label in SBP_RANGE_LABELS:
        subset = frame[frame["sbp_range"] == label]
        if len(subset) == 0:
            continue
        rows.append(
            {
                "range": label,
                "n_participants": int(len(subset)),
                "mean_residual": round(float(subset["residual"].mean()), 2),
                "mae": round(float(subset["residual"].abs().mean()), 2),
                "rmse": round(float(np.sqrt((subset["residual"] ** 2).mean())), 2),
            }
        )
    return rows


def main(raw_dir: Path = RAW_DATA_DIR, models_dir: Path = MODELS_DIR) -> dict:
    download_raw_data(raw_dir)
    X, y = build_ml_dataset(raw_dir)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)

    overall = {
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "test_r2": round(float(r2_score(y_test, y_pred)), 4),
        "test_mae": round(float(mean_absolute_error(y_test, y_pred)), 2),
        "test_rmse": round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 2),
    }
    reliability = _range_reliability_table(y_test, y_pred)

    metrics = {
        "overall": overall,
        "reliability_by_sbp_range": reliability,
        "note": (
            "Near-zero aggregate error can conceal severe range-specific bias. "
            "See reliability_by_sbp_range, especially the 160+ row, before "
            "treating overall R2/MAE/RMSE as evidence of clinical usefulness."
        ),
    }

    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, models_dir / "rf_sbp_pipeline.joblib")
    (models_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))

    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=RAW_DATA_DIR)
    parser.add_argument("--models-dir", type=Path, default=MODELS_DIR)
    args = parser.parse_args()

    result = main(args.raw_dir, args.models_dir)
    print(json.dumps(result, indent=2))
