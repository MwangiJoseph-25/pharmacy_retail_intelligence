
-- DATABASE AUDIT

-- Confirming which PostgreSQL database we are connected to

select current_database(); 

--Listing all tables in the public schema.
-- This helps us confirm which datasets are available

select table_name
	from information_schema.tables
	where table_schema = 'public' and table_type = 'BASE TABLE'
		order by table_name;

-- INVENTORY MOVEMENT AUDIT
-- Identify the different types of inventory movements
-- recorded in the database and how frequently they occur.
-- This helps us understand how stock enters and leaves each branch.

select * from inventory_movements
limit 10;

select count(movement_type ) 
	from inventory_movements;

select 
    movement_type,
    count(*) as number_of_records,
    sum(quantity_change) as total_quantity_change,
    min(movement_datetime) as first_movement,
    max(movement_datetime) as last_movement
from inventory_movements
group by movement_type
order by number_of_records desc;


-- INVENTORY MOVEMENT REFERENCE AUDIT
-- Examine the reference types associated with inventory movements.
-- This helps in understanding which business records are linked to stock changes
-- and whether we can reconcile movements with sales, receipts and returns.

select movement_type,reference_type,
    COUNT(*) as number_of_records
from inventory_movements
group by
    movement_type,
    reference_type
order by
	movement_type,
    number_of_records desc;

-- SALES AND INVENTORY RECONCILIATION
-- Comparing quantities recorded in inventory movements
-- against quantities recorded in transaction items.
-- This helps establish whether sales-related stock reductions
-- are consistent with the actual sales records.

select
    count(*) as total_sale_movements,
    count(ti.transaction_id) as matched_movements,
    count(*) - count(ti.transaction_id) as unmatched_movements,
    sum(abs(im.quantity_change)) as inventory_units_sold,
    sum(ti.quantity) AS transaction_units_sold
from inventory_movements im
left join transaction_items ti
    on im.reference_id = ti.transaction_id
   and im.product_id = ti.product_id
where im.movement_type = 'Sale';


select * from inventory_movements;
select sum(quantity) as transaction_total_quantity from transaction_items
where ;



select * from transactions;
select * from transaction_items;


-- finding total units sold for all completed transactions
with units_sold_df as(
select 
ti.transaction_id,
t.transaction_id,
t.transaction_status,
sum(ti.quantity) as units_sold
from transaction_items ti
inner join transactions t
	on ti.transaction_id = t.transaction_id
where t.transaction_status = 'Completed'
group by
ti.transaction_id,
t.transaction_id
)
select sum(units_sold) as total_units_sold
	from units_sold_df;


-- PURCHASE RECEIPT RECONCILIATION
-- Compare recorded inventory receipts with purchase-order
-- quantities received, after aggregating each source independently.
-- This helps us identify missing or inconsistent receipt records.
select * from purchase_order_items;
select * from inventory_movements;

with inventory_receipts as (
    select
        reference_id AS purchase_order_id,
        product_id,
        sum(quantity_change) as units_received
    from inventory_movements
    where movement_type = 'Receipt'
    group by  reference_id, product_id
),
purchase_receipts as (
    select
        purchase_order_id,
        product_id,
        sum(quantity_received) as units_received
    from purchase_order_items
    group by purchase_order_id, product_id
)
select
    coalesce(sum(pr.units_received), 0) as purchase_order_units_received,
    coalesce(sum(ir.units_received), 0) as inventory_units_received,
    coalesce(sum(pr.units_received), 0)
      - coalesce(sum(ir.units_received), 0) as quantity_difference
from purchase_receipts pr
full outer join inventory_receipts ir
    on pr.purchase_order_id = ir.purchase_order_id
   and  pr.product_id = ir.product_id;


-- OPENING INVENTORY AUDIT
-- Examine the opening inventory records across branches
-- and products, including the quantities available at the
-- beginning of the inventory tracking period.

select * from open_inventory;
select * from products;

select
    count(*) AS total_opening_records,
    count(distinct store_id) as number_of_stores,
    count(distinct product_id) as number_of_products,
    sum(opening_quantity) as total_opening_quantity,
    min(as_of_date) as earliest_opening_date,
    max(as_of_date) as latest_opening_date
