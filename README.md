# Intelligent Blood Pressure Risk Assessment

An end-to-end data science feasibility study using NHANES 2017–March 2020 data to predict average systolic blood pressure (SBP) from age, sex, BMI, and diabetes status.

> **Bottom line:** the final Random Forest captured meaningful population-level signal, but its errors at clinically important SBP extremes make it unsuitable for clinical use.

## Start here

- **[Portfolio notebook](notebook/02-portfolio-notebook.ipynb):** concise, decision-focused analysis for reviewers
- **[Full technical notebook](notebook/01-project-notebook.ipynb):** expanded EDA, statistical diagnostics, tuning, and error analysis
- **[Deployment roadmap](roadmap.md):** steps required to move beyond the feasibility benchmark

## Problem

Version 1 asks a deliberately narrow question: do a small set of routinely collected predictors contain enough signal to estimate average SBP?

- **Population:** NHANES participants aged 8 years or older with measured SBP
- **Target:** average of up to three oscillometric SBP readings
- **Predictors:** age, sex, BMI, and diabetes status
- **Analytical cohort:** 10,257 participants with complete modeling data
- **Validation:** 80/20 train-test split with five-fold cross-validation performed only within the training set

## Results

| Model | Mean CV R² | CV MAE | CV RMSE |
|---|---:|---:|---:|
| Linear Regression | 0.357 | 11.52 | 15.48 |
| Decision Tree | 0.365 | 11.37 | 15.38 |
| Random Forest | 0.378 | 11.24 | 15.22 |
| XGBoost | 0.378 | 11.24 | 15.22 |

The Random Forest was selected because it was effectively tied with XGBoost while requiring fewer tuning decisions.

**Held-out Random Forest performance:** R² = 0.372, MAE = 11.18 mmHg, RMSE = 15.35 mmHg.

## What the model learned

- Age dominated predictive behavior across SHAP and permutation importance.
- Sex contributed a smaller but consistent signal.
- BMI contributed weak nonlinear information.
- Diabetes status added almost no incremental predictive value after the other features were known.

These findings describe the fitted model; they are not causal conclusions.

## Most important limitation

Aggregate performance hides systematic regression toward the mean. The model overpredicted low SBP and underpredicted high SBP. For participants with observed SBP of 160 mmHg or greater, mean underprediction was approximately 40.75 mmHg. This failure pattern is the main reason the project is presented as a technical benchmark rather than a clinical decision-support system.

Additional limitations include complete-case analysis, omission of relevant clinical and behavioral predictors, failure to incorporate the NHANES complex survey design, age top-coding at 80, and lack of external validation.

## Reproduce the analysis

```bash
python -m venv bp-risk-env
source bp-risk-env/bin/activate
pip install -r requirements.txt
jupyter notebook
```

The notebooks download the required public NHANES files if they are not already available under `data/raw/`.

## Author

Iris Johnson
