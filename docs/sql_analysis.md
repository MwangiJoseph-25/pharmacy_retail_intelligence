# SQL analysis

## Database setup

The operational datasets were loaded into a PostgreSQL database named `Customer_sales_intelligence`, using the `public` schema. The schema contains 15 operational tables.

The table definitions, primary keys and foreign keys are provided in [`sql/01_create_tables.sql`](../sql/01_create_tables.sql). The opening stock table is named `open_inventory` in PostgreSQL. Composite primary keys are used for transaction items, sales return items, purchase order items, opening inventory, price changes and lost-sales records.

## Inventory and transaction reconciliation

The SQL work included:

- Checking the connected database, available tables and inventory movement types.
- Comparing inventory sales movements with transaction item quantities.
- Comparing purchase-order receipts with inventory receipt movements.
- Reviewing opening stock, adjustments, write-offs and restockable returns.
- Checking inventory movement references and reconstructing stock balances.
- Summarising lost sales and comparing partially fulfilled quantities with recorded sales.

## Daily demand dataset

A complete product-branch-day dataset was built for 2025, including dates with no recorded sales. Reusable daily demand views were created with calendar features, historical sales features and a seven-day future demand target. The SQL workflow also prepared a modelling dataset containing historical features and future targets.

## Customer and business analysis

The SQL analysis also covered:

- Customer purchase cohorts.
- RFM segmentation.
- Sales by branch and county.
- Sales by product category and month.
- Product performance.

## SQL files

- [`01_create_tables.sql`](../sql/01_create_tables.sql) — creates the operational database tables and their key relationships.
- [`02_inventory_reconciliation_and_analysis.sql`](../sql/02_inventory_reconciliation_and_analysis.sql) — contains inventory reconciliation, demand dataset preparation and business analysis queries.

The SQL scripts provide the queries used for the work. Key query outputs and supporting screenshots or CSV evidence should be added where required for review.

## Notes

The SQL analysis is based on the simulated operational records. The database table name `open_inventory` should be used when referring to the opening stock table in PostgreSQL.
