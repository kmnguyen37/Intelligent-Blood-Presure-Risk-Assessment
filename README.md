# Intelligent Blood Pressure Risk Assessment System

Project Vision
Intelligent Blood Pressure Risk Assessment System

Current Implementation (Version 1)
SBP Prediction Engine


This project develops an end-to-end machine learning system that predicts a patient's systolic blood pressure using routinely collected clinical information and provides a clinically meaningful explanation for each prediction.

The system is designed as a clinical decision-support tool to help physicians review patient information more efficiently, allowing them to spend less time on routine data review and more time providing direct patient care.

> **Important:** This system is intended to assist clinicians, not replace clinical judgment. Final medical decisions remain the responsibility of the treating physician.
>

## Business Problem

Hypertension affects millions of people worldwide and is one of the leading risk factors for cardiovascular disease and stroke.

Clinicians often review multiple sources of patient information before assessing blood pressure risk, which can be time-consuming in busy healthcare environments.

This project explores how machine learning can assist clinicians by predicting systolic blood pressure using routinely collected patient information while providing clinically meaningful explanations for every prediction.

## Business Objective

Develop an Intelligent Blood Pressure Risk Assessment System that assists physicians by reducing chart review time and providing clinically interpretable predictions using routinely collected patient information.

The system is intended to support—not replace—physician decision-making, allowing clinicians to spend more time on direct patient care.

## Version 1 Scope

Version 1 is a technical feasibility study, not the final product. Its purpose is to validate whether routinely collected patient information can accurately predict average systolic blood pressure (SBP).

This establishes confidence in the data pipeline, feature selection, and modeling approach before expanding to hypertension risk assessment and broader clinical decision support.

## Why SBP as the Initial Target?

SBP was selected because:

- It is a continuous physiological measurement that provides a strong foundation for future risk-assessment models.
- The required features are routinely collected during standard patient intake, minimizing additional cost and workflow changes.
- Successfully predicting SBP demonstrates that the available clinical information contains sufficient predictive signal before introducing more complex clinical outcomes.

## Dataset

Source:
CDC National Health and Nutrition Examination Survey (NHANES)

Cycle:
2017–March 2020 Pre-Pandemic

Population:
Participants aged 8 years and older after project-specific preprocessing.

Purpose:
Routinely collected clinical measurements used to develop the Version 1 SBP prediction model.

## Project Documentation

This project emphasizes reproducibility and decision traceability through structured documentation.

- Decision Log – Records major project decisions and their rationale.
- Session Log – Summarizes work completed in each development session.
- Data Dictionary – Describes all variables used in the project.
- Reference Guide – Contains NHANES variable definitions and coding references.

## Long-Term Roadmap

- **Version 1:** Predict average SBP using routinely collected clinical data.
- **Version 2:** Expand to hypertension risk stratification, such as Normal, Elevated, Stage 1, and Stage 2.
- **Version 3:** Generate physician-facing clinical summaries and explanations to support decision-making and reduce chart-review time.

### Reviewer Notes

- The project addresses a meaningful clinical workflow problem rather than pursuing machine learning for its own sake.
- Version 1 is appropriately positioned as a validation milestone for the larger system.
- The business and scientific justifications for selecting SBP as the initial target are clearly established.

## Current Status

✅ Business Understanding

✅ Domain Research

✅ Dataset Selection

✅ Dataset Understanding

✅ Data Preparation

✅ Exploratory Data Analysis

✅ Statistical Modeling (OLS)

✅ Model Diagnostics

✅ Machine Learning Modeling

✅ Model Comparison & Evaluation

⬜ Model Interpretability (SHAP)

⬜ Clinical Decision Support Summary

⬜ Version 2: Hypertension Risk Classification

## Project Roadmap

BBusiness Understanding
        │
        ▼
Data Preparation
        │
        ▼
Exploratory Data Analysis
        │
        ▼
Feature Engineering
        │
        ▼
Statistical Modeling (OLS)
        │
        ▼
Model Diagnostics
        │
        ▼
Machine Learning Modeling
        │
        ▼
Model Comparison & Evaluation
        │
        ▼
Model Interpretability
        │
        ▼
Clinical Decision Support
        │
        ▼
AI Assistant Integration

## Project Workflow

NHANES Raw Files
        │
        ▼
Data Validation
        │
        ▼
Data Integration
        │
        ▼
Feature Engineering
        │
        ▼
Training Dataset
        │
        ▼
Exploratory Data Analysis
        │
        ▼
Baseline Model
        │
        ▼
Model Evaluation
        │
        ▼
Clinical Interpretation

Model Development
Version 1 evaluates multiple predictive modeling approaches to establish an interpretable and reproducible baseline for systolic blood pressure (SBP) prediction.
The following models were developed and compared:
Ordinary Least Squares (OLS) for statistical inference and coefficient interpretation.
Linear Regression as the baseline machine learning model.
Decision Tree Regression to capture nonlinear relationships.
Random Forest Regression to improve predictive performance through bagging.
XGBoost Regression to evaluate gradient boosting using sequential residual correction.
Model selection was performed using an 80/20 train-test split and evaluated using:
R²
Mean Absolute Error (MAE)
Root Mean Squared Error (RMSE)
Hyperparameter tuning was performed experimentally by varying one parameter at a time to understand its impact on model performance rather than relying solely on automated optimization.
Model diagnostics for the OLS model included:
Residual vs. Fitted Plot
Normal Q-Q Plot
Variance Inflation Factor (VIF)
Cook's Distance
These diagnostics were used to verify model assumptions, identify influential observations, and assess multicollinearity before developing machine learning models.
Model Summary
Four predictive models were evaluated using the testing dataset.
Model	Purpose
Linear Regression	Baseline machine learning model
Decision Tree	Capture nonlinear relationships
Random Forest	Ensemble learning through bagging
XGBoost	Ensemble learning through boosting


Key findings include:
Ensemble methods consistently outperformed Linear Regression.
Decision Tree improved predictive performance by modeling nonlinear relationships.
Random Forest achieved the highest testing performance.
XGBoost produced nearly identical performance to Random Forest, indicating that additional boosting complexity provided minimal benefit for this prediction task.



## Author
Iris Johnson
An end-to-end healthcare data science project for predicting systolic blood pressure, classifying hypertension risk, and explaining model predictions using NHANES data.

## Key Results

- Developed an end-to-end SBP prediction pipeline using NHANES 2017–2020 data.
- Compared OLS, Linear Regression, Decision Tree, Random Forest, and XGBoost models.
- Performed comprehensive statistical diagnostics, including residual analysis, Q-Q plots, VIF, and Cook's Distance.
- Demonstrated that ensemble methods improved predictive performance over the linear baseline.
- Found that Random Forest and XGBoost achieved nearly identical testing performance, suggesting limited benefit from additional boosting complexity for this dataset.
- Established a reproducible modeling workflow to support future hypertension risk classification and physician-facing clinical decision support.
