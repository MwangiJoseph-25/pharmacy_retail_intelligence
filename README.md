# Pharmacy Customer and Sales Intelligence System

## Project overview

This project explores sales, customer behaviour, product performance and inventory operations for a simulated Kenyan pharmacy retailer. The scenario covers 12 fictional branches across six counties, 150 generic medicine and healthcare-supply product names, 8,000 synthetic customer records and 100,000 simulated sales attempts during 1 January–31 December 2025.

The project combines synthetic operational data with selected public contextual data for Kenya. All branch, customer, supplier, price, cost, transaction, promotion, purchasing and inventory records are simulated. The public contextual files are separate and must not be interpreted as actual pharmacy sales or customer data.

**Currency:** Kenyan shillings (KES).  
**Period:** 1 January–31 December 2025.  
**Primary tools:** Python, pandas, NumPy, SQL, Power BI and Jupyter Notebook.

## Business problem and objectives

A multi-branch pharmacy retailer needs a clearer view of sales performance, customer purchasing patterns, product profitability and stock availability. The project is designed to demonstrate how linked retail data can support those decisions and how short-term product demand can be forecast to inform replenishment planning.

The analysis uses the available simulated records. Findings describe the simulated business only and are not evidence about actual pharmacies or customers in Kenya.

## Business questions and success measures

The following questions define the business scope. Each question has measurable outputs so that the analysis can be assessed against a clear purpose.

1. **How are sales and profitability changing over time?**  
   **Measures:** completed net sales, gross profit, gross margin, transaction count, average transaction value and month-on-month sales change.  
   **Success measure:** produce monthly and overall performance summaries, with transaction header totals reconciled to transaction-line totals. Voided transactions are excluded; refunds are reported separately and incorporated in net profitability.

2. **Which branches and counties contribute most to sales and profit?**  
   **Measures:** net sales, gross profit, gross margin, transaction count and average transaction value by branch and county.  
   **Success measure:** compare all branches using consistent definitions and identify the strongest and weakest contributors without relying on revenue alone.

3. **Which products and product categories drive sales and profitability?**  
   **Measures:** units sold, net sales, gross profit, gross margin and each product/category's contribution to total sales and profit.  
   **Success measure:** identify high-contribution and low-contribution products/categories and distinguish sales volume from profitability. Stock availability and lost-sales records are considered when interpreting low sales.

4. **What do identified customers' purchasing patterns tell us about repeat business?**  
   **Measures:** repeat purchase rate, number of completed purchases per customer, average customer spend, recency and customer-segment contribution to sales.  
   **Success measure:** quantify repeat purchasing and compare the defined customer segments using completed transactions. Customer-level measures are restricted to transactions with a recorded customer ID; approximately 20% of simulated transaction records are intentionally unidentified.

5. **How are promotions associated with sales and profitability?**  
   **Measures:** promoted units, promoted net sales, discount value, gross margin on promoted lines and comparison with non-promoted lines or periods.  
   **Success measure:** report the sales and margin patterns associated with promotions and identify promotions with weaker margins. This is descriptive analysis, not proof that a promotion caused an increase in sales, because the simulation does not provide a controlled experiment.

6. **Where do stock availability and inventory movements indicate operational issues?**  
   **Measures:** stock on hand, inventory turnover, stockout events, unfilled or partially filled quantities, write-offs and adjustments.  
   **Success measure:** identify products and branches with stockout or inventory-loss signals and reconcile closing stock to opening inventory plus recorded movements.

7. **How well do purchasing and supplier records support branch replenishment?**  
   **Measures:** quantities ordered and received, supplier fill rate, purchase-order status, delivery lead time where order and receipt dates are available, and outstanding quantities.  
   **Success measure:** compare ordered and received quantities, identify incomplete orders and summarize supplier/branch replenishment patterns using consistent calculations.

8. **Can short-term product demand be forecast accurately enough to support replenishment planning?**  
   **Measures:** forecast MAE, RMSE and WAPE for product-branch demand over the defined forecast horizon.  
   **Success measure:** evaluate on a chronological holdout period and compare the model with a documented simple baseline forecast. The model should improve on the baseline for the selected primary error measure; all metrics and the validation period should be reported. Forecast performance is assessed on simulated data and does not establish real-world performance.

## Data inventory

The project uses two types of data: synthetic operational datasets generated by the project script, and public contextual datasets compiled from official Kenyan sources.

### A. Synthetic operational data

The following 15 CSV datasets are generated by `script/generate_synthetic_data.py`. By default, the script writes them to `data/raw/synthetic/`. Row counts below are documented in the [data dictionary](docs/data_dictionary.md).

