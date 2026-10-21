# Data Dictionary

**Pharmacy Customer and Sales Intelligence System** - synthetic data for a simulated 12-branch Kenyan pharmacy retailer, 1 Jan - 31 Dec 2025. All records are simulated; product names are real generic names, but prices, costs, customers and sales are not real. Currency is KES. Dates are ISO (`YYYY-MM-DD`); timestamps are `YYYY-MM-DD HH:MM:SS`. Blank cell = NULL.

## 1. Files at a glance

| # | File | What one row is | Rows | Key |
|---|---|---|---:|---|
| 1 | [`stores.csv`](#stores) | One row per simulated pharmacy branch (2 per county, 6 counties) | 12 | store_id |
| 2 | [`products.csv`](#products) | Product catalogue: real generic product names, simulated costs and prices | 150 | product_id |
| 3 | [`customers.csv`](#customers) | Synthetic customer records | 8,000 | customer_id |
| 4 | [`transactions.csv`](#transactions) | One row per sales attempt (header) | 100,000 | transaction_id |
| 5 | [`transaction_items.csv`](#transaction-items) | One row per product line in a transaction | 247,794 | transaction_id + line_id |
| 6 | [`sales_returns.csv`](#sales-returns) | One row per return event (at most one per transaction, always a completed one) | 1,030 | return_id |
| 7 | [`sales_return_items.csv`](#sales-return-items) | One row per product line returned | 1,271 | return_id + line_id |
| 8 | [`promotions.csv`](#promotions) | Simulated promotions, valid for all branches | 60 | promotion_id |
| 9 | [`inventory_movements.csv`](#inventory-movements) | Stock ledger | 270,156 | movement_id |
| 10 | [`suppliers.csv`](#suppliers) | Fictional suppliers | 24 | supplier_id |
| 11 | [`purchase_orders.csv`](#purchase-orders) | One row per purchase order (one supplier, one branch, one order date) | 6,593 | purchase_order_id |
| 12 | [`purchase_order_items.csv`](#purchase-order-items) | One row per product on a purchase order | 20,584 | purchase_order_id + line_id |
| 13 | [`opening_inventory.csv`](#opening-inventory) | Supplementary: stock on hand at the start of the period (the starting point of the ledger) | 1,800 | store_id + product_id |
| 14 | [`price_changes.csv`](#price-changes) | Supplementary: the 30 simulated cost/price increases during 2025 (one per product) | 30 | product_id |
| 15 | [`lost_sales_log.csv`](#lost-sales-log) | Supplementary: demand that could not be filled because stock ran out | 2,002 | transaction_id + product_id |

Public-context placeholders (`data/raw/public/`): `cpi_monthly_TEMPLATE.csv` (empty - fill from KNBS) and `public_holidays_2025_DRAFT_unverified.csv` (unverified - confirm against Kenya Law). Not described below.

## 2. How the files connect

```
stores ──< transactions >── customers (customer_id may be blank)
              │
              ├──< transaction_items >── products ──< price_changes
              │            └── promotion_id ──> promotions
              └──< sales_returns ──< sales_return_items >── products

stores + products ──< inventory_movements   (reference_id -> transaction / return / purchase order)
stores + products ──  opening_inventory     (starting stock, 2024-12-31)
suppliers ──< purchase_orders ──< purchase_order_items >── products
transactions/items ──< lost_sales_log
```
`──<` means one-to-many.

## 3. Column definitions

### stores

One row per simulated pharmacy branch (2 per county, 6 counties).  
**Rows:** 12 | **Key:** store_id

| Column | Type | Description | Blank | Example | Values / range |
|---|---|---|---:|---|---|
| `store_id` | text | Primary key, e.g. ST01. | 0 | ST01 |  |
| `store_name` | text | Fictional branch name. | 0 | SimPharm Westlands |  |
| `county` | text | Kenyan county. | 0 | Nairobi | Kiambu, Kisumu, Mombasa, Nairobi, Nakuru, Uasin Gishu |
| `town` | text | Town or locality within the county. | 0 | Westlands | Eldoret Town, Embakasi, Kisumu Central, Langas, Milimani, Mombasa Island, Naivasha, Nakuru Town, Nyali, Ruaka, Thika, Westlands |
| `opening_date` | date | Simulated opening date; all before 2025-01-01. | 0 | 2016-03-14 | 2015-09-01 to 2021-08-16 |
| `store_status` | text | Active or Inactive in the simulation (all Active). | 0 | Active | Active |

### products

Product catalogue: real generic product names, simulated costs and prices.  
**Rows:** 150 | **Key:** product_id

| Column | Type | Description | Blank | Example | Values / range |
|---|---|---|---:|---|---|
| `product_id` | text | Primary key, e.g. P001. | 0 | P001 |  |
| `product_name` | text | Generic name + strength + form. Real names; provenance still to be documented. | 0 | Paracetamol 500 mg Tablets |  |
| `active_ingredient` | text | Active ingredient. Blank for devices, test kits and strips. | 14 | Paracetamol |  |
| `strength` | text | Strength as labelled. Blank where not applicable. | 18 | 500 mg |  |
| `dosage_form` | text | Tablets, Capsules, Syrup, Cream, Injection, Other, etc. | 0 | Tablets |  |
| `category` | text | One of 13 product categories. | 0 | Pain & Fever | Antibiotics, Antimalarials, Cardiovascular, Dermatology, Diabetes, Eye, Ear & Nose, First Aid & Medical Supplies, Gastrointestinal, Other Anti-infectives, Pain & Fever, Reproductive Health, Respiratory & Allergy, Vitamins & Supplements |
| `unit_of_measure` | text | The sale/stock unit, e.g. 'strip of 10 tablets'. 1 quantity = 1 of this unit; no tablet-level counting. | 0 | pack of 20 tablets |  |
| `unit_cost` | decimal (KES) | Simulated standard cost per unit at START of 2025. Later changes are in price_changes.csv. | 0 | 28.86 | 22.3 to 913.17 |
| `selling_price` | decimal (KES) | Simulated standard price per unit at START of 2025. | 0 | 44.00 | 29 to 1360 |
| `product_status` | text | Active, or Discontinued (stops selling on a date in Q3 2025). | 0 | Active | Active, Discontinued |

### customers

Synthetic customer records. No names, phones, addresses or health data.  
**Rows:** 8,000 | **Key:** customer_id

| Column | Type | Description | Blank | Example | Values / range |
|---|---|---|---:|---|---|
| `customer_id` | text | Primary key, pseudonymous, e.g. CUST00001. Numbered in registration order. | 0 | CUST00001 |  |
| `registration_date` | date | Simulated registration date (2022-2025). Customers registered in 2025 first buy on this date. | 0 | 2022-01-01 | 2022-01-01 to 2025-12-31 |
| `customer_segment` | text | Analytical behaviour group (not demographic or medical). | 0 | Frequent | Basket-builder, Frequent, Occasional, Promo-driven, Regular |
| `customer_status` | text | Active = at least one completed purchase in the last 90 days of 2025; otherwise Inactive. | 0 | Active | Active, Inactive |

### transactions

One row per sales attempt (header). Filter transaction_status = 'Completed' for sales analysis.  
**Rows:** 100,000 | **Key:** transaction_id

| Column | Type | Description | Blank | Example | Values / range |
|---|---|---|---:|---|---|
| `transaction_id` | text | Primary key, e.g. TXN0000001. Numbered in time order. | 0 | TXN0000001 |  |
| `transaction_datetime` | timestamp | Local date-time, 08:00-20:59, within 2025. | 0 | 2025-01-01 08:16:31 | 2025-01-01 to 2025-12-31 |
| `store_id` | text | FK to stores.store_id. | 0 | ST02 |  |
| `customer_id` | text, nullable | FK to customers.customer_id. Blank = unidentified buyer (~20%). | 20,000 | CUST02120 |  |
| `payment_method` | text | M-Pesa, Cash, Card or Insurance. | 0 | Cash | Card, Cash, Insurance, M-Pesa |
| `transaction_status` | text | Completed or Voided. Voided rows keep attempted amounts but must be excluded from sales, profit and stock. | 0 | Completed | Completed, Voided |
| `currency_code` | text | Always KES. | 0 | KES | KES |
| `gross_amount` | decimal (KES) | Sum of line_gross_amount. | 0 | 120.00 | 29 to 7355 |
| `discount_amount` | decimal (KES) | Sum of line discount_amount. | 0 | 0.00 | 0 to 816 |
| `net_amount` | decimal (KES) | gross_amount - discount_amount. Before refunds, which are in sales_returns. | 0 | 120.00 | 28.9 to 7355 |

### transaction_items

One row per product line in a transaction. Composite key (transaction_id, line_id).  
**Rows:** 247,794 | **Key:** transaction_id + line_id

| Column | Type | Description | Blank | Example | Values / range |
|---|---|---|---:|---|---|
| `transaction_id` | text | FK to transactions.transaction_id. | 0 | TXN0000001 |  |
| `line_id` | integer | Line number within the transaction, from 1. | 0 | 1 | 1 to 9 |
| `product_id` | text | FK to products.product_id. | 0 | P122 |  |
| `quantity` | integer | Sale units. For completed sales this is the quantity actually filled. | 0 | 1 | 1 to 8 |
| `unit_price` | decimal (KES) | Price used for this sale (reflects any dated price change). | 0 | 120.00 | 29 to 1360 |
| `discount_amount` | decimal (KES) | Promotion discount on the line; 0 if none. | 0 | 0.00 | 0 to 816 |
| `unit_cost_at_sale` | decimal (KES) | Standard cost in force on the sale date. Use for cost of goods sold. | 0 | 87.71 | 22.3 to 913.17 |
| `line_gross_amount` | decimal (KES) | quantity x unit_price. | 0 | 120.00 | 29 to 5440 |
| `line_net_amount` | decimal (KES) | line_gross_amount - discount_amount. | 0 | 120.00 | 28.9 to 5440 |
| `promotion_id` | text, nullable | EXTRA column: FK to promotions.promotion_id for the promotion applied. Blank if none. | 230,863 | PROMO001 |  |

### sales_returns

One row per return event (at most one per transaction, always a completed one).  
**Rows:** 1,030 | **Key:** return_id

| Column | Type | Description | Blank | Example | Values / range |
|---|---|---|---:|---|---|
| `return_id` | text | Primary key, e.g. RET000001. | 0 | RET000001 |  |
| `original_transaction_id` | text | FK to transactions.transaction_id. | 0 | TXN0000029 |  |
| `return_datetime` | timestamp | 0-14 days after the original sale. | 0 | 2025-01-03 18:12:09 | 2025-01-03 to 2025-12-31 |
| `store_id` | text | FK to stores; branch processing the return (same as the original sale). | 0 | ST11 |  |
| `return_reason` | text | Simulated reason. | 0 | Product near expiry | Customer changed mind, Damaged packaging, Duplicate purchase, Prescription changed, Product near expiry, Wrong product dispensed |
| `refund_amount` | decimal (KES) | Sum of quantity_returned x unit_refund_amount over the return's lines. | 0 | 150.00 | 29 to 1460 |

### sales_return_items

One row per product line returned. Composite key (return_id, line_id).  
**Rows:** 1,271 | **Key:** return_id + line_id

| Column | Type | Description | Blank | Example | Values / range |
|---|---|---|---:|---|---|
| `return_id` | text | FK to sales_returns.return_id. | 0 | RET000001 |  |
| `line_id` | integer | Return line number, from 1. | 0 | 1 | 1 to 2 |
| `product_id` | text | FK to products; matches a product on the original transaction. | 0 | P142 |  |
| `quantity_returned` | integer | Never more than the quantity sold on that original line. | 0 | 1 | 1 to 3 |
| `unit_refund_amount` | decimal (KES) | Refund per unit = original line net amount / quantity, rounded down to the cent. | 0 | 150.00 | 28.9 to 1360 |
| `restockable` | text | TRUE = returned to saleable stock (creates a +ve 'Return' stock movement); FALSE = not restocked, no movement. | 0 | FALSE | FALSE, TRUE |

### promotions

Simulated promotions, valid for all branches. One promotion per line, product-level wins over category-level, then larger discount wins.  
**Rows:** 60 | **Key:** promotion_id

| Column | Type | Description | Blank | Example | Values / range |
|---|---|---|---:|---|---|
| `promotion_id` | text | Primary key, e.g. PROMO001. | 0 | PROMO001 |  |
| `promotion_name` | text | Simulated name. | 0 | Hydrochlorothiazide 25 mg Tablets - 5% off |  |
| `promotion_type` | text | Product-level or Category-level. | 0 | Product-level | Category-level, Product-level |
| `product_id` | text, nullable | Target product (product-level only). | 20 | P045 |  |
| `category` | text, nullable | Target category (category-level only). | 40 | Dermatology | Antibiotics, Antimalarials, Dermatology, Diabetes, Eye, Ear & Nose, First Aid & Medical Supplies, Other Anti-infectives, Pain & Fever, Reproductive Health, Respiratory & Allergy, Vitamins & Supplements |
| `start_date` | date | First day (inclusive). | 0 | 2025-01-07 | 2025-01-07 to 2025-11-13 |
| `end_date` | date | Last day (inclusive). | 0 | 2025-01-20 | 2025-01-16 to 2025-11-19 |
| `discount_type` | text | Percentage or Fixed amount. | 0 | Percentage | Fixed amount, Percentage |
| `discount_value` | decimal | Percent (e.g. 10 = 10%) or KES per unit, depending on discount_type. | 0 | 5.00 | 5 to 20 |

### inventory_movements

Stock ledger. Stock on hand = opening_inventory + sum(quantity_change) per store and product.  
**Rows:** 270,156 | **Key:** movement_id

| Column | Type | Description | Blank | Example | Values / range |
|---|---|---|---:|---|---|
| `movement_id` | text | Primary key, e.g. MOV0000001. Numbered in time order. | 0 | MOV0000001 |  |
| `movement_datetime` | timestamp | When the stock changed (receipts ~06-08h, sales in trading hours, write-offs/adjustments after 21h). | 0 | 2025-01-01 08:16:31 | 2025-01-01 to 2025-12-31 |
| `store_id` | text | FK to stores. | 0 | ST02 |  |
| `product_id` | text | FK to products. | 0 | P122 |  |
| `movement_type` | text | Receipt, Sale, Return, Write-off or Adjustment. | 0 | Sale | Adjustment, Receipt, Return, Sale, Write-off |
| `quantity_change` | integer | Signed change: positive adds stock, negative removes it. | 0 | -1 | -18 to 130 |
| `reference_type` | text | Sale, Return, Purchase order or Adjustment. | 0 | Sale | Adjustment, Purchase order, Return, Sale |
| `reference_id` | text, nullable | Source event: transaction_id, return_id or purchase_order_id. Blank for write-offs and adjustments. | 4,966 | TXN0000001 |  |
| `adjustment_reason` | text, nullable | Reason for write-offs and adjustments only. | 265,190 | Shrinkage (unexplained loss) | Damaged, Expired, Near-expiry removal, Product discontinued, Shrinkage (unexplained loss), Stock count variance, Stock count variance (found stock) |

### suppliers

Fictional suppliers.  
**Rows:** 24 | **Key:** supplier_id

| Column | Type | Description | Blank | Example | Values / range |
|---|---|---|---:|---|---|
| `supplier_id` | text | Primary key, e.g. SUP01. | 0 | SUP01 |  |
| `supplier_name` | text | Clearly simulated name ('SIM Supplier ...'). | 0 | SIM Supplier 01 (Pharmaceutical) |  |
| `supplier_type` | text | Supplier category. | 0 | Pharmaceutical wholesaler | Generic manufacturer distributor, Medical supplies distributor, OTC and consumer health distributor, Pharmaceutical wholesaler, Supplements distributor |
| `supplier_status` | text | Active or Inactive at year end. Inactive suppliers stopped receiving orders mid-2025. | 0 | Active | Active, Inactive |

### purchase_orders

One row per purchase order (one supplier, one branch, one order date).  
**Rows:** 6,593 | **Key:** purchase_order_id

| Column | Type | Description | Blank | Example | Values / range |
|---|---|---|---:|---|---|
| `purchase_order_id` | text | Primary key, e.g. PO000001. | 0 | PO000001 |  |
| `supplier_id` | text | FK to suppliers. | 0 | SUP01 |  |
| `store_id` | text | FK to stores; receiving branch. | 0 | ST11 |  |
| `order_date` | date | Date placed. | 0 | 2025-01-01 | 2025-01-01 to 2025-12-31 |
| `expected_delivery_date` | date | Planned arrival (can fall after 2025-12-31). Actual arrival = date of the Receipt movement. | 0 | 2025-01-06 | 2025-01-02 to 2026-01-06 |
| `order_status` | text | Completed (all lines fully received), Partially received (some lines short, shortfall never arrives), Open (delivery after year end) or Cancelled. | 0 | Completed | Cancelled, Completed, Open, Partially received |

### purchase_order_items

One row per product on a purchase order. Composite key (purchase_order_id, line_id).  
**Rows:** 20,584 | **Key:** purchase_order_id + line_id

| Column | Type | Description | Blank | Example | Values / range |
|---|---|---|---:|---|---|
| `purchase_order_id` | text | FK to purchase_orders. | 0 | PO000001 |  |
| `line_id` | integer | Line number within the order, from 1. | 0 | 1 | 1 to 13 |
| `product_id` | text | FK to products. | 0 | P010 |  |
| `quantity_ordered` | integer | Units ordered. | 0 | 10 | 2 to 150 |
| `quantity_received` | integer | Units received; never above quantity_ordered. 0 for Open and Cancelled orders. | 0 | 10 | 0 to 130 |
| `unit_purchase_cost` | decimal (KES) | Simulated cost per unit (standard cost x 0.97-1.03). Outstanding = ordered - received. | 0 | 47.86 | 21.63 to 940.32 |

### opening_inventory

Supplementary: stock on hand at the start of the period (the starting point of the ledger). Key (store_id, product_id).  
**Rows:** 1,800 | **Key:** store_id + product_id

| Column | Type | Description | Blank | Example | Values / range |
|---|---|---|---:|---|---|
| `store_id` | text | FK to stores. | 0 | ST01 |  |
| `product_id` | text | FK to products. | 0 | P001 |  |
| `opening_quantity` | integer | Units in stock at close of 2024-12-31. | 0 | 120 | 2 to 147 |
| `as_of_date` | date | Always 2024-12-31 (the only pre-period reference). | 0 | 2024-12-31 | 2024-12-31 to 2024-12-31 |

### price_changes

Supplementary: the 30 simulated cost/price increases during 2025 (one per product).  
**Rows:** 30 | **Key:** product_id

| Column | Type | Description | Blank | Example | Values / range |
|---|---|---|---:|---|---|
| `product_id` | text | FK to products. | 0 | P088 |  |
| `effective_date` | date | Applies to sales on or after this date. | 0 | 2025-03-11 | 2025-03-11 to 2025-10-10 |
| `new_unit_cost` | decimal (KES) | Replaces products.unit_cost from this date. | 0 | 123.27 | 23.6 to 406.95 |
| `new_selling_price` | decimal (KES) | Replaces products.selling_price from this date. | 0 | 165.00 | 31 to 580 |
| `reason` | text | Simulated supplier cost increase. | 0 | Simulated supplier cost increase | Simulated supplier cost increase |

### lost_sales_log

Supplementary: demand that could not be filled because stock ran out. One row per affected line.  
**Rows:** 2,002 | **Key:** transaction_id + product_id

| Column | Type | Description | Blank | Example | Values / range |
|---|---|---|---:|---|---|
| `transaction_id` | text | FK to transactions. | 0 | TXN0001330 |  |
| `transaction_date` | date | Date of the sale attempt. | 0 | 2025-01-07 | 2025-01-07 to 2025-12-31 |
| `store_id` | text | FK to stores. | 0 | ST07 |  |
| `product_id` | text | FK to products. | 0 | P107 |  |
| `quantity_demanded` | integer | Quantity the customer wanted. | 0 | 1 | 1 to 5 |
| `quantity_fulfilled` | integer | Quantity actually sold (0 if none). | 0 | 0 | 0 to 4 |
| `outcome` | text | Partially filled, Line dropped - no stock, or Transaction voided - no stock. | 0 | Line dropped - no stock | Line dropped - no stock, Partially filled, Transaction voided - no stock |

## 4. Business rules and how to calculate things

| Measure | Definition |
|---|---|
| Sales (net) | `SUM(transactions.net_amount)` where `transaction_status = 'Completed'`. |
| Refunds | `SUM(sales_returns.refund_amount)`, dated by `return_datetime`. |
| Cost of goods sold | `SUM(quantity x unit_cost_at_sale)` over items of completed transactions (reverse it for units returned as restockable). |
| Gross profit | (Net sales - refunds) - COGS. |
| Gross margin % | Gross profit / (net sales - refunds). |
| Stock on hand | `opening_quantity` + `SUM(quantity_change)` up to the date, per store and product. |
| Outstanding PO quantity | `quantity_ordered - quantity_received` (only meaningful for Open orders; short deliveries on 'Partially received' orders never arrive). |
| Customer repeat rate | Customers with 2+ completed transactions / customers with 1+ (ignore blank `customer_id`). |

**Rules to remember**
- Voided transactions: exclude from sales, profit, customer counts and stock. They keep their attempted lines and amounts.
- About 20% of transactions have no customer. Customer analyses cover identified purchases only.
- Quantities are always in the product's `unit_of_measure` (a pack/strip/bottle), never single tablets.
- Header amounts equal the sum of the line amounts exactly; discounts exist only at line level.
- A line's price and cost come from the sale itself, not from `products`; `products` shows start-of-year values.
- Stock-outs mean zero or low sales is not proof of low demand - check `lost_sales_log` and stock levels.
- Seasonality, regional patterns, return rates and customer behaviour are modelling assumptions (see `data_generation_assumptions.md`).
