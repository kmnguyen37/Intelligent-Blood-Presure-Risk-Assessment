"""
Streamlit demonstration interface (roadmap.md, Track 1.3).

    streamlit run app.py

A synthetic-input-only demo of the reliability-study pipeline. This is
explicitly NOT a clinical tool: see the disclaimer rendered on every page
and docs/Model_Card.md for the full intended-use / prohibited-use statement.
"""
from __future__ import annotations

import streamlit as st

from src.data import DIABETES_CATEGORIES, SEX_CATEGORIES
from src.predict import ModelNotFoundError, predict_sbp
from src.schema import MAX_AGE, MAX_BMI, MIN_AGE, MIN_BMI, ValidationError

st.set_page_config(page_title="SBP Reliability Demo", page_icon="🩺")

st.title("Systolic Blood Pressure — Reliability Demo")

st.warning(
    "**Educational technical demonstration only.** Not validated for "
    "clinical use. Do not use for diagnosis, treatment, triage, risk "
    "communication, or any patient-care decision. Direct blood-pressure "
    "measurement is preferable whenever available.",
    icon="⚠️",
)

st.markdown(
    "This app runs the Random Forest model documented in "
    "[the reliability study](README.md): it predicts *Average Systolic "
    "Blood Pressure* from age, sex, BMI, and diabetes status alone. The "
    "study's own finding is that this model is **not reliable across observed "
    "SBP ranges**, especially at the high end. The observed range is unknown "
    "when making a prediction, so every output receives the same warning."
)

with st.form("prediction_form"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input(
            "Age (years)", min_value=float(MIN_AGE), max_value=float(MAX_AGE),
            value=45.0, step=1.0,
        )
        sex = st.selectbox("Sex", SEX_CATEGORIES)
    with col2:
        bmi = st.number_input(
            "BMI (kg/m²)", min_value=float(MIN_BMI), max_value=float(MAX_BMI),
            value=27.0, step=0.1,
        )
        diabetes_status = st.selectbox("Diabetes status", DIABETES_CATEGORIES)

    submitted = st.form_submit_button("Predict Average SBP")

if submitted:
    try:
        result = predict_sbp(
            age_years=age, bmi=bmi, sex=sex, diabetes_status=diabetes_status
        )
    except ModelNotFoundError:
        st.error(
            "No trained model found. Run `python -m src.train` once to build "
            "`models/rf_sbp_pipeline.joblib`, then reload this app."
        )
    except ValidationError as exc:
        st.error(f"Invalid input: {exc}")
    else:
        st.metric("Predicted Average SBP", f"{result.predicted_sbp} mmHg")
        st.error(result.reliability_warning, icon="🚨")
        st.caption(result.disclaimer)

st.divider()
st.markdown(
    "See [`docs/Model_Card.md`](docs/Model_Card.md) for training population, "
    "performance by SBP range, known failure modes, and intended use; see "
    "[`roadmap.md`](roadmap.md) for what would be required before any "
    "clinical use of this model."
)
