# Model Card — Random Forest SBP Reliability Benchmark

This card follows the spirit of Mitchell et al. (2019), "Model Cards for
Model Reporting," scoped to what this project actually supports. It should
be read alongside [`README.md`](../README.md) (findings) and
[`roadmap.md`](../roadmap.md) (deployment tracks), not in place of them.

## Model details

- **Model type:** Random Forest Regressor (scikit-learn), 50 trees, max depth 5.
- **Selected via:** 5-fold cross-validated `GridSearchCV` over `n_estimators`
  and `max_depth`, effectively tied with a tuned XGBoost model while
  requiring fewer tuning decisions (see `docs/Decision_log.md`, M003–M006).
- **Artifact:** a single scikit-learn `Pipeline` (`src/pipeline.py`) bundling
  categorical encoding and the regressor, produced by `python -m src.train`
  and saved to `models/rf_sbp_pipeline.joblib`.
- **Author:** Iris Johnson.
- **Version:** 1 (nonclinical portfolio benchmark). See `roadmap.md` Track 2
  for what a clinical-readiness version would require.

## Intended use

- **Intended use:** a transparent, nonclinical benchmark and educational
  demonstration of how model reliability can vary across the outcome range
  even when aggregate metrics look acceptable.
- **Intended users:** people evaluating this project's methodology (e.g.
  hiring managers, other data scientists), or learners exploring model
  reliability and clinical-error-profile analysis.
- **Out of scope / prohibited uses:** diagnosis, treatment, triage, risk
  communication, or any patient-care decision, for any population, in any
  setting. Direct blood-pressure measurement is preferable whenever
  available. This is explicit and non-negotiable — see `README.md`,
  "Deployment recommendation."

## Training data

- **Source:** NHANES 2017–March 2020 pre-pandemic cycle, Demographics, Body
  Measures, Blood Pressure (oscillometric), BP Questionnaire, and Diabetes
  Questionnaire components.
- **Population:** participants aged 8 years or older with at least one valid
  oscillometric SBP reading and complete Age, BMI, Sex, and Diabetes-status
  data (diabetes "Don't Know" responses excluded — see `docs/Decision_log.md`
  M005).
- **Cohort size:** 10,257 participants; 80/20 train/test split
  (`random_state=42`), 5-fold cross-validation within the training split only.
- **Target:** `Average_SBP`, the mean of up to three oscillometric systolic
  readings per participant (`docs/Decision_log.md` FE002/FE004).
- **Predictors (only):** age (years), BMI (kg/m²), sex, diabetes status
  (No / Borderline / Yes). BP-medication status was evaluated in a secondary
  sensitivity model but excluded from the primary model because it is only
  collected for a subset of participants (`docs/Decision_log.md` M003/M006).

## Performance

Regenerate this table with `python -m src.train`, which writes it to
`models/metrics.json`.

**Overall, held-out test set (n = 2,052):**

| Metric | Value |
|---|---:|
| R² | 0.372 |
| MAE | 11.18 mmHg |
| RMSE | 15.35 mmHg |

**By observed SBP range (the primary evidence — see README "Why the model
fails"):**

| Observed SBP range | n | Mean residual (actual − predicted) | MAE | RMSE |
|---|---:|---:|---:|---:|
| <100 | 249 | −13.25 | 13.27 | 16.72 |
| 100–119 | 945 | −6.35 | 9.09 | 11.94 |
| 120–139 | 564 | 3.21 | 7.16 | 9.02 |
| 140–159 | 213 | 17.35 | 17.43 | 19.20 |
| 160+ | 81 | 40.75 | 40.75 | 43.67 |

Negative residual = overprediction; positive residual = underprediction.
**Every** test participant with observed SBP ≥ 160 mmHg was underpredicted,
by 40.75 mmHg on average and up to 89.08 mmHg in the single worst case.

## Known failure modes

- The model regresses toward the center of the training distribution: it
  overpredicts low SBP and, more consequentially, underpredicts high SBP.
- Age dominates model behavior (SHAP mean |value| ≈ 9.70 mmHg; permutation
  importance: removing age drops held-out R² by ≈0.67). Sex contributes a
  smaller, consistent signal. BMI is weak and behaves unstably at sparse
  extremes. Diabetes status adds almost no incremental value once age, BMI,
  and sex are known.
- NHANES top-codes age at 80: participants 80 and older are
  indistinguishable to the model, which caps how well it can resolve SBP for
  the oldest, often highest-risk participants.
- With only four demographic predictors, the model cannot distinguish
  someone whose SBP is unusually high or low for their demographic profile
  from someone whose SBP is typical for it.

## Ethical considerations and limitations

- **Do not deploy for clinical use.** See README "Deployment recommendation"
  and `roadmap.md` Track 2 for what would be required (revised use case,
  richer predictors, uncertainty estimates, external/temporal/prospective
  validation, regulatory assessment, and governance) before any clinical
  application could be considered.
- The severe high-SBP underprediction is the single most safety-relevant
  finding: in a real triage or risk-communication context, this failure mode
  would systematically miss the people most in need of follow-up.
- Performance was evaluated on U.S. NHANES participants; nothing here
  supports generalization to other populations, measurement devices, or time
  periods without new validation.
- No confidence or prediction intervals are produced by this model version;
  a single point estimate should never be read as a bounded range.

## Reproducing

```bash
source bp-risk-env/bin/activate
pip install -r requirements-app.txt   # streamlit, pytest, joblib, etc.
python -m src.train                   # writes models/rf_sbp_pipeline.joblib
                                       # and models/metrics.json
pytest                                # runs tests/
streamlit run app.py                  # launches the demonstration UI
```

`python -m src.train` downloads the NHANES `.XPT` files into `data/raw/` if
they are not already present.