| File | Rows | Description | Source / terms |
|---|---:|---|---|
| `stores.csv` | 12 | Fictional pharmacy branches, two in each of six counties | Generated for this project; synthetic |
| `products.csv` | 150 | Generic product names with simulated costs, selling prices and categories | Names are generic medicine/supply labels; prices and attributes are simulated. Product-name provenance still needs a documented reference |
| `customers.csv` | 8,000 | Pseudonymous customer IDs, registration dates, behavioural segments and status | Generated for this project; no real names, phone numbers, addresses or health data |
| `transactions.csv` | 100,000 | Sales attempts, including completed and voided transactions | Generated for this project; synthetic |
| `transaction_items.csv` | 247,794 | Product lines attached to sales transactions | Generated for this project; synthetic |
| `sales_returns.csv` | 1,030 | Return events linked to completed transactions | Generated for this project; synthetic |
| `sales_return_items.csv` | 1,271 | Product lines and quantities associated with returns | Generated for this project; synthetic |
| `promotions.csv` | 60 | Simulated product-level and category-level promotions | Generated for this project; synthetic |
| `inventory_movements.csv` | 270,156 | Stock receipts, sales, returns, write-offs and adjustments | Generated for this project; synthetic |
| `suppliers.csv` | 24 | Fictional suppliers and supplier categories | Generated for this project; synthetic |
| `purchase_orders.csv` | 6,593 | Purchase orders by supplier, branch and date | Generated for this project; synthetic |
| `purchase_order_items.csv` | 20,584 | Products and quantities on purchase orders | Generated for this project; synthetic |
| `opening_inventory.csv` | 1,800 | Opening stock by branch and product at 31 December 2024 | Generated for this project; synthetic |
| `price_changes.csv` | 30 | Simulated product cost and selling-price changes during 2025 | Generated for this project; synthetic |
| `lost_sales_log.csv` | 2,002 | Demand that could not be fully met because of stock availability | Generated for this project; synthetic |

The row counts are expected outputs documented by the generator and data dictionary. Re-run the generator to recreate the CSV files. The synthetic data has no third-party data licence; it is created for this portfolio project. No repository-level licence file is currently provided, so reuse permissions for the project code and compiled datasets are not formally specified.

### B. Public contextual data

| File | Contents | How it was obtained | Terms and attribution |
|---|---|---|---|
| `data/Public_data/cpi_monthly.csv` | Kenya's overall monthly Consumer Price Index and annual inflation rate for January–December 2025 | Values compiled from Kenya National Bureau of Statistics (KNBS) Consumer Price Indices and Inflation Rates publications. See the [KNBS CPI and inflation portal](https://www.knbs.or.ke/cpi-and-inflation-rates/) and its [October 2025 release](https://www.knbs.or.ke/reports/consumer-price-indices-and-inflation-rates-october-2025/) | Attribute KNBS as the source. No explicit open-data licence was identified in the cited publications; check KNBS terms before redistribution |
| `data/Public_data/public_holidays_2025_1.csv` | Kenyan public-holiday dates and notes for 2025 | Compiled from the [Public Holidays Act (Cap. 110)](https://www.interior.go.ke/ova_doc/public-holidays-act-cap-110/) and relevant 2025 Kenya Gazette notices, including [Notice No. 3861](https://new.kenyalaw.org/akn/ke/officialGazette/2025-03-28/62/eng%402025-03-28/source), [Notice No. 7317](https://new.kenyalaw.org/akn/ke/officialGazette/2025-06-04/116/eng%402025-06-04/source) and [Notice No. 15007](https://new.kenyalaw.org/akn/ke/officialGazette/2025-10-16/214/eng%402025-10-16/source) | Attribute the Government of Kenya and Kenya Gazette. These are legal/public notices; retain the source references and verify dates against the official notices |

The public contextual datasets are not generated by the synthetic-data script. They are maintained separately in `data/Public_data/`. The CPI series is national context and should not be interpreted as pharmacy-specific inflation or product-level price data.

### C. Supporting project files

| File | Purpose | Source / terms |
|---|---|---|
| `script/generate_synthetic_data.py` | Reproducible Python script that creates the synthetic operational datasets | Original project code; uses NumPy and pandas |
| `docs/data_dictionary.md` | Dataset descriptions, row counts, column definitions, relationships and calculation rules | Written for this project |
| `docs/data_generation_assumptions.md` | Main synthetic scenario settings, random seed and interpretation limitations | Written for this project |
| `requirements.txt` | Python package versions for the project environment | Package versions are listed; each dependency remains subject to its own licence |
| `docs/validation_report_initial.md` | Validation report written by the synthetic-data generator when it runs | Generated by the project script |

The generator also creates draft/template files under `data/raw/public/`. These are not the compiled public contextual datasets listed above. Treat the generated holiday file as an unverified draft and the CPI file as a blank template; use the separately sourced files in `data/Public_data/` for contextual analysis.

## Data generation and reproducibility

The synthetic operational datasets are generated using a fixed random seed (`SEED = 20250101`) in `script/generate_synthetic_data.py`. Keeping the seed unchanged makes the generated output reproducible, subject to the same compatible package environment.

From the repository root:

```bash
python -m pip install -r requirements.txt
python script/generate_synthetic_data.py
```

The script uses Python, NumPy and pandas. It writes the synthetic CSV files to `data/raw/synthetic/` and creates its validation report under `docs/`. The public contextual files in `data/Public_data/` are sourced separately and are not recreated by this script.

For the full column-level definitions, relationships and business calculation rules, see [docs/data_dictionary.md](docs/data_dictionary.md). The main simulation settings and assumptions are listed in [docs/data_generation_assumptions.md](docs/data_generation_assumptions.md).

## Important data limitations

- The operational records are simulated and should not be presented as actual pharmacy performance.
- Customer IDs are pseudonymous. Around 20% of transaction records have no customer ID, so customer analysis covers identified transactions only.
- Product names are generic medicine and healthcare-supply labels; the generator currently notes that their provenance still needs a documented reference.
- Promotion comparisons are descriptive and do not establish causal impact.
- Public CPI is a national economic indicator, not a measure of pharmacy-specific price changes.
- Forecast results must be evaluated against a baseline using a time-based validation split before any performance claim is made.
