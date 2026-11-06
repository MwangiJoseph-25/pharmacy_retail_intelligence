# Exploratory data analysis (EDA)

## Overview

The exploratory analysis examined sales performance, branch and county contribution, monthly trends, product performance, promotions and identified customer purchasing behaviour. The figures below describe the simulated pharmacy retailer and are not estimates of actual pharmacy performance in Kenya.

## Sales and profitability

The overall sales summary from the analysis was:

| Measure | Amount (KES) |
|---|---:|
| Net sales before refunds | 51,071,364.75 |
| Refunds | 216,716.00 |
| Sales after refunds | 50,854,648.75 |
| Cost of goods sold | 37,736,141.54 |
| Gross profit before refunds | 13,335,223.21 |

Gross profit in this summary is before deducting refunds. It is not return-adjusted gross profit.

## Branch and county performance

Sales and gross profit before refunds were compared across the 12 branches and six counties. Nairobi recorded the highest county-level net sales in the analysis, followed by Mombasa and Kiambu. Branch comparisons also considered units sold and transaction counts.

## Monthly sales

Monthly sales were summarised across 2025. December recorded the highest net sales in the analysis, while February recorded the lowest. Transaction counts and gross profit before refunds were also compared by month.

## Product and promotion analysis

Product-level analysis compared units sold and net sales to identify products contributing most to sales. Selected promotions were compared across periods before, during and after the promotion.

These comparisons are descriptive. They show patterns in the simulated data and do not establish that a promotion caused a change in sales.

## Customer purchasing behaviour

Customer analysis covered repeat purchase frequency, customer sales and gross profit before refunds, RFM measures, and customers who may have lapsed.

A 60-day period without a recorded purchase was used to flag potentially lapsed customers. This is an analytical rule, not confirmation that a customer has stopped buying. Customers whose last purchase was near the end of the dataset had less time to return.

The analysis also showed that customers with the highest transaction frequency were not always those with the highest sales or gross profit.

## Interpretation and limitations

- Customer findings cover completed transactions with an identified customer ID only.
- Refunds were reported separately from gross profit before refunds.
- Promotion comparisons are descriptive and do not demonstrate causal impact.
- The 60-day lapse flag is a working definition and is affected by the dataset end date.
- All findings relate to simulated operational data.

Further statistical testing is documented separately from EDA in [statistical analysis](statistical_analysis.md).
