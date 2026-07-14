# Intelligent Blood Pressure Risk Assessment System

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

## Long-Term Roadmap

- **Version 1:** Predict average SBP using routinely collected clinical data.
- **Version 2:** Expand to hypertension risk stratification, such as Normal, Elevated, Stage 1, and Stage 2.
- **Version 3:** Generate physician-facing clinical summaries and explanations to support decision-making and reduce chart-review time.

## Design Review Status

**Business Problem:** Approved

### Reviewer Notes

- The project addresses a meaningful clinical workflow problem rather than pursuing machine learning for its own sake.
- Version 1 is appropriately positioned as a validation milestone for the larger system.
- The business and scientific justifications for selecting SBP as the initial target are clearly established.

## Current Status

Current Phase

✅ Business Understanding

✅ Domain Research

✅ Dataset Selection

✅ Dataset Understanding

✅ Feature Approval

⬜ Data Preparation

⬜ Exploratory Data Analysis

⬜ Modeling

⬜ Evaluation

⬜ AI Clinical Assistant

## Project Roadmap

Business -> Domain Research -> Dataset Selection -> Data Preparation -> EDA -> Feature Engineering -> Modeling -> Evaluation -> Interpretability -> AI Assistant

## Project Structure

docs/

README.md

## Project Workflow

NHANES Files
        │
        ▼
Raw Data
(data/raw)
        │
        ▼
Load into pandas
        │
        ▼
Working Dataset
(model_v1_df)
        │
Feature Engineering
Data Cleaning
EDA
Validation
        │
        ▼
Training Dataset
(model_training_df)
        │
        ▼
Machine Learning

## Author
Iris Johnson
An end-to-end healthcare data science project for predicting systolic blood pressure, classifying hypertension risk, and explaining model predictions using NHANES data.
