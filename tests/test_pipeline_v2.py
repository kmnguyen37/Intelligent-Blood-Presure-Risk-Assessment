"""Phase 2 pipeline-structure tests (docs/Decision_log.md, P2-M001).

Mirrors tests/test_pipeline.py's synthetic-fixture approach: exercises the
v2 encoding/prediction shape contract without requiring data/raw/ to hold
the Phase 2 NHANES extracts.
"""
import numpy as np
import pandas as pd

from src.data import FEATURE_COLUMNS_V2, NUMERIC_FEATURES_V2, CATEGORICAL_FEATURES_V2
from src.pipeline import build_pipeline_v2


def test_feature_columns_v2_match_expected_schema():
    assert FEATURE_COLUMNS_V2 == NUMERIC_FEATURES_V2 + CATEGORICAL_FEATURES_V2
    assert FEATURE_COLUMNS_V2 == [
        "RIDAGEYR",
        "BMXBMI",
        "LBXSCR",
        "LBXGH",
        "RIAGENDR_label",
        "DIQ010_label",
        "current_smoker_label",
        "PAQ650_label",
        "ALQ111_label",
    ]


def _synthetic_v2_frame(n: int = 40) -> tuple[pd.DataFrame, pd.Series]:
    diabetes_cycle = ["No", "No", "No", "Borderline", "Yes"]
    yes_no_cycle = ["Yes", "No"]

    rows, targets = [], []
    for i in range(n):
        rows.append(
            {
                "RIDAGEYR": 18 + (i * 3) % 62,
                "BMXBMI": 18.0 + (i % 40) * 1.3,
                "LBXSCR": 0.6 + (i % 10) * 0.1,
                "LBXGH": 4.8 + (i % 15) * 0.2,
                "RIAGENDR_label": "Male" if i % 2 == 0 else "Female",
                "DIQ010_label": diabetes_cycle[i % len(diabetes_cycle)],
                "current_smoker_label": yes_no_cycle[i % 2],
                "PAQ650_label": yes_no_cycle[(i + 1) % 2],
                "ALQ111_label": yes_no_cycle[(i + 1) % 2],
            }
        )
        targets.append(95 + 0.4 * rows[-1]["RIDAGEYR"] + 0.3 * rows[-1]["BMXBMI"])

    X = pd.DataFrame(rows, columns=FEATURE_COLUMNS_V2)
    y = pd.Series(targets, name="Average_SBP")
    return X, y


def test_pipeline_v2_fits_and_predicts():
    X, y = _synthetic_v2_frame()
    pipeline = build_pipeline_v2()
    pipeline.fit(X, y)

    predictions = pipeline.predict(X)
    assert predictions.shape == (len(X),)
    assert np.isfinite(predictions).all()


def test_encoded_feature_count_v2():
    # numeric passthrough (4) + sex (1) + diabetes (2) + smoker (1)
    # + activity (1) + alcohol (1) = 10 columns feeding the Random Forest.
    X, y = _synthetic_v2_frame()
    pipeline = build_pipeline_v2()
    pipeline.fit(X, y)

    preprocessor = pipeline.named_steps["preprocess"]
    encoded = preprocessor.transform(X.iloc[[0]])
    assert encoded.shape == (1, 10)
