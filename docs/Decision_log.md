DECISION_LOG

Purpose

This document records the major design decisions that shaped the project.

It does not record daily progress or coding activities. Git already maintains the history of changes. This document explains why important decisions were made so future collaborators—and future versions of this project—can understand the reasoning behind them.

⸻

BUSINESS DECISIONS

B001 — Project Vision

Decision

Evaluate the reliability and clinical error profile of machine-learning estimates of Average Systolic Blood Pressure, with particular attention to performance across observed blood-pressure ranges.

Rationale

The immediate objective is not simply to produce an SBP estimate. It is to determine whether apparently acceptable aggregate performance conceals clinically important failures, especially systematic underprediction at high SBP. Explainability is used to investigate model behavior, not to imply clinical validity.

Impact

Every future version should report range-specific error, uncertainty, subgroup performance, and explicit evidence for or against clinical readiness.

⸻

B002 — Intended Users

Decision

Treat Version 1 as a nonclinical model-reliability benchmark. Do not position it as a physician decision-support or autonomous diagnostic system.

Options Considered

* Fully automated diagnosis
* Clinical decision-support

Rationale

The observed high-SBP underprediction and large individual errors make clinical use unsafe without a revised use case, stronger data, uncertainty estimates, external and prospective validation, and governance. Human oversight alone does not validate an unreliable estimate.

Impact

Range-specific error analysis is the primary evaluation requirement; explainability supports investigation of the observed failures.

⸻

B003 — Version 1 Scope

Decision

Version 1 evaluates how reliably machine-learning models estimate Average Systolic Blood Pressure across observed blood-pressure ranges.

Rationale

A single regression target permits detailed evaluation of directional bias, error magnitude, subgroup behavior, and extreme failures without changing the existing analytical scope.

Future Direction

Future versions may include:

* Hypertension risk classification
* Diastolic blood pressure prediction
* Additional clinical variables
* Explainable AI assistant
* Clinical dashboard

⸻

DATASET DECISIONS

DS001 — Dataset Selection

Decision

Use NHANES as the primary dataset.

Options Considered

* NHANES
* ICU datasets
* Other publicly available cardiovascular datasets

Rationale

NHANES provides a broad population sample with blood pressure measurements, demographic information, BMI, medication use, and diabetes status. It best matches the project’s objective of building a general clinical prediction model.

Impact

All subsequent project phases are based on NHANES.

⸻

DS002 — Observation Unit

Decision

One row represents one NHANES participant.

Options Considered

* One participant
* One blood pressure measurement
* Multiple rows per participant

Rationale

Patient characteristics belong to an individual rather than to individual blood pressure measurements. A single observation per participant better represents the clinical problem.

Impact

Blood pressure readings will later be summarized into one prediction target.

⸻

DS003 — Target Definition

Decision

Use Average Systolic Blood Pressure as the regression target.

Options Considered

* First reading
* Last reading
* Median
* Average

Rationale

The average provides a better representation of visit-level blood pressure while reducing random measurement variability.

Impact

Version 1 predicts Average Systolic Blood Pressure.

⸻

DS004 — NHANES Component Selection

Decision

Prioritize NHANES components in the following order:

1. Examination
2. Demographics
3. Questionnaire

Rationale

These components provide the highest clinical value while remaining inexpensive to collect and available before prediction.

Laboratory and dietary variables will be evaluated in future versions.

Impact

Version 1 remains simple, practical, and deployable.

⸻

DATA ENGINEER DECISIONS

DE001 — Preserve Raw Data Throughout the Pipeline

Status: Approved

Decision

Raw NHANES datasets and the original pandas dataframes will never be modified directly.

All preprocessing will be performed on independent copies.

Rationale

* Preserves reproducibility.
* Allows future feature expansion without reloading data.
* Prevents accidental loss of information.
* Follows standard ETL and data engineering practices.

⸻

DE002 — Create Version-Specific Working DataFrames

Status: Approved

Decision

Create dedicated Version 1 working dataframes (*_v1_df) while preserving the complete source dataframes.

Rationale

Examples:

