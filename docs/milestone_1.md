# Milestone 1: Problem, data and SQL analysis

## 1. Problem identification

This project uses a simulated Kenyan pharmacy retailer with 12 branches across six counties. The business scenario brings together sales, customer, product, purchasing and inventory records. The aim is to understand sales and customer behaviour, compare branch and product performance, examine stock availability, and prepare the data for short-term product demand forecasting.

All operational records are synthetic. The findings describe this simulated business and should not be treated as evidence of actual pharmacy performance in Kenya.

## 2. Data preparation

The operational data covers 1 January to 31 December 2025 and consists of 15 related datasets:

- Stores and products
- Customers
- Transactions and transaction items
- Promotions
- Sales returns and return items
- Inventory movements and opening inventory (`open_inventory` in PostgreSQL)
- Suppliers, purchase orders and purchase order items
- Price changes and lost sales

The scenario contains 12 branches, 150 products, 8,000 synthetic customer records and 100,000 transaction headers. Around 80% of transaction headers are designed to have a customer ID; the remaining records represent unidentified purchases.

The operational CSV files were generated using the project data-generation script with a fixed random seed. The prepared datasets were loaded into Python from pickle files for exploration. For sales analysis, voided transactions were excluded. Transaction items were joined to transaction details, product information and branch information. Transaction dates were converted to datetime values, and cost of goods sold and gross profit before refunds were calculated at line level.

Customer-level analysis was limited to completed transactions with an identified customer ID. Refunds were calculated separately from sales and gross profit before refunds.

Public contextual data was kept separate from the synthetic operational records. This includes Kenya's monthly CPI and the 2025 public holiday calendar.

## 3. Exploratory data analysis

The EDA focused on sales performance, branch and county comparisons, product contribution, promotions and customer purchasing patterns.

### Sales and profitability

| Measure | Amount (KES) |
|---|---:|
| Net sales before refunds | 51,071,364.75 |
| Refunds | 216,716.00 |
| Sales after refunds | 50,854,648.75 |
| Cost of goods sold | 37,736,141.54 |
| Gross profit before refunds | 13,335,223.21 |

Gross profit in this summary is before deducting refunds. It is not return-adjusted gross profit.

### Branch and county performance

Sales and gross profit before refunds were compared across the 12 branches and six counties. Nairobi recorded the highest county-level net sales in the notebook, followed by Mombasa and Kiambu. Branch comparisons also considered units sold and transaction counts.

### Monthly sales

Monthly sales were summarised across 2025. December recorded the highest net sales in the notebook, while February recorded the lowest. Transaction counts and gross profit before refunds were also compared by month.

### Products and promotions

Product-level analysis compared units sold and net sales to identify products contributing most to sales. Selected promotions were compared across periods before, during and after the promotion.

These promotion comparisons are descriptive. They show patterns in the simulated data and do not establish that a promotion caused a change in sales.

### Customer purchasing behaviour

Customer analysis covered repeat purchase frequency, customer sales and gross profit before refunds, RFM measures, and customers who may have lapsed.

A 60-day period without a recorded purchase was used to flag potentially lapsed customers. This is an analytical rule, not confirmation that a customer has stopped buying. Customers whose last purchase was near the end of the dataset had less time to return.

The analysis also showed that customers with the highest transaction frequency were not always those with the highest sales or gross profit.

## 4. SQL database and analysis

The operational datasets were loaded into PostgreSQL in a database named `Customer_sales_intelligence`, using the `public` schema.

The schema contains 15 operational tables. The table definitions, primary keys and foreign keys are provided separately in `sql/01_create_tables.sql`. The opening stock table is named `open_inventory` in the database. Composite primary keys are used for transaction items, sales return items, purchase order items, opening inventory, price changes, and lost-sales records.

The SQL analysis covered:

- Checking the connected database, available tables and inventory movement types.
- Comparing inventory sales movements with transaction item quantities.
- Comparing purchase-order receipts with inventory receipt movements.
- Reviewing opening stock, adjustments, write-offs and restockable returns.
- Checking inventory movement references and reconstructing stock balances.
- Summarising lost sales and comparing partially fulfilled quantities with recorded sales.
- Building a complete product-branch-day dataset for 2025, including dates with no recorded sales.
- Creating reusable daily demand views with calendar features, historical sales features and a seven-day future demand target.
- Preparing a modelling dataset with complete historical features and future targets.
- Analysing customer purchase cohorts, RFM segments and sales by branch, county, category and month.

The SQL work is organised into two separate scripts: one for creating the operational tables and another for inventory reconciliation and analysis.

## 5. Scope reached

This milestone establishes the business problem, prepares and explores the project data, and uses SQL to organise and analyse the relational datasets. It also prepares the product-branch-day dataset for the next forecasting stage.

Model development and evaluation are outside the scope of this milestone document.

## Data limitations

- Operational records are synthetic and do not represent real pharmacy sales or customers.
- Customer-level analysis excludes transactions without an identified customer ID.
- Promotion comparisons are descriptive and do not prove causal impact.
- National CPI is contextual information, not a pharmacy-specific price index.
- Forecasting performance must be evaluated on a chronological holdout period and compared with a baseline before drawing conclusions.
