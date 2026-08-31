"""
Input validation for a single Average-SBP prediction request.

Used by both src/predict.py and app.py so the demo UI and any future
programmatic caller reject the same malformed inputs the same way
(roadmap.md, Track 1.2 "Validate the prediction input schema" and
Track 1.4 automated-test checklist).
"""
from __future__ import annotations

from dataclasses import dataclass

from src.data import DIABETES_CATEGORIES, SEX_CATEGORIES

MIN_AGE, MAX_AGE = 8, 80
# NHANES top-codes age at 80. An input of 80 therefore represents the source
# category "80 or older"; accepting larger values would imply unsupported age
# resolution that is absent from the training data.
MIN_BMI, MAX_BMI = 12.5, 80.6  # observed complete-case training range (kg/m^2)


class ValidationError(ValueError):
    """Raised when a prediction request fails input validation."""


@dataclass(frozen=True)
class SBPRequest:
    age_years: float
    bmi: float
    sex: str
    diabetes_status: str


def validate_request(age_years, bmi, sex, diabetes_status) -> SBPRequest:
    """Validate and coerce raw inputs into an SBPRequest, or raise ValidationError."""
    if age_years is None or bmi is None or sex is None or diabetes_status is None:
        raise ValidationError("age_years, bmi, sex, and diabetes_status are all required.")

    try:
        age_years = float(age_years)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"age_years must be numeric, got {age_years!r}.") from exc
    if not (MIN_AGE <= age_years <= MAX_AGE):
        raise ValidationError(
            f"age_years must be between {MIN_AGE} and {MAX_AGE}; got {age_years}. "
            "The training cohort excluded participants younger than 8, and NHANES "
            "top-codes age at 80. Use 80 for the source category '80 or older'."
        )

    try:
        bmi = float(bmi)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"bmi must be numeric, got {bmi!r}.") from exc
    if not (MIN_BMI <= bmi <= MAX_BMI):
        raise ValidationError(
            f"bmi must be between {MIN_BMI} and {MAX_BMI}; got {bmi}."
        )

    if sex not in SEX_CATEGORIES:
        raise ValidationError(f"sex must be one of {SEX_CATEGORIES}; got {sex!r}.")

    if diabetes_status not in DIABETES_CATEGORIES:
        raise ValidationError(
            f"diabetes_status must be one of {DIABETES_CATEGORIES}; got {diabetes_status!r}."
        )

    return SBPRequest(
        age_years=age_years, bmi=bmi, sex=sex, diabetes_status=diabetes_status
    )