demo_df      → complete NHANES demographics

demo_v1_df   → only approved Version 1 variables

Benefits:

* Easier feature expansion.
* Cleaner notebooks.
* Clear separation between source data and modeling data.

⸻

DE003 — Merge Strategy

Status: Approved

Decision

Use Demographics as the base dataset and perform LEFT JOIN operations using SEQN.

Rationale

* Preserve the full participant population.
* Assess missingness before excluding observations.
* Delay cleaning decisions until after data quality assessment.
* Consistent with the project’s “investigate before removing” philosophy.

⸻

DE004 — Validate Merge Integrity

Status: Approved

Decision

Verify that SEQN is unique in every dataframe before merging.

Use: validate="one_to_one" during merges.

Rationale

* Prevent accidental row multiplication.
* Enforce the approved observation unit:
* One row = one participant.

⸻

DE005 — Configuration Separate from Logic

Status: Approved

Decision

Store NHANES dataset metadata in a configuration object (NHANES_DATASETS) separate from the download implementation.

Rationale

Separating configuration from logic makes the pipeline easier to maintain.

Adding new datasets should require modifying only the configuration rather than the download code.

⸻

DE006 — Exclusion of Ages 0–7 from the Training Dataset

Status: Approved

Decision

Participants aged 0–7 years will be excluded from the training dataset because no valid systolic blood pressure target values are available within this age range.

Rationale

* Exploratory Data Analysis showed that participants aged 0–7 have 0% availability for Average_SBP.
* A supervised learning model requires observed target values for training.
* Retaining these participants would introduce rows with universally missing targets without contributing useful information to model development.
* This exclusion is based on data availability, not on clinical assumptions regarding pediatric hypertension.

Scope: This decision applies to the training dataset. The working dataset will continue to retain all participants to preserve the original NHANES data and support future analyses.

Notebook: EDA 4 - Blood Pressure Measurement Availability by Age

⸻

DE007 — Remove Observations with Missing Target Values

Status: Approved

Decision

Remove all observations with missing Average_SBP from the training dataset.

Rationale

* Supervised regression requires a known target value for every training observation.
* Observations without Average_SBP cannot contribute to model learning because the true outcome is unknown.
* These observations will remain in the working dataset for future analyses but will not be included in model training.

⸻

DE008 - Retain the existing training dataset for BP medication analysis.

Rationale: Although the BP medication variable appears to have a high proportion of missing values when considering the full training dataset, this is primarily due to the NHANES survey design, where the question is only asked of participants aged 16 years and older. Furthermore, preprocessing retained participants reporting BP medication use and non-use at nearly identical rates (83.1% vs. 81.7%), and the overall category distributions remained essentially unchanged (27.3% vs. 27.4% for “Yes”; 4.83% vs. 4.77% for “No”). There is no evidence that preprocessing materially altered the distribution of this feature.

⸻

FEATURE ENGINEERING DECISIONS

FE001 — Version 1 Feature Approval Framework

Decision

Every candidate feature must pass five evaluations before being approved.

Evaluation Criteria

1. Business
2. Clinical
3. Data Science
4. Modeling
5. Information Contribution

Rationale

Correlation alone is insufficient for feature selection.

Every approved feature must contribute unique information to the model.

Impact

This framework becomes the permanent feature evaluation methodology for Project 1.

⸻

FE002 — Construction of Average Systolic Blood Pressure

Status: Approved

Decision

Create a new engineered feature named Average_SBP by calculating the arithmetic mean of all available systolic blood pressure measurements collected during the NHANES examination.

Implementation

* 3 valid readings → average all 3
* 2 valid readings → average the 2 available
* 1 valid reading → use the single available reading
* 0 valid readings → Average_SBP remains missing

Rationale

* Blood pressure naturally varies between repeated measurements.
* Averaging multiple readings provides a more stable estimate of systolic blood pressure than relying on a single measurement.
* Participants with one or two valid measurements are retained to maximize the available sample while preserving valid clinical information.
* Participants with no systolic blood pressure measurements cannot be used as supervised learning targets.

⸻

