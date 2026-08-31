"""Input-validation tests (roadmap.md, Track 1.4)."""
import pytest

from src.schema import SBPRequest, ValidationError, validate_request


def test_valid_input_returns_request():
    req = validate_request(age_years=45, bmi=27.5, sex="Female", diabetes_status="No")
    assert isinstance(req, SBPRequest)
    assert req.age_years == 45.0
    assert req.bmi == 27.5
    assert req.sex == "Female"
    assert req.diabetes_status == "No"


def test_coerces_numeric_strings():
    req = validate_request(age_years="45", bmi="27.5", sex="Male", diabetes_status="Yes")
    assert req.age_years == 45.0
    assert req.bmi == 27.5


@pytest.mark.parametrize("age", [-1, 7, 80.1, 101, 500])
def test_rejects_invalid_age(age):
    with pytest.raises(ValidationError):
        validate_request(age_years=age, bmi=27.5, sex="Male", diabetes_status="No")


@pytest.mark.parametrize("bmi", [-5, 0, 12.4, 80.7, 200])
def test_rejects_invalid_bmi(bmi):
    with pytest.raises(ValidationError):
        validate_request(age_years=40, bmi=bmi, sex="Male", diabetes_status="No")


def test_rejects_invalid_sex_category():
    with pytest.raises(ValidationError):
        validate_request(age_years=40, bmi=27.5, sex="Unknown", diabetes_status="No")


def test_rejects_invalid_diabetes_category():
    with pytest.raises(ValidationError):
        validate_request(age_years=40, bmi=27.5, sex="Male", diabetes_status="Sometimes")


def test_rejects_non_numeric_age():
    with pytest.raises(ValidationError):
        validate_request(age_years="not-a-number", bmi=27.5, sex="Male", diabetes_status="No")


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(age_years=None, bmi=27.5, sex="Male", diabetes_status="No"),
        dict(age_years=40, bmi=None, sex="Male", diabetes_status="No"),
        dict(age_years=40, bmi=27.5, sex=None, diabetes_status="No"),
        dict(age_years=40, bmi=27.5, sex="Male", diabetes_status=None),
    ],
)
def test_rejects_missing_fields(kwargs):
    with pytest.raises(ValidationError):
        validate_request(**kwargs)