from open_inventory;


-- OPENING STOCK DISTRIBUTION
-- Examine how opening inventory quantities are distributed
-- across branch-product combinations.
-- This identifies products that started with zero stock and helps
-- us understand the initial stock position before 2025 sales began.

select
    case
        when opening_quantity = 0 then 'Zero stock'
        when opening_quantity between  1 and 10 then'1-10 units'
        when opening_quantity between 11 and 50 then '11-50 units'
        when opening_quantity between 51 and 100 then '51-100 units'
        else 'Above 100 units'
    end as stock_category,
    count(*) as product_branch_combinations,
    sum (opening_quantity) as  total_units
from open_inventory
group by
    case
        when opening_quantity = 0 then 'Zero stock'
        when opening_quantity between  1 and 10 then'1-10 units'
        when opening_quantity between 11 and 50 then '11-50 units'
        when opening_quantity between 51 and 100 then '51-100 units'
        else 'Above 100 units'
    end
order by min(opening_quantity);


-- INVENTORY ADJUSTMENT AUDIT
-- Examine the reasons and quantity changes associated
-- with inventory adjustments and write-offs.
-- This helps us understand all stock reductions and additions
-- before reconstructing historical inventory balances.

select * from inventory_movements;
select
    movement_type,
    reference_type,
    quantity_change,
    count(*) as number_of_records
from inventory_movements
where movement_type in ('Adjustment', 'Write-off')
group by
    movement_type,
    reference_type,
    quantity_change
order by
    movement_type,
    quantity_change;


--SALES RETURN AUDIT
-- Examine returned product quantities and determine
-- which returned products are marked as suitable for restocking.
-- This helps us establish which returns should increase
-- the reconstructed available inventory balance.
select * from sales_return_items;

select
    restockable,
    count(*) as return_item_records,
    sum(quantity_returned) as units_returned
from sales_return_items
group by restockable
order by restockable;


--RESTOCKABLE RETURN RECONCILIATION
-- Purpose: Compare inventory return movements with return items
-- marked as restockable.
-- This verifies whether only eligible returned products are
-- being added back into inventory.

select * from sales_return_items;

with restockable_returns as (
    select
        sr.return_id,
        sri.product_id,
        sum(sri.quantity_returned) as units_returned
    from sales_return_items sri
    join sales_returns sr
        on sri.return_id = sr.return_id
    where sri.restockable = TRUE
    group by sr.return_id, sri.product_id
),
inventory_returns as (
    select
        reference_id as return_id,
        product_id,
        sum(quantity_change) as units_restocked
    from inventory_movements
    where movement_type = 'Return'
    group by reference_id, product_id
)
select
    coalesce(sum(rr.units_returned), 0) as restockable_units,
    coalesce(sum(ir.units_restocked), 0) as inventory_units_restocked,
    coalesce(sum(rr.units_returned), 0)
      - coalesce(sum(ir.units_restocked), 0) as quantity_difference
from restockable_returns rr
full outer join inventory_returns ir
    on rr.return_id = ir.return_id
   and rr.product_id = ir.product_id;


-- INVENTORY MOVEMENT RELATIONSHIP VALIDATION
-- Check whether all inventory movements reference
-- valid products and branches in their respective master tables.
-- This helps ensure that stock movements can be assigned to
-- the correct product and pharmacy branch.

select
    count(*) as total_movements,
    count(p.product_id) as valid_product_references,
    count(s.store_id) as valid_store_references
from inventory_movements im
left join products p
    on im.product_id = p.product_id
left join stores s
    on im.store_id = s.store_id;


-- LOST-SALES SUMMARY
-- Purpose: Summarise lost-sales records by outcome.
-- Why: Understand how customer demand, fulfilled quantities,
-- and unmet quantities are represented before using this table
-- to support product demand forecasting.
select * from lost_sales_log;
select
    outcome,
    count(*) as number_of_records,
    sum(quantity_demanded) as total_quantity_demanded,
    sum(quantity_fulfilled) as total_quantity_fulfilled,
    sum(quantity_demanded - quantity_fulfilled) as unfulfilled_quantity
