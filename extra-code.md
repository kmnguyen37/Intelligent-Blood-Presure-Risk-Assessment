## Visualizing the bias-variance tradeoff for Decision Tree Regressor (with testing set)

plt.figure(figsize=(6, 4))

depths = range(1, 11)
train_r2_scores = []
test_r2_scores = []

for depth in depths:
    dt_model = DecisionTreeRegressor(
        random_state=42,
        max_depth=depth
    )
    dt_model.fit(X_train, y_train)

    y_train_pred = dt_model.predict(X_train)
    train_r2_scores.append(r2_score(y_train, y_train_pred))

    y_test_pred = dt_model.predict(X_test)
    test_r2_scores.append(r2_score(y_test, y_test_pred))

plt.plot(depths, train_r2_scores, marker='o', label='Train')
plt.plot(depths, test_r2_scores, marker='s', label='Test')
plt.xlabel('Max Depth')
plt.ylabel('R-squared')
plt.title('Bias-Variance Tradeoff: Decision Tree Regressor')
plt.axvline(
    x=5,
    linestyle="--",
    color="red",
    label="Optimal Depth"
)
plt.legend()
plt.show()


Figure illustrates the effect of tree depth on predictive performance. As model complexity increased from a maximum depth of 1 to 5, both training and testing R² improved, indicating that the tree captured increasingly meaningful nonlinear relationships. Beyond a depth of 5, training performance continued to increase while testing performance steadily declined. This divergence indicates overfitting, where the model increasingly memorized the training data rather than learning generalizable patterns. Consequently, a maximum depth of 5 was selected as the optimal balance between model complexity and predictive performance.


## Random Forest 

### Manually tuning for hyperparameters

#### Evaluate Random Forest Regressor with different hyperparameters using cross-validation (manually)

from sklearn.model_selection import cross_validate
from sklearn.ensemble import RandomForestRegressor

rf_depths = [3, 5, 7, 10, None]
rf_estimators = [25, 50, 100, 200]

rf_tuning_results = []

for depth in rf_depths:
    for n_trees in rf_estimators:

        rf_candidate = RandomForestRegressor(
            n_estimators=n_trees,
            max_depth=depth,
            random_state=42,
            n_jobs=-1
        )

        cv_results = cross_validate(
            rf_candidate,
            X_train,
            y_train,
            cv=cv,
            scoring="r2",
            return_train_score=True
        )

        rf_tuning_results.append({
            "Max Depth": depth,
            "Number of Trees": n_trees,
            "Mean Training R²": cv_results["train_score"].mean(),
            "Mean CV R²": cv_results["test_score"].mean(),
            "CV R² Std Dev": cv_results["test_score"].std()
        })

rf_tuning_df = pd.DataFrame(rf_tuning_results)

rf_tuning_df = rf_tuning_df.sort_values(
    "Mean CV R²",
    ascending=False
)

rf_tuning_df.head(10)

### Effects on number of trees on RF performance (with test set)

plt.figure(figsize=(6, 4))
n_estimators_list = [1, 5, 10, 25, 50, 100, 200]
train_r2_scores = []
test_r2_scores = []

for n_estimators in n_estimators_list:
    rf_model = RandomForestRegressor(
        n_estimators=n_estimators,
        random_state=42,
        max_depth=5
    )
    rf_model.fit(X_train, y_train)

    y_train_pred = rf_model.predict(X_train)
    train_r2_scores.append(r2_score(y_train, y_train_pred))

    y_test_pred = rf_model.predict(X_test)
    test_r2_scores.append(r2_score(y_test, y_test_pred))

plt.plot(n_estimators_list, train_r2_scores, label="Training")
plt.plot(n_estimators_list, test_r2_scores, label="Testing")
plt.xlabel("Number of Estimators")
plt.ylabel("R-squared")
plt.title("Effects of Number of Trees on Random Forest Performance")
plt.axvline(
    x=25,
    color="red",
    linestyle="--",
    label="Optimal n_estimators"
)
plt.legend()
plt.show()

