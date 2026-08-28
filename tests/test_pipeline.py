"""Pipeline-structure tests (roadmap.md, Track 1.4).

These use the synthetic fixture in conftest.py, not the real NHANES
extracts, so they exercise the encoding and prediction *shape*
contract quickly, without requiring data/raw/ to be populated.
"""
import numpy as np
import pandas as pd

from src.data import CATEGORICAL_FEATURES, FEATURE_COLUMNS, NUMERIC_FEATURES
from src.pipeline import build_pipeline


def test_feature_columns_match_expected_schema():
    assert FEATURE_COLUMNS == NUMERIC_FEATURES + CATEGORICAL_FEATURES
    assert FEATURE_COLUMNS == ["RIDAGEYR", "BMXBMI", "RIAGENDR_label", "DIQ010_label"]


def test_pipeline_fits_and_predicts(synthetic_training_data):
    X, y = synthetic_training_data
    pipeline = build_pipeline()
    pipeline.fit(X, y)

    predictions = pipeline.predict(X)
    assert predictions.shape == (len(X),)
    assert np.isfinite(predictions).all()


def test_encoded_feature_count_and_order(fitted_pipeline):
    # numeric passthrough (2) + sex one-hot drop-first (1) + diabetes
    # one-hot drop-first (2) = 5 columns feeding the Random Forest.
    preprocessor = fitted_pipeline.named_steps["preprocess"]
    example = pd.DataFrame(
        [{"RIDAGEYR": 40, "BMXBMI": 27.0, "RIAGENDR_label": "Male", "DIQ010_label": "No"}]
    )
    encoded = preprocessor.transform(example)
    assert encoded.shape == (1, 5)


def test_predictions_stable_under_row_order(fitted_pipeline):
    """Feature-column order in the input frame should not change predictions."""
    row = {
        "RIDAGEYR": 55,
        "BMXBMI": 29.4,
        "RIAGENDR_label": "Female",
        "DIQ010_label": "No",
    }
    ordered = pd.DataFrame([row], columns=["RIDAGEYR", "BMXBMI", "RIAGENDR_label", "DIQ010_label"])
    reordered = pd.DataFrame([row], columns=["DIQ010_label", "RIAGENDR_label", "BMXBMI", "RIDAGEYR"])

    pred_a = fitted_pipeline.predict(ordered)[0]
    pred_b = fitted_pipeline.predict(reordered)[0]
    assert pred_a == pred_b