FE003 — Construction of Average Diastolic Blood Pressure

Status: Approved

Decision

Create a new engineered feature named Average_DBP by calculating the arithmetic mean of all available diastolic blood pressure measurements collected during the NHANES examination.

Implementation

* 3 valid readings → average all 3
* 2 valid readings → average the 2 available
* 1 valid reading → use the single available reading
* 0 valid readings → Average_DBP remains missing

Rationale

* Uses the same methodology as Average_SBP to ensure consistency.
* Produces a more stable estimate of diastolic blood pressure than relying on a single reading.
* Preserves participants with partial measurements.
* Supports future expansion of the project, even though Average_DBP is not the primary target in Version 1.

⸻

FE004 - Construction of Average Systolic Blood Pressure

Status: Approved

Decision

The target variable Average_SBP will be calculated as the arithmetic mean of all available systolic blood pressure measurements collected during the NHANES examination.

Implementation

* 3 valid readings → average all 3
* 2 valid readings → average the 2 available
* 1 valid reading → use the single available reading
* 0 valid readings → Average_SBP remains missing

Rationale

* Blood pressure naturally varies between repeated measurements.
* Averaging multiple readings provides a more stable estimate of the participant’s systolic blood pressure than relying on a single measurement.
* Participants with one or two valid measurements are retained to maximize the available training data while preserving valid clinical information.
* Participants without any systolic blood pressure measurements cannot contribute to supervised model training and will be addressed during data quality assessment.

FE004 — Working Dataset vs. Training Dataset

Status: Approved

Decision

Maintain a comprehensive working dataset (model_v1_df) containing both original NHANES variables and engineered features throughout data preparation and exploratory data analysis.

A separate training dataset (model_training_df) will be created only after feature engineering, exploratory data analysis, and data cleaning are complete.

Rationale

* Preserves original measurements for validation and future feature engineering.
* Prevents accidental target leakage during model development.
* Separates exploratory analysis from machine learning preparation.
* Improves reproducibility and supports future feature engineering without modifying the original merged dataset.

⸻

MODELING DECISIONS

M001 — Modeling Philosophy

Decision

Feature selection will prioritize unique information contribution rather than simple statistical correlation.

Rationale

The objective is to build an interpretable model where every feature represents a distinct aspect of the patient’s health.

Impact

Future feature additions must justify their inclusion beyond demonstrating correlation with blood pressure.

⸻

M002 — Explainability Requirement

Decision

Model interpretability is considered a core project objective rather than an optional enhancement.

Rationale

Clinical users must understand why predictions are generated before incorporating them into patient care.

Impact

Future model selection will consider both predictive performance and explainability.

⸻

M003 – Two-Model Modeling Strategy

Decision: Develop two regression models rather than one.

Primary (Baseline) Model

Purpose

- Maximize sample size.
- Provide the primary interpretable model for the study population.

Predictors

- Age
- Sex
- BMI
- Diabetes

Sample Size: 10,257 participants

Role: Primary model used for interpretation and reporting.

Selected Model

Purpose

- Evaluate the additional contribution of BP medication status.
- Assess whether including medication meaningfully improves model performance.

Predictors
- Age
- Sex
- BMI
- Diabetes
- BP Medication

Sample Size: 2,681 participants

Role: Sensitivity analysis / secondary model.

⸻

M004 – Reference Categories

Selected reference groups:
Sex → Male
Diabetes → No diabetes

Reason: These represent the natural baseline for coefficient interpretation.

⸻

M005 – Diabetes Unknown Responses

Removed participants with "Don't Know" diabetes responses before regression modeling.

Reason:
- Extremely small sample size.
- Created singularity issues in the design matrix.
- Did not provide meaningful clinical interpretation.

⸻

M006 – Baseline Model Selection

The Primary (Baseline) Model will be the principal model presented throughout the project.

Reason:

- Largest available sample.
- Most representative of the study population.
- Avoids restricting the analysis because of structurally missing BP medication data.
- Provides the strongest foundation for interpretation and future machine learning models.

⸻

PHASE 2 — RICHER-PREDICTOR SENSITIVITY EXPERIMENT