from lost_sales_log
group by outcome
order by number_of_records desc;



-- LOST-SALES AND TRANSACTION STATUS
-- Purpose: Compare lost-sales outcomes with their transaction statuses.
-- Why: Establish whether lost-sales records are associated with
-- completed or voided transactions before reconciling fulfilled units
-- against recorded transaction items.

select
    ls.outcome,
    t.transaction_status,
    count(*) as number_of_records,
    sum(ls.quantity_demanded) as total_quantity_demanded,
    sum(ls.quantity_fulfilled) as total_quantity_fulfilled
from lost_sales_log ls
left join transactions t
    on ls.transaction_id = t.transaction_id
group by
    ls.outcome,
    t.transaction_status
order by
    ls.outcome,
    t.transaction_status;


-- PARTIALLY FULFILLED DEMAND RECONCILIATION
-- Purpose: Compare fulfilled quantities in lost_sales_log with
-- quantities recorded in transaction_items for the same transaction
-- and product.
-- Why: Determine whether fulfilled units are already included in
-- completed sales, preventing double-counting in the demand target.
select * from lost_sales_log;

with recorded_sales as(
    select
        transaction_id,
        product_id,
        sum(quantity) as recorded_units
    from transaction_items
    group by
        transaction_id,
        product_id
),
partial_demand as (
    select
        transaction_id,
        product_id,
        quantity_fulfilled
    from lost_sales_log
    where outcome = 'Partially filled'
)
select
    count(*) as partial_records,
    sum(pd.quantity_fulfilled) as fulfilled_units_in_lost_sales,
    sum(coalesce(rs.recorded_units, 0)) AS corresponding_recorded_sales,
    count(*) filter(
        where pd.quantity_fulfilled = coalesce(rs.recorded_units, 0)
    ) as records_with_matching_quantities,
    count(*) filter(
        where pd.quantity_fulfilled <> coalesce(rs.recorded_units, 0)
    ) as records_with_different_quantities
from partial_demand pd
left join recorded_sales rs
    on pd.transaction_id = rs.transaction_id
   and pd.product_id = rs.product_id;


-- CHRONOLOGICAL INVENTORY BALANCE
-- Reconstruct stock balances after each inventory movement.
-- Identify product-branch combinations where stock becomes
-- negative, which may indicate inventory availability or timing issues.
select 
	movement_type,
	count (*) as total_movement_type
from inventory_movements
group by(movement_type)
order by total_movement_type desc;

select * from inventory_movements;

with stock_movements as(
    select
        im.movement_id,
        im.store_id,
        im.product_id,
        im.movement_datetime,
        im.movement_type,
        im.quantity_change,
        oi.opening_quantity
    from inventory_movements im
    join open_inventory oi
        on im.store_id = oi.store_id
       and im.product_id = oi.product_id
),
running_balances as (
    select
        movement_id,
        store_id,
        product_id,
        movement_datetime,
        movement_type,
        quantity_change,
        opening_quantity,
        opening_quantity
        + SUM(quantity_change) over (
            partition by store_id, product_id
            order by movement_datetime, movement_id
            rows between unbounded preceding and current row
        )as stock_balance
    from stock_movements
    )
select
    count(*) as total_movement_records,
    count(*) filter (
        where stock_balance < 0
    ) as movements_with_negative_stock,
    count(distinct (store_id, product_id)) filter (
        where stock_balance < 0
    ) as product_branch_combinations_with_negative_stock,
    min(stock_balance) as lowest_stock_balance
from running_balances;


-- ZERO-STOCK INVENTORY CHECK
-- Identify inventory movements after which stock reached zero.
-- Why: Determine how frequently products had no remaining recorded
-- stock, which may help identify potential stockout periods.

