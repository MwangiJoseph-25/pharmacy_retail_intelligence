# Predictive Modelling

## 1. Overview

The objective of this stage was to develop a model that could forecast the next seven days of product demand for each pharmacy branch.

The target variable was `target_next_7_days`, which represents the total units sold over the following seven days using information available at the end of the current day.

The modelling process involved preparing the features, comparing different algorithms, tuning model parameters, evaluating the selected model and saving the final pipeline.

## 2. Features Used

Eight features were used in the modelling process:

- `store_id`
- `product_id`
- `units_sold`
- `day_of_week`
- `sales_month`
- `sales_previous_day`
- `sales_previous_week`
- `avg_sales_previous_7_days`

The features included product and branch information, calendar information and historical sales patterns.

The target variable was `target_next_7_days`.

## 3. Data Splitting and Validation

A time-based approach was used to separate the training and test data. This was important because the task involved forecasting future demand using historical records.

The training dataset contained 441,000 observations, covering 8 January to 9 September 2025.

The separate test dataset contained 84,600 observations, covering 8 November to 24 December 2025.

Three expanding-window validation folds were created using dates from the training data. Each fold used earlier dates for training and a later period for validation, with an eight-day gap between the training and validation periods.

The same validation folds were used when comparing and tuning the models. The test dataset was kept separate from model selection and used for the final evaluation.

## 4. Models Compared

The following algorithms were considered:

- Linear Regression
- Random Forest
- XGBoost
- Ridge Regression
- Lasso Regression
- Elastic Net

The linear models and XGBoost were further tuned using `RandomizedSearchCV`. The same date-based validation folds were used for the tuned models.

A preprocessing pipeline was also used. Categorical features were handled using `OneHotEncoder`, while numerical features were scaled using `StandardScaler`.

## 5. Model Tuning Results

The tuned models were compared using their cross-validation mean absolute error (MAE).

| Model | Cross-validation MAE |
|---|---:|
| Tuned XGBoost | 1.7436 |
| Tuned Ridge | 1.7672 |
| Tuned Elastic Net | 1.7943 |
| Tuned Lasso | 1.7987 |

A lower MAE indicates that the model's predictions were closer to the actual demand values on average.

Tuned XGBoost achieved the lowest cross-validation MAE, followed by Ridge Regression.

## 6. Model Selection

Tuned XGBoost was selected as the leading model because it achieved the lowest cross-validation MAE among the four tuned candidates.

Its pooled out-of-fold validation results were also slightly better than those of Tuned Ridge.

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Tuned XGBoost | 1.7436 | 2.4178 | 0.5351 |
| Tuned Ridge | 1.7672 | 2.4640 | 0.5171 |

The difference between the two models was not large, but XGBoost performed better across all three reported metrics.

## 7. Final Test Evaluation

After selecting Tuned XGBoost, the model was evaluated on the separate test dataset containing 84,600 observations.

The final results were:

| Metric | Result |
|---|---:|
| MAE | 1.9020 |
| RMSE | 2.7021 |
| R² | 0.5432 |

The MAE of 1.9020 means that the model's predictions differed from actual demand by approximately 1.90 units on average.

The R² value of 0.5432 indicates that the model explained approximately 54.32% of the variation in the test target values.

The test results were slightly weaker than the pooled validation results for MAE and RMSE. This showed that the model's errors increased on the separate test period.

## 8. Residual Analysis

Residuals were calculated by subtracting predicted demand from actual demand.

The mean residual was approximately 0.5382, indicating a slight tendency to underpredict demand on average.

The residual histogram showed that many errors were concentrated around zero, although some larger errors remained. The model therefore performed reasonably across the test observations but did not predict every demand level equally well.

Higher-demand observations remained more difficult to predict accurately.

## 9. Saving and Verifying the Model

The selected model was saved as a Joblib file.

The saved object contains the complete fitted pipeline, including the preprocessing steps and the tuned XGBoost estimator.

The file was loaded again using `joblib.load()`. Predictions from the reloaded model were compared with the original model's predictions on ten test observations. The predictions matched, confirming that the saved pipeline could be loaded and used.

The model can be used in a future deployment application. New input data must contain the same eight features and follow the expected data formats.

## 10. Limitations

- The data was simulated and may not fully represent real pharmacy sales.
- The dataset covered one year, which limits the amount of historical information available for identifying longer-term patterns.
- The model did not predict all observations equally well, particularly at higher demand levels.
- The final test results may not represent performance in a different year or in an actual pharmacy environment.

## 11. Conclusion

Tuned XGBoost was selected as the leading model after comparison and tuning of four candidate models. It achieved a cross-validation MAE of 1.7436 and a final test MAE of 1.9020.

The model provides a useful starting point for forecasting product demand across pharmacy branches. Its performance and limitations should be considered before using it to support real inventory decisions.