Context

roadmap.md Track 2 ("Improve the data and model") lists "add relevant
clinical, behavioral, medication, and social predictors" as a candidate next
step toward closing the range-specific reliability gap documented in
README.md. This experiment tests that specific candidate rather than
assuming it would help.

P2-DS001 — Additional NHANES Components and Population Restriction

Status: Approved

Decision

Evaluate five additional NHANES 2017-March 2020 predictors: current smoking
status (P_SMQ), vigorous recreational physical activity (P_PAQ), any lifetime
alcohol use (P_ALQ), serum creatinine (P_BIOPRO), and glycohemoglobin/HbA1c
(P_GHB). Restrict the Phase 2 cohort to participants aged 18 and older.

Rationale

* SMQ020/SMQ040, PAQ650, and ALQ111 are structurally 100% missing for
  participants under 18 in this NHANES cycle (not administered to that age
  group) - confirmed by direct inspection of the raw extracts before writing
  any merge code.
* LBXSCR and LBXGH (blood-draw labs) are missing for 56-58% of ages 8-17
  versus 13-15% of adults - retaining children would have meant imputing or
  discarding most of the pediatric sample regardless.
* This mirrors the M003 precedent (BP-medication sensitivity model on a
  restricted subsample) rather than the primary model's population.

Impact

The Phase 2 complete-case cohort is 7,146 participants (age >= 18), versus
10,257 (age >= 8) for Version 1. Because the population differs, Version 1's
published metrics (models/metrics.json) cannot be directly compared against
a model fit on the Phase 2 cohort - see P2-M001.

⸻

P2-FE001 — Feature Approval: Current Smoking Status

Status: Approved. SMQ020 ("smoked >=100 cigarettes lifetime") and SMQ040
("do you now smoke") are combined into one current_smoker_label (Yes/No)
feature, since SMQ040 is only asked when SMQ020 == 1. Clinical rationale:
smoking is an established cardiovascular/BP risk correlate. Approved under
FE001's five-part framework on clinical plausibility; its actual information
contribution is evaluated empirically, not assumed (see P2-M002).

P2-FE002 — Feature Approval: Vigorous Recreational Physical Activity

Status: Approved. PAQ650 (Yes/No) used as-is. Clinical rationale: physical
activity is an established BP correlate.

P2-FE003 — Feature Approval: Alcohol Use

Status: Approved. ALQ111 ("ever had a drink of any kind of alcohol", Yes/No)
used as-is.

P2-FE004 — Feature Approval: Serum Creatinine

Status: Approved. LBXSCR (mg/dL) used as a continuous kidney-function proxy.
Clinical rationale: renal function is mechanistically linked to blood-
pressure regulation (renin-angiotensin-aldosterone system) more directly
than any Version-1 predictor.

P2-FE005 — Feature Approval: Glycohemoglobin (HbA1c)

Status: Approved. LBXGH (%) used as a continuous glycemic-control measure,
in addition to (not replacing) the existing categorical DIQ010 diabetes
status, since it carries information a No/Borderline/Yes categorical cannot
(degree of control, undiagnosed hyperglycemia).

⸻

P2-M001 — Same-Subsample Ablation Design

Status: Approved

Decision

Do not compare a Phase 2 model against the published Version-1 metrics
directly. Instead fit two models on the identical age >= 18,
complete-case-on-all-Phase-2-features population and the identical
train/test split (random_state=42):

1. baseline_v1_features_adult_subsample - age, BMI, sex, diabetes only
   (the Version-1 feature set, re-fit on the Phase 2 population)
2. richer_v2_features - baseline features + smoking, activity, alcohol,
   creatinine, HbA1c

Rationale

Comparing a richer-feature model fit on adults against the published
Version-1 model fit on ages 8+ would confound two changes at once: added
predictors AND a different, older population. Only the two same-subsample
models isolate the effect of the added predictors. Implemented in
src/train_v2.py; both models use src/pipeline.py's unchanged RF_PARAMS so
that hyperparameters are not a third confounding variable.

⸻

