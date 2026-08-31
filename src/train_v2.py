"""
Phase 2 reproducible experiment entry point (roadmap.md Track 2 "Improve the
data and model"; docs/Decision_log.md P2-DS001-P2-M002).

    python -m src.train_v2

Tests whether the Version-1 finding (near-zero aggregate bias masking severe
underprediction at SBP >= 160) is a limitation of the four-feature predictor
set, or a limitation of the underlying population/target relationship, by
adding smoking, physical activity, alcohol use, creatinine, and HbA1c.

Because those predictors are only collected for NHANES participants aged 18+
(see src/data.py docstrings), naively comparing "v2 metrics on adults" against
the published "v1 metrics on ages 8+" would confound two different changes at
once: richer features AND a different, older population. This script instead
fits and evaluates two models on the *same* age>=18, complete-case-on-v2-
features population and the *same* train/test split:

    baseline_v1_features  age/BMI/sex/diabetes only (same features as v1)
    richer_v2_features    baseline features + smoking/activity/alcohol/labs

Any difference between them is attributable to the added predictors, not to
population selection. The originally published Version-1 metrics.json
(models/metrics.json, age >= 8, full complete-case cohort) is left untouched
and is included in the output for reference only - it is not a fair
apples-to-apples comparison point for the reasons above.

Writes:
    models/rf_sbp_pipeline_v2.joblib   the richer-features artifact only
    models/metrics_v2.json             both same-subsample models' metrics
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
from sklearn.model_selection import train_test_split

from src.data import (
    PROJECT_ROOT,
    RAW_DATA_DIR,
    build_ml_dataset_v1_features_adult_subsample,
    build_ml_dataset_v2,
    download_raw_data,
    download_raw_data_v2_extra,
)
from src.pipeline import RANDOM_STATE, build_pipeline, build_pipeline_v2
from src.train import MODELS_DIR, _range_reliability_table
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np


def _fit_and_score(pipeline, X, y, label: str) -> dict:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE
    )
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    return {
        "label": label,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "test_r2": round(float(r2_score(y_test, y_pred)), 4),
        "test_mae": round(float(mean_absolute_error(y_test, y_pred)), 2),
        "test_rmse": round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 2),
        "reliability_by_sbp_range": _range_reliability_table(y_test, y_pred),
    }, pipeline


def main(raw_dir: Path = RAW_DATA_DIR, models_dir: Path = MODELS_DIR) -> dict:
    download_raw_data(raw_dir)
    download_raw_data_v2_extra(raw_dir)

    X_baseline, y_baseline = build_ml_dataset_v1_features_adult_subsample(raw_dir)
    X_v2, y_v2 = build_ml_dataset_v2(raw_dir)

    baseline_metrics, _ = _fit_and_score(
        build_pipeline(), X_baseline, y_baseline,
        "v1_features_on_adult_subsample (age/BMI/sex/diabetes, age>=18, n=%d)" % len(X_baseline),
    )
    v2_metrics, v2_pipeline = _fit_and_score(
        build_pipeline_v2(), X_v2, y_v2,
        "v2_richer_features (+smoking/activity/alcohol/creatinine/HbA1c, age>=18, n=%d)" % len(X_v2),
    )

    published_v1_path = models_dir / "metrics.json"
    published_v1 = (
        json.loads(published_v1_path.read_text()) if published_v1_path.exists() else None
    )

    delta_160plus = None
    b160 = next(
        (r for r in baseline_metrics["reliability_by_sbp_range"] if r["range"] == "160+"), None
    )
    v160 = next((r for r in v2_metrics["reliability_by_sbp_range"] if r["range"] == "160+"), None)
    if b160 and v160:
        delta_160plus = {
            "baseline_mean_residual": b160["mean_residual"],
            "v2_mean_residual": v160["mean_residual"],
            "baseline_mae": b160["mae"],
            "v2_mae": v160["mae"],
        }

    results = {
        "same_subsample_comparison": {
            "baseline_v1_features_adult_subsample": baseline_metrics,
            "richer_v2_features": v2_metrics,
            "delta_160plus_bucket": delta_160plus,
        },
        "published_v1_for_reference_only": published_v1,
        "note": (
            "Only compare baseline_v1_features_adult_subsample against "
            "richer_v2_features directly - both use the identical age>=18, "
            "complete-case population and the identical train/test split. "
            "published_v1_for_reference_only used a different (age>=8, "
            "full complete-case) population and is not a valid ablation "
            "baseline for this experiment; see the module docstring."
        ),
    }

    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(v2_pipeline, models_dir / "rf_sbp_pipeline_v2.joblib")
    (models_dir / "metrics_v2.json").write_text(json.dumps(results, indent=2))

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=RAW_DATA_DIR)
    parser.add_argument("--models-dir", type=Path, default=MODELS_DIR)
    args = parser.parse_args()

    result = main(args.raw_dir, args.models_dir)
    print(json.dumps(result, indent=2))