with stock_movements as (
    select
        im.movement_id,
        im.store_id,
        im.product_id,
        im.movement_datetime,
        im.quantity_change,
        oi.opening_quantity
    from inventory_movements im
    join open_inventory oi
        on im.store_id = oi.store_id
       and im.product_id = oi.product_id
),
running_balances as (
    select
        movement_id,
        store_id,
        product_id,
        movement_datetime,
        opening_quantity
        + sum(quantity_change) over (
            partition by store_id, product_id
            order by movement_datetime, movement_id
            rows between unbounded preceding and current row
        ) as stock_balance
    from stock_movements
)
select
    count(*) filter (
        where stock_balance = 0
    )as movements_ending_at_zero_stock,
    count(distinct (store_id, product_id)) filter (
        where stock_balance = 0
    ) as product_branch_combinations_reaching_zero,
    count(distinct (store_id, product_id, movement_datetime::date))
        filter (
            where stock_balance = 0
        ) as product_branch_days_reaching_zero
from running_balances;


-- COHORT CONTRUCTION


-- PRODUCT-BRANCH-DAILY COHORT
-- Generate every product, branch and calendar-day combination
-- for the 2025 forecasting period.
-- Why: Establish a complete daily dataset, including dates when
-- a product had no recorded sales at a particular branch.

with calendar as (
    select
        generate_series(
            date '2025-01-01',
            date '2025-12-31',
            interval  '1 day'
        )::date as sales_date
)
select
count(*) as total_cohort_rows
from calendar c
cross join stores s
cross join products p;


-- COHORT UNIQUENESS VALIDATION
-- Check whether any product-branch-date combination
-- appears more than once in the generated cohort.
-- Ensures that each row represents one unique forecasting
-- observation and prevent duplication during later joins.

with calendar as (
    select
        generate_series(
            date '2025-01-01',
            date '2025-12-31',
            interval '1 day'
        )::date as sales_date
),
cohort as (
    select
        c.sales_date,
        s.store_id,
        p.product_id
    from calendar c
    cross join stores s
    cross join products p
)
select
    count(*) as total_rows,
    count(distinct (sales_date, store_id, product_id))
        as unique_combinations,
    count(*) - count(distinct (sales_date, store_id, product_id))
        as duplicate_rows
from cohort;


-- DAILY PRODUCT-BRANCH SALES
-- Aggregate completed transaction quantities by product,
-- pharmacy branch and calendar date.
-- Create the historical daily sales measure that will become
-- the starting point for our product demand forecasting dataset.

with total_sales as (
select
    t.transaction_datetime::date as sales_date,
    t.store_id,
    ti.product_id,
    sum(ti.quantity) as units_sold
from transactions t
join transaction_items ti
    on t.transaction_id = ti.transaction_id
where t.transaction_status = 'Completed'
group by
    t.transaction_datetime::date,
    t.store_id,
    ti.product_id
order by
    sales_date,
    store_id,
    product_id)
select count(*)  from total_sales;


-- BUILD COMPLETE DAILY SALES DATASET
-- Attaching aggregated daily sales to every product-branch-date
-- combination in the forecasting cohort.
-- Create a complete time series and represent dates without
-- recorded sales as zero rather than dropping those observations.

with calendar as(
    select
        generate_series(
            date '2025-01-01',
            date '2025-12-31',
            interval '1 day'
        )::date as sales_date
),
cohort as (
    select
        c.sales_date,
        s.store_id,
        p.product_id
    from calendar c
    cross join stores s
    cross join products p
),
daily_sales as(
    select
        t.transaction_datetime::date as sales_date,
        t.store_id,
        ti.product_id,
        sum(ti.quantity) as units_sold
    from transactions t
    join transaction_items ti
        on t.transaction_id = ti.transaction_id
    where t.transaction_status = 'Completed'
    group by
        t.transaction_datetime::date,
        t.store_id,
        ti.product_id
)
select
    c.sales_date,
    c.store_id,
    c.product_id,
    coalesce(ds.units_sold, 0) as units_sold
FROM cohort c
left join daily_sales ds
    on c.sales_date = ds.sales_date
   and c.store_id = ds.store_id
   and c.product_id = ds.product_id;



--DAILY UNFULFILLED DEMAND
-- Aggregating quantities customers requested but could not
-- obtain, by date, branch and product.
-- help Capture unmet demand separately from completed sales,
-- so that i can later investigate its contribution to demand forecasting.
select
    transaction_date as sales_date,
    store_id,
    product_id,
    sum(quantity_demanded - quantity_fulfilled) as unfulfilled_units
