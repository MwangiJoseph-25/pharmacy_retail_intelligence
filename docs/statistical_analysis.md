# Statistical Analysis

## 1. Overview

This stage examined the relationship between historical sales patterns and future product demand. The analysis was carried out to understand the data, identify useful patterns and support decisions during predictive modelling.

The analysis used the `prod_demand_forecast_df` dataset, which contains daily sales records for 12 pharmacy branches and 150 products.

## 2. Dataset Summary

The dataset contained:

- **631,800 observations**
- **12 pharmacy branches**
- **150 products**
- **351 sales dates**
- **Date range:** 8 January 2025 to 24 December 2025

The target variable was `target_next_7_days`, representing the total units sold over the following seven days for each product and branch.

## 3. Descriptive Statistics

The target variable had the following summary statistics:

| Statistic | Value |
|---|---:|
| Mean | 3.3265 |
| Median | 2 |
| Standard deviation | 3.5740 |
| Variance | 12.7735 |
| Minimum | 0 |
| Maximum | 50 |
| Skewness | 2.2629 |

The mean was higher than the median, and the positive skewness showed that the distribution was right-skewed. This means that most observations had relatively low demand, while a smaller number had much higher demand.

Zero sales were also common. Approximately 71.71% of current-day `units_sold` observations were zero, compared with 18.09% of the future seven-day demand observations.

This showed that demand was not evenly distributed across products and branches.

## 4. Correlation Analysis

Spearman rank correlation was used to examine the relationship between numerical features and future demand. This method was selected because the sales data was not normally distributed.

The results were:

| Feature | Spearman correlation (ρ) |
|---|---:|
| `avg_sales_previous_7_days` | 0.4520 |
| `units_sold` | 0.2473 |
| `sales_previous_day` | 0.2452 |
| `sales_previous_week` | 0.2409 |
| `sales_month` | 0.0680 |
| `is_weekend` | -0.0010 |
| `day_of_week` | -0.0012 |

The strongest positive relationship was between the previous seven-day average sales and future demand (ρ = 0.4520). This suggested that recent sales activity was useful for understanding upcoming demand.

Current sales, previous-day sales and previous-week sales also had positive relationships with future demand, although these relationships were weaker.

The calendar variables had very weak individual correlations with the target.

## 5. Kruskal–Wallis Tests

The Kruskal–Wallis test was used to check whether future demand differed across groups. It was selected because the target variable did not follow a normal distribution.

### 5.1 Day of the Week

The test examined whether future demand differed across the days of the week.

- H-statistic: 1.8700
- p-value: 0.931260
- Significance level: 0.05

The p-value was greater than 0.05. Therefore, there was not enough evidence to conclude that future demand differed across the days of the week.

### 5.2 Sales Month

The test also examined whether future demand differed across the months of the year.

- H-statistic: 3205.0055
- p-value: less than 0.001
- Significance level: 0.05

The p-value was below 0.05. This provided evidence that future demand was not the same across all months.

The test showed an overall difference between monthly groups. It did not identify which specific months differed from one another.

## 6. Key Findings

The statistical analysis highlighted several findings:

1. Future demand was right-skewed, with many low-demand observations and a smaller number of high-demand observations.
2. The previous seven-day average sales had the strongest positive correlation with future demand among the numerical features examined.
3. There was no statistically significant evidence of differences in demand across days of the week.
4. There was a statistically significant difference in demand across months.
5. Sales history appeared useful for understanding future demand, supporting the use of lag and rolling-average features in the forecasting models.

## 7. Limitations

The analysis was based on simulated pharmacy sales data covering one year. The findings may not represent actual sales patterns in operating pharmacies.

The dataset also contained repeated observations for the same products and branches. In addition, the seven-day target windows overlap across consecutive dates. These factors should be considered when interpreting statistical results because observations may not be fully independent.

The correlation results describe relationships between variables and do not establish cause and effect.

## 8. Conclusion

The analysis showed that recent sales history was an important indicator of future demand. Monthly differences were also observed, while differences across weekdays were not statistically significant.

These findings informed the feature selection and modelling work in the predictive modelling stage.
