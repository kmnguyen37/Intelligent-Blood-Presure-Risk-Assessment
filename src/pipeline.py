"""
The single reproducible preprocessing + model artifact (roadmap.md, Track 1.2).

Builds one sklearn Pipeline that goes straight from the raw feature
DataFrame (as produced by src.data.build_ml_dataset) to a predicted
Average SBP, using the same encoding and the same tuned Random Forest
hyperparameters selected in notebook/01-project-notebook-reframed-reliability
.ipynb (GridSearchCV winner: n_estimators=50, max_depth=5 - see M003/M006 in
docs/Decision_log.md). Packaging preprocessing and model together removes an
entire class of train/serve skew: there is no separate "remember to one-hot
encode the same way" step at inference time.
"""
from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.data import (
    CATEGORICAL_FEATURES,
    DIABETES_CATEGORIES,
    NUMERIC_FEATURES,
    NUMERIC_FEATURES_V2_EXTRA,
    SEX_CATEGORIES,
    YES_NO_CATEGORIES,
)

RANDOM_STATE = 42

# Final hyperparameters selected via 5-fold GridSearchCV in the technical
# notebook (mean CV R2 = 0.378, effectively tied with XGBoost while needing
# fewer tuning decisions - see roadmap.md model comparison table).
RF_PARAMS = dict(
    n_estimators=50,
    max_depth=5,
    random_state=RANDOM_STATE,
    n_jobs=-1,
)


def build_pipeline() -> Pipeline:
    """Return an unfitted Pipeline: encode categoricals, pass numerics, RF regress.

    Categories are fixed explicitly (not inferred from data) so that a
    category unseen at fit time never silently shifts the output column
    order, and so a single participant can be encoded at inference time
    the same way a full training batch is.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", "passthrough", NUMERIC_FEATURES),
            (
                "sex",
                OneHotEncoder(categories=[SEX_CATEGORIES], drop="first", handle_unknown="error"),
                ["RIAGENDR_label"],
            ),
            (
                "diabetes",
                OneHotEncoder(
                    categories=[DIABETES_CATEGORIES], drop="first", handle_unknown="error"
                ),
                ["DIQ010_label"],
            ),
        ]
    )

    model = RandomForestRegressor(**RF_PARAMS)

    return Pipeline(steps=[("preprocess", preprocessor), ("model", model)])


def build_pipeline_v2() -> Pipeline:
    """Phase 2 sensitivity pipeline (docs/Decision_log.md, P2-M001-P2-M002).

    Same encoding pattern and the same RF_PARAMS as build_pipeline(), so any
    change in held-out performance is attributable to the added predictors
    (smoking, physical activity, alcohol use, creatinine, HbA1c) rather than
    to different hyperparameters. Hyperparameter re-tuning is deliberately
    deferred until it is known whether the added features help at all.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", "passthrough", NUMERIC_FEATURES + NUMERIC_FEATURES_V2_EXTRA),
            (
                "sex",
                OneHotEncoder(categories=[SEX_CATEGORIES], drop="first", handle_unknown="error"),
                ["RIAGENDR_label"],
            ),
            (
                "diabetes",
                OneHotEncoder(
                    categories=[DIABETES_CATEGORIES], drop="first", handle_unknown="error"
                ),
                ["DIQ010_label"],
            ),
            (
                "smoker",
                OneHotEncoder(categories=[YES_NO_CATEGORIES], drop="first", handle_unknown="error"),
                ["current_smoker_label"],
            ),
            (
                "activity",
                OneHotEncoder(categories=[YES_NO_CATEGORIES], drop="first", handle_unknown="error"),
                ["PAQ650_label"],
            ),
            (
                "alcohol",
                OneHotEncoder(categories=[YES_NO_CATEGORIES], drop="first", handle_unknown="error"),
                ["ALQ111_label"],
            ),
        ]
    )

    model = RandomForestRegressor(**RF_PARAMS)

    return Pipeline(steps=[("preprocess", preprocessor), ("model", model)])
