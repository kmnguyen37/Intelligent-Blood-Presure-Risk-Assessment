"""Shared pytest fixtures: a tiny synthetic dataset, fast to fit.

Deliberately does NOT depend on the real NHANES .XPT files, so
`pytest` runs in under a second and works even before `python -m
src.train` has ever been executed or data/raw/ has been populated.
Correctness against the real data is checked separately by running
`python -m src.train` and diffing models/metrics.json against the
published README table (see docs/Model_Card.md, "Reproducing").
"""
from __future__ import annotations

import pandas as pd
import pytest

from src.pipeline import build_pipeline


@pytest.fixture
def synthetic_training_data():
    """A small, hand-built stand-in for the real X_train/y_train."""
    n = 60
    diabetes_cycle = ["No", "No", "No", "Borderline", "Yes"]

    ages, bmis, sexes, diabetes, targets = [], [], [], [], []
    for i in range(n):
        age = 8 + (i * 3) % 70
        bmi = 18.0 + (i % 40) * 1.3
        sex = "Male" if i % 2 == 0 else "Female"
        diab = diabetes_cycle[i % len(diabetes_cycle)]
        ages.append(age)
        bmis.append(bmi)
        sexes.append(sex)
        diabetes.append(diab)
        # A simple synthetic-but-plausible target: older/higher-BMI -> higher SBP.
        targets.append(95 + 0.4 * age + 0.3 * bmi + (5 if diab == "Yes" else 0))

    X = pd.DataFrame(
        {
            "RIDAGEYR": ages,
            "BMXBMI": bmis,
            "RIAGENDR_label": sexes,
            "DIQ010_label": diabetes,
        }
    )
    y = pd.Series(targets, name="Average_SBP")
    return X, y


@pytest.fixture
def fitted_pipeline(synthetic_training_data):
    X, y = synthetic_training_data
    pipeline = build_pipeline()
    pipeline.fit(X, y)
    return pipeline
