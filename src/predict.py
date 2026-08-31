"""
Load the saved pipeline artifact and produce a single validated prediction.

    from src.predict import predict_sbp
    predict_sbp(age_years=55, bmi=29.4, sex="Female", diabetes_status="No")

This is the one code path app.py (the Streamlit demo) and any future
programmatic caller should both go through, so validation and the
disclaimer/limitations text can never drift between surfaces.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from functools import lru_cache

import joblib
import pandas as pd

from src.data import PROJECT_ROOT
from src.schema import validate_request

DEFAULT_ARTIFACT_PATH = PROJECT_ROOT / "models" / "rf_sbp_pipeline.joblib"

DISCLAIMER = (
    "This is an educational technical demonstration. It is not validated for "
    "clinical use and must not be used for diagnosis, treatment, or "
    "patient-care decisions. The underlying model systematically "
    "underpredicts high observed SBP (roughly 41 mmHg on average for "
    "participants at or above 160 mmHg in the held-out test set) and should "
    "never be treated as a substitute for a direct blood-pressure measurement."
)

RELIABILITY_WARNING = (
    "The model compresses estimates toward the center of the observed SBP "
    "distribution. An individual prediction cannot identify which observed-SBP "
    "error range a person belongs to and must not be treated as a lower bound, "
    "upper bound, or substitute for direct measurement."
)


class ModelNotFoundError(FileNotFoundError):
    """Raised when the trained pipeline artifact has not been built yet."""


@dataclass(frozen=True)
class SBPPrediction:
    predicted_sbp: float
    disclaimer: str = DISCLAIMER
    reliability_warning: str = RELIABILITY_WARNING


@lru_cache(maxsize=1)
def _load_pipeline(artifact_path: str):
    path = Path(artifact_path)
    if not path.exists():
        raise ModelNotFoundError(
            f"No trained pipeline found at {path}. Run `python -m src.train` first."
        )
    return joblib.load(path)


def predict_sbp(
    age_years,
    bmi,
    sex,
    diabetes_status,
    artifact_path: Path = DEFAULT_ARTIFACT_PATH,
) -> SBPPrediction:
    """Validate inputs, run the pipeline, and return a prediction with context."""
    request = validate_request(age_years, bmi, sex, diabetes_status)
    pipeline = _load_pipeline(str(artifact_path))

    row = pd.DataFrame(
        [
            {
                "RIDAGEYR": request.age_years,
                "BMXBMI": request.bmi,
                "RIAGENDR_label": request.sex,
                "DIQ010_label": request.diabetes_status,
            }
        ]
    )
    predicted = float(pipeline.predict(row)[0])

    return SBPPrediction(
        predicted_sbp=round(predicted, 1),
    )