P2-M002 — Result: Added Predictors Do Not Close the Reliability Gap

Status: Recorded, 2026-08-31 (python -m src.train_v2)

Result

| Model | n | Test R² | Test MAE | 160+ mean residual | 160+ MAE |
|---|---:|---:|---:|---:|---:|
| baseline_v1_features_adult_subsample | 7,146 | 0.226 | 12.62 | 41.53 | 41.53 |
| richer_v2_features | 7,146 | 0.228 | 12.61 | 41.14 | 41.14 |

Adding smoking status, physical activity, alcohol use, creatinine, and HbA1c
moved held-out R² by +0.0024, MAE by -0.01 mmHg, and the 160+ mmHg bucket's
mean underprediction by -0.39 mmHg. Permutation importance on the richer
model (n_repeats=15, scoring=r2) ranks the five added features far below
age and even below BMI:

| Feature | Mean R² drop when permuted |
|---|---:|
| RIDAGEYR (age) | 0.4133 |
| RIAGENDR_label (sex) | 0.0559 |
| BMXBMI | 0.0120 |
| LBXSCR (creatinine) | 0.0045 |
| LBXGH (HbA1c) | 0.0015 |
| PAQ650_label (activity) | 0.0002 |
| current_smoker_label | 0.0002 |
| ALQ111_label (alcohol) | -0.0001 |
| DIQ010_label (diabetes) | -0.0003 |

Separately, note that restricting the *same* four Version-1 features to the
adult-only Phase 2 population drops R² from 0.372 (age >= 8) to 0.226
(age >= 18) - most of Version 1's apparent explanatory power comes from age
tracking SBP over childhood/adolescent growth, not from a genuinely strong
age-BMI-sex-diabetes relationship among adults.

Interpretation

This is a negative result and is retained as evidence, not discarded. It
indicates the Version-1 reliability ceiling - and specifically the high-SBP
underprediction reported in README.md - is not primarily an artifact of a
too-narrow feature set. Adding five more clinically plausible predictors,
including two lab values, left the 160+ bucket's ~41 mmHg average
underprediction essentially unchanged. Closing that gap likely requires
predictor types absent from a single cross-sectional NHANES exam entirely
(e.g., longitudinal BP history, direct hemodynamic measurement, genetic or
familial risk) rather than more items from the same kind of data source.

Impact

* Do not present richer demographic/behavioral/lab predictors as a
  promising near-term path to clinical readiness without new evidence.
* roadmap.md Track 2's "improve the data and model" item is updated to
  reflect this tested result rather than an open question.
* README.md's core reliability finding is unaffected and is not
  contradicted by this experiment - if anything it is reinforced by an
  additional, independent line of evidence.
* Artifacts: src/train_v2.py, src/pipeline.build_pipeline_v2(),
  src/data.build_ml_dataset_v2() / build_ml_dataset_v1_features_adult_subsample(),
  models/rf_sbp_pipeline_v2.joblib, models/metrics_v2.json,
  tests/test_pipeline_v2.py. None of these replace or alter the deployed
  Version-1 pipeline (models/rf_sbp_pipeline.joblib) or app.py.

⸻

Engineering Decisions

E001 — Repository Development

Decision

Develop the GitHub repository alongside the project rather than after completion.

Rationale

Documentation, implementation, and decision making should evolve together.

Impact

The repository captures the complete engineering process instead of only the final product.

⸻

E002 — Repository Growth Philosophy

Decision

Every file and folder must justify its existence by solving a real project problem.

Rationale

Avoid unnecessary complexity by introducing project artifacts only when they become useful.

Examples

* docs/ exists because project documentation now exceeds the README.
* data/ will exist when NHANES files are downloaded.
* notebooks/ will exist when exploratory analysis begins.

Impact

The repository grows naturally as the project evolves.

⸻

E003 — Documentation Philosophy

Decision

Separate project documentation from implementation.

Rationale

Documentation communicates project reasoning to humans, while code implements those decisions for the computer.

Impact

Project knowledge will be maintained under the docs/ directory while implementation remains organized in purpose-specific folders.