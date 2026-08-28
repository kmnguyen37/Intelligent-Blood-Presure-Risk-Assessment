"""End-to-end predict.py tests: save -> reload -> predict reproduces results.

(roadmap.md Track 1.4: "Confirm a saved and reloaded pipeline reproduces
expected predictions.")
"""
import joblib
import pytest

from src.predict import ModelNotFoundError, predict_sbp
import src.predict as predict_module
from src.schema import ValidationError


@pytest.fixture
def saved_artifact_path(tmp_path, fitted_pipeline):
    path = tmp_path / "pipeline.joblib"
    joblib.dump(fitted_pipeline, path)
    # predict_sbp caches the loaded pipeline by path; clear between tests
    # so each test starts from a clean cache.
    predict_module._load_pipeline.cache_clear()
    return path


def test_predict_sbp_returns_prediction_with_disclaimer(saved_artifact_path):
    result = predict_sbp(
        age_years=55, bmi=29.4, sex="Female", diabetes_status="No",
        artifact_path=saved_artifact_path,
    )
    assert isinstance(result.predicted_sbp, float)
    assert "not validated for clinical use" in result.disclaimer


def test_reloaded_pipeline_matches_in_memory_pipeline(saved_artifact_path, fitted_pipeline):
    import pandas as pd

    row = pd.DataFrame(
        [{"RIDAGEYR": 55, "BMXBMI": 29.4, "RIAGENDR_label": "Female", "DIQ010_label": "No"}]
    )
    direct = float(fitted_pipeline.predict(row)[0])

    result = predict_sbp(
        age_years=55, bmi=29.4, sex="Female", diabetes_status="No",
        artifact_path=saved_artifact_path,
    )
    assert result.predicted_sbp == round(direct, 1)


def test_high_prediction_sets_warning_flag(saved_artifact_path):
    # A 90-year-old (extrapolated) with high BMI and diabetes should push
    # the synthetic model's prediction into the high range.
    result = predict_sbp(
        age_years=95, bmi=80, sex="Male", diabetes_status="Yes",
        artifact_path=saved_artifact_path,
    )
    if result.predicted_sbp >= 140:
        assert result.high_range_warning is True


def test_missing_artifact_raises_clear_error(tmp_path):
    predict_module._load_pipeline.cache_clear()
    missing_path = tmp_path / "does_not_exist.joblib"
    with pytest.raises(ModelNotFoundError):
        predict_sbp(
            age_years=40, bmi=27, sex="Male", diabetes_status="No",
            artifact_path=missing_path,
        )


def test_invalid_input_never_reaches_model(saved_artifact_path):
    with pytest.raises(ValidationError):
        predict_sbp(
            age_years=200, bmi=27, sex="Male", diabetes_status="No",
            artifact_path=saved_artifact_path,
        )