from lost_sales_log
group by
    transaction_date,
    store_id,
    product_id
order by
    sales_date,
    store_id,
    product_id;

--CREATE REUSABLE DAILY DEMAND VIEW
-- DAILY SALES AND UNFULFILLED DEMAND DATASET
-- Combining the complete product-branch-day cohort with
-- completed sales and unfulfilled demand.
-- help Create a richer daily dataset that distinguishes fulfilled
-- purchases from recorded unmet customer demand.
create or replace view public.daily_demand_base AS
with calendar as (
    select
        generate_series(
            date '2025-01-01',
            date '2025-12-31',
            interval '1 day'
        )::date as sales_date
),
cohort as (
    select
        c.sales_date,
        s.store_id,
        p.product_id
    from calendar c
    cross join stores s
    cross join products p
),
daily_sales as (
    select
        t.transaction_datetime::date AS sales_date,
        t.store_id,
        ti.product_id,
        sum(ti.quantity) AS units_sold
    from transactions t
    join transaction_items ti
        on t.transaction_id = ti.transaction_id
    where t.transaction_status = 'Completed'
    group by
        t.transaction_datetime::date,
        t.store_id,
        ti.product_id
),
daily_unfulfilled as (
    select
        transaction_date as sales_date,
        store_id,
        product_id,
        sum(quantity_demanded - quantity_fulfilled)
            as unfulfilled_units
    from lost_sales_log
    group by
        transaction_date,
        store_id,
        product_id
)
select
    c.sales_date,
    c.store_id,
    c.product_id,
    coalesce(ds.units_sold, 0) as units_sold,
    coalesce(du.unfulfilled_units, 0) as unfulfilled_units
from cohort c
left join daily_sales ds
    on c.sales_date = ds.sales_date
   and c.store_id = ds.store_id
   and c.product_id = ds.product_id
left join daily_unfulfilled du
    on c.sales_date = du.sales_date
   and c.store_id = du.store_id
   and c.product_id = du.product_id;

-- CALENDAR FEATURES
-- Adding day-of-week, month and weekend indicators
-- to the daily product-branch demand dataset.
-- Sales may vary depending on the day of the week
-- and the time of year.

create or replace view public.daily_demand_features as
select
    sales_date,
    store_id,
    product_id,
    units_sold,
    unfulfilled_units,
extract(ISODOW from sales_date)::integer as day_of_week,
    extract(month from sales_date)::integer as sales_month,
    case
        when extract(ISODOW from sales_date) in (6, 7)
        then 1
        else 0
    end as is_weekend
from public.daily_demand_base;

-- HISTORICAL SALES FEATURES
-- will create lag and rolling-average features using past sales.
-- Historical sales patterns can help predict future product demand.
-- The rolling average excludes the current day to prevent data leakage.

create or replace view public.daily_demand_model AS
select
    sales_date,
    store_id,
    product_id,
    units_sold,
    unfulfilled_units,
    day_of_week,
    sales_month,
    is_weekend,
-- Sales on the previous calendar day
    lag(units_sold, 1) over(partition by store_id, product_id order by sales_date)as sales_previous_day,
-- Sales on the same weekday in the previous week
    lag(units_sold, 7) over(partition by store_id, product_id order by sales_date)as sales_previous_week,
-- Average sales over the previous seven days
    avg(units_sold), over(partition by store_id, product_id order by sales_date 
    rows between 7 preceding and 1 preceding
    ) as avg_sales_previous_7_days
from public.daily_demand_features;

--SEVEN-DAY FUTURE SALES TARGET
-- will calculate total units sold during the seven days
-- following each product-branch-date observation.
-- this creates the outcome the forecasting model
-- will learn to predict.

create or replace view public.pharmacy_forecasting_dataset as
select *,sum(units_sold) over(
        partition by store_id, product_id
        order by sales_date
        rows between 1 following and 7 following
    ) as target_next_7_days
from public.daily_demand_model;

select * from pharmacy_forecasting_dataset;
limit 10;

































