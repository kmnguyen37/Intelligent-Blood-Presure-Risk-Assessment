# Reliability Findings and Deployment Roadmap

## Research Finding and Current Readiness Decision

The primary research question asks how reliable machine-learning SBP estimates are across clinically important blood-pressure ranges. The answer is that reliability deteriorates sharply away from the center of the observed distribution, with the most consequential failure at high SBP.

The current Random Forest should not be deployed for clinical use. It systematically underpredicts very high SBP, including an average underprediction of approximately 40.75 mmHg among test participants with observed Average SBP of 160 mmHg or greater. Packaging the model as an application would make the software accessible, but it would not make the model clinically safe or validated.

The project therefore has two distinct deployment tracks:

1. A nonclinical portfolio demonstration that can be completed for October job applications.
2. A longer-term clinical-development pathway requiring a revised use case, stronger data, external validation, governance, and prospective evaluation.

## Track 1: Portfolio-Demo Deployment

### 1. Finalize and communicate the reliability analysis

- [x] Complete SHAP interpretation.
- [x] Add a consolidated limitations and future-work section.
- [x] Make range-specific reliability and severe high-SBP underprediction the organizing findings.
- [x] Preserve the full technical record and create a concise portfolio notebook.
- [x] Restart the kernel and verify the portfolio notebook from top to bottom.

### 2. Create a reproducible training pipeline

- Move preprocessing and model training into reusable Python functions.
- Use a scikit-learn `Pipeline` for preprocessing and prediction.
- Save the complete preprocessing-plus-model artifact.
- Lock dependency versions.
- Validate the prediction input schema.

### 3. Build a demonstration interface

- Create a simple Streamlit application or FastAPI endpoint.
- Accept age, BMI, sex, and diabetes status as inputs.
- Return predicted SBP with clear limitations and appropriate uncertainty information.
- Use synthetic demonstration inputs only.
- Do not describe the result as a diagnosis or clinical recommendation.

Recommended disclaimer:

> This application is an educational technical demonstration. It is not validated for clinical use and must not be used for diagnosis, treatment, or patient-care decisions.

### 4. Add automated tests

- Confirm valid inputs produce predictions.
- Reject invalid ages, BMI values, and categories.
- Handle missing inputs predictably.
- Confirm encoded feature order remains correct.
- Confirm a saved and reloaded pipeline reproduces expected predictions.

### 5. Add professional documentation

- Model card
- Intended use and prohibited uses
- Training population
- Overall and subgroup performance
- Known failure modes
- Reproduction and installation instructions
- Application screenshot or demonstration video

## Track 2: Clinical-Readiness Development

### 1. Reconsider the clinical use case

Directly measuring blood pressure with a cuff is generally more accurate and actionable than estimating SBP from age, BMI, sex, and diabetes status. Before further clinical development, define:

- Who will use the prediction?
- At what point in the workflow will it be used?
- Why is a measured SBP unavailable?
- What action will the prediction trigger?
- What are the harms of overprediction and underprediction?
- Does the model improve care compared with directly measuring BP?

A potentially more defensible future use case may be identifying people who need BP measurement or follow-up when reliable measurements are unavailable.

### 2. Improve the data and model

- Quantify the number of valid SBP readings per participant and test minimum-reading requirements.
- Add relevant clinical, behavioral, medication, and social predictors.
- Consider separate pediatric and adult models or clearly defined populations.
- Validate temporally using another NHANES cycle.
- Validate externally using data from the intended health system.
- Develop confidence or prediction intervals.
- Explicitly address performance among very high-SBP participants.
- Implement missing-data and out-of-range input handling.
- Report uncertainty intervals for performance metrics.
- Assess calibration and subgroup performance.
- Compare performance with a clinically meaningful standard of care.

Any new model development should use a new validation strategy and must not reuse the current held-out test set for tuning.

### 3. Conduct prospective evaluation

1. Retrospective external validation
2. Silent prospective testing without exposing predictions to clinicians
3. Workflow and human-factors evaluation
4. Evaluation of the clinician-plus-model team
5. Controlled implementation with escalation and override procedures
6. Continuous safety and performance monitoring

### 4. Determine regulatory status

Regulatory status depends on intended use and whether clinicians can independently review the basis of patient-specific outputs. A formal regulatory assessment is required before clinical deployment; a disclaimer alone is not sufficient.

### 5. Build production safeguards

- Authentication and authorization
- Encryption in transit and at rest
- Audit logging
- Model and data versioning
- Data- and concept-drift monitoring
- Subgroup performance monitoring
- Operational alert thresholds
- Rollback procedures
- Human override
- Incident-response plans
- Scheduled model revalidation
- HIPAA-aligned administrative, physical, and technical safeguards when protected health information is involved

## Recommended October Positioning

- Deploy a nonclinical demonstration.
- Present the current Random Forest as a model-reliability benchmark whose aggregate score conceals clinically important range-specific failures.
- Make the failure analysis visible rather than hiding it.
- Describe the additional work required for a production clinical system.
- Do not imply clinical readiness, diagnostic capability, or treatment utility.

This positioning demonstrates awareness of the difference between predictive modeling, software deployment, and clinical validation.

## Authoritative References

- [FDA: Good Machine Learning Practice for Medical Device Development](https://www.fda.gov/medical-devices/software-medical-device-samd/good-machine-learning-practice-medical-device-development-guiding-principles)
- [FDA: Clinical Decision Support Software Guidance](https://www.fda.gov/media/162880/download)
- [HHS: HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [NIST: AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
