DECISION_LOG

Purpose

This document records the major design decisions that shaped the project.

It does not record daily progress or coding activities. Git already maintains the history of changes. This document explains why important decisions were made so future collaborators—and future versions of this project—can understand the reasoning behind them.

⸻

BUSINESS DECISIONS

B001 — Project Vision

Decision

Develop an intelligent clinical decision-support system that assists healthcare professionals in assessing blood pressure and hypertension risk using explainable machine learning and AI.

Rationale

The long-term objective is not simply to predict a blood pressure value. The goal is to improve clinical decision making by providing fast, explainable, and evidence-based recommendations while preserving physician oversight.

Impact

Every future version of this project should contribute toward this vision.

⸻

B002 — Intended Users

Decision

Design the system as a physician decision-support tool rather than an autonomous diagnostic system.

Options Considered

* Fully automated diagnosis
* Clinical decision-support

Rationale

Medical decisions require physician judgment. The AI system should support clinicians by providing predictions and explanations, while the physician remains responsible for final clinical decisions.

Impact

Explainability becomes a primary project requirement.

⸻

B003 — Version 1 Scope

Decision

Version 1 will focus exclusively on predicting Average Systolic Blood Pressure.

Rationale

Beginning with a single regression target reduces project complexity while establishing a strong technical and clinical foundation.

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

DS001 — Preserve Raw Data Throughout the Pipeline

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

DS002 — Create Version-Specific Working DataFrames

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

DS003 — Merge Strategy

Status: Approved

Decision

Use Demographics as the base dataset and perform LEFT JOIN operations using SEQN.

Rationale

* Preserve the full participant population.
* Assess missingness before excluding observations.
* Delay cleaning decisions until after data quality assessment.
* Consistent with the project’s “investigate before removing” philosophy.

⸻

DS004 — Validate Merge Integrity

Status: Approved

Decision

Verify that SEQN is unique in every dataframe before merging.

Use: validate="one_to_one" during merges.

Rationale

* Prevent accidental row multiplication.
* Enforce the approved observation unit:
* One row = one participant.

⸻

DS005 — Configuration Separate from Logic

Status: Approved

Decision

Store NHANES dataset metadata in a configuration object (NHANES_DATASETS) separate from the download implementation.

Rationale

Separating configuration from logic makes the pipeline easier to maintain.

Adding new datasets should require modifying only the configuration rather than the download code.

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