Increasing the number of trees substantially improved predictive performance during the initial stages of model training. Performance gains became progressively smaller after approximately 25–50 trees, indicating diminishing returns. Unlike a single Decision Tree, increasing the number of trees did not produce evidence of overfitting. Instead, the Random Forest converged to a stable level of predictive performance, consistent with the variance-reduction properties of ensemble learning.

## XGBoost
### With test set

plt.figure(figsize=(6, 4))

learning_rates = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5]
train_r2_scores = []
test_r2_scores = []

for lr in learning_rates:
    xgb_model = XGBRegressor(
        n_estimators=25,
        max_depth=5,
        learning_rate=lr,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1
    )
    xgb_model.fit(X_train, y_train)

    xgb_train_pred = xgb_model.predict(X_train)
    train_r2_scores.append(r2_score(y_train, xgb_train_pred))

    xgb_test_pred = xgb_model.predict(X_test)
    test_r2_scores.append(r2_score(y_test, xgb_test_pred))

plt.plot(learning_rates, train_r2_scores, marker='o', label='Train')
plt.plot(learning_rates, test_r2_scores, marker='s', label='Test')
plt.xlabel('Learning Rate')
plt.ylabel('R-squared')
plt.title('Effect of Learning Rate on XGBoost Performance')
plt.axvline(
    x=0.05,
    linestyle="--",
    color="red",
    label="Optimal Learning Rate 1"
)
plt.axvline(
    x=0.1,
    linestyle="--",
    color="green",
    label="Optimal Learning Rate 2"
)
plt.legend()
plt.show()

A lower learning rate of 0.05 required more boosting rounds to reach peak predictive performance. With 50 estimators, the model achieved approximately the same testing $R^2$ as the model using a learning rate of 0.10 and 25 estimators, while maintaining a smaller training–testing performance gap. Therefore, learning_rate=0.05 and n_estimators=50 were selected as the preferred configuration because they provided a better balance between predictive accuracy and generalization.

#### Checking between 2 optimal learning rates (0.05 and 0.1) for XGBoost
n_estimators_list = [1, 5, 10, 25, 50, 100, 200]
train_r2_scores_lr1 = []
test_r2_scores_lr1 = []
train_r2_scores_lr2 = []
test_r2_scores_lr2 = []

for n_estimators in n_estimators_list:
    # Learning rate 0.05
    xgb_model_lr1 = XGBRegressor(
        n_estimators=n_estimators,
        max_depth=5,
        learning_rate=0.05,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1
    )
    xgb_model_lr1.fit(X_train, y_train)

    xgb_train_pred_lr1 = xgb_model_lr1.predict(X_train)
    train_r2_scores_lr1.append(r2_score(y_train, xgb_train_pred_lr1))

    xgb_test_pred_lr1 = xgb_model_lr1.predict(X_test)
    test_r2_scores_lr1.append(r2_score(y_test, xgb_test_pred_lr1))

    # Learning rate 0.1
    xgb_model_lr2 = XGBRegressor(
        n_estimators=n_estimators,
        max_depth=5,
        learning_rate=0.1,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1
    )
    xgb_model_lr2.fit(X_train, y_train)

    xgb_train_pred_lr2 = xgb_model_lr2.predict(X_train)
    train_r2_scores_lr2.append(r2_score(y_train, xgb_train_pred_lr2))

    xgb_test_pred_lr2 = xgb_model_lr2.predict(X_test)
    test_r2_scores_lr2.append(r2_score(y_test, xgb_test_pred_lr2))

plt.figure(figsize=(6, 4))
plt.plot(n_estimators_list, train_r2_scores_lr1, marker='o', label='Train (lr=0.05)')
plt.plot(n_estimators_list, test_r2_scores_lr1, marker='s', label='Test (lr=0.05)')
plt.plot(n_estimators_list, train_r2_scores_lr2, marker='o', linestyle='--', label='Train (lr=0.1)')
plt.plot(n_estimators_list, test_r2_scores_lr2, marker='s', linestyle='--', label='Test (lr=0.1)')
plt.xlabel('Number of Estimators')
plt.ylabel('R-squared')
plt.title('XGBoost Performance Comparison: Learning Rates 0.05 vs 0.1')
plt.legend()
plt.show()




