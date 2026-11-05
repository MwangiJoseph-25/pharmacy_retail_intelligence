-- Pharmacy Customer and Sales Intelligence
-- Inventory reconciliation, demand analysis, customer cohorts and business summaries
-- Uses the public schema and the existing operational tables created by 01_create_tables.sql.

-- database audit

select current_database();

select table_name
from information_schema.tables
where table_schema = 'public'
and table_type = 'BASE TABLE'
order by table_name;

-- inventory movement audit

select
    movement_type,
    count(*) as number_of_records,
    sum(quantity_change) as total_quantity_change,
    min(movement_datetime) as first_movement,
    max(movement_datetime) as last_movement
from inventory_movements
group by movement_type
order by number_of_records desc;

select
    movement_type,
    reference_type,
    count(*) as number_of_records
from inventory_movements
group by movement_type, reference_type
order by movement_type, number_of_records desc;

-- sales and inventory reconciliation

with inventory_sales as (
    select
        reference_id as transaction_id,
        product_id,
        sum(abs(quantity_change)) as inventory_units_sold
    from inventory_movements
    where movement_type = 'Sale'
    group by reference_id, product_id
),
recorded_sales as (
    select
        transaction_id,
        product_id,
        sum(quantity) as transaction_units_sold
    from transaction_items
    group by transaction_id, product_id
)
select
    coalesce(sum(rs.transaction_units_sold), 0) as transaction_units_sold,
    coalesce(sum(im.inventory_units_sold), 0) as inventory_units_sold,
    coalesce(sum(rs.transaction_units_sold), 0)
        - coalesce(sum(im.inventory_units_sold), 0) as quantity_difference
from recorded_sales rs
full outer join inventory_sales im
    on rs.transaction_id = im.transaction_id
    and rs.product_id = im.product_id;

-- total units sold in completed transactions

select sum(ti.quantity) as total_units_sold
from transactions t
join transaction_items ti
    on t.transaction_id = ti.transaction_id
where t.transaction_status = 'Completed';

-- purchase receipt reconciliation

with inventory_receipts as (
    select
        reference_id as purchase_order_id,
        product_id,
        sum(quantity_change) as inventory_units_received
    from inventory_movements
    where movement_type = 'Receipt'
    group by reference_id, product_id
),
purchase_receipts as (
    select
        purchase_order_id,
        product_id,
        sum(quantity_received) as purchase_order_units_received
    from purchase_order_items
    group by purchase_order_id, product_id
)
select
    coalesce(sum(pr.purchase_order_units_received), 0) as purchase_order_units_received,
    coalesce(sum(ir.inventory_units_received), 0) as inventory_units_received,
    coalesce(sum(pr.purchase_order_units_received), 0)
        - coalesce(sum(ir.inventory_units_received), 0) as quantity_difference
from purchase_receipts pr
full outer join inventory_receipts ir
    on pr.purchase_order_id = ir.purchase_order_id
    and pr.product_id = ir.product_id;

-- opening inventory audit

select
    count(*) as total_opening_records,
    count(distinct store_id) as number_of_stores,
    count(distinct product_id) as number_of_products,
    sum(opening_quantity) as total_opening_quantity,
    min(as_of_date) as earliest_opening_date,
    max(as_of_date) as latest_opening_date
from open_inventory;

-- opening stock distribution

select
    case
        when opening_quantity = 0 then 'zero stock'
        when opening_quantity between 1 and 10 then '1-10 units'
        when opening_quantity between 11 and 50 then '11-50 units'
        when opening_quantity between 51 and 100 then '51-100 units'
        else 'above 100 units'
    end as stock_category,
    count(*) as product_branch_combinations,
    sum(opening_quantity) as total_units
from open_inventory
group by stock_category
order by min(opening_quantity);

-- inventory adjustments and write-offs

select * from inventory_movements;

select
    movement_type,
    reference_type,
    count(*) as number_of_records,
    sum(quantity_change) as total_quantity_change
from inventory_movements
where movement_type in ('Adjustment', 'Write-off')
group by movement_type, reference_type
order by movement_type, number_of_records desc;

-- sales returns

select
    restockable,
    count(*) as return_item_records,
    sum(quantity_returned) as units_returned
from sales_return_items
group by restockable
order by restockable;

-- restockable return reconciliation

with restockable_returns as (
    select
        sr.return_id,
        sri.product_id,
        sum(sri.quantity_returned) as units_returned
    from sales_return_items sri
    join sales_returns sr
        on sri.return_id = sr.return_id
    where sri.restockable = true
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

-- inventory movement references

select
    count(*) as total_movements,
    count(p.product_id) as valid_product_references,
    count(s.store_id) as valid_store_references
from inventory_movements im
left join products p
    on im.product_id = p.product_id
left join stores s
    on im.store_id = s.store_id;

-- lost sales summary

select
    outcome,
    count(*) as number_of_records,
    sum(quantity_demanded) as total_quantity_demanded,
    sum(quantity_fulfilled) as total_quantity_fulfilled,
    sum(quantity_demanded - quantity_fulfilled) as unfulfilled_quantity
from lost_sales_log
group by outcome
order by number_of_records desc;

-- lost sales and transaction status

select
    ls.outcome,
    t.transaction_status,
    count(*) as number_of_records,
    sum(ls.quantity_demanded) as total_quantity_demanded,
    sum(ls.quantity_fulfilled) as total_quantity_fulfilled
from lost_sales_log ls
left join transactions t
    on ls.transaction_id = t.transaction_id
group by ls.outcome, t.transaction_status
order by ls.outcome, t.transaction_status;

-- compare partially fulfilled demand with recorded sales

with recorded_sales as (
    select
        transaction_id,
        product_id,
        sum(quantity) as recorded_units
    from transaction_items
    group by transaction_id, product_id
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
    sum(coalesce(rs.recorded_units, 0)) as corresponding_recorded_sales,
    count(*) filter (
        where pd.quantity_fulfilled = coalesce(rs.recorded_units, 0)
    ) as matching_records,
    count(*) filter (
        where pd.quantity_fulfilled <> coalesce(rs.recorded_units, 0)
    ) as records_with_different_quantities
from partial_demand pd
left join recorded_sales rs
    on pd.transaction_id = rs.transaction_id
    and pd.product_id = rs.product_id;

-- reconstruct inventory balances

with stock_movements as (
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
        opening_quantity
            + sum(quantity_change) over (
                partition by store_id, product_id
                order by movement_datetime, movement_id
                rows between unbounded preceding and current row
            ) as stock_balance
    from stock_movements
)
select
    count(*) as total_movement_records,
    count(*) filter (where stock_balance < 0) as movements_with_negative_stock,
    count(distinct (store_id, product_id)) filter (
        where stock_balance < 0
    ) as product_branch_combinations_with_negative_stock,
    min(stock_balance) as lowest_stock_balance
from running_balances;

-- check movements that bring stock to zero

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
    ) as movements_ending_at_zero_stock,
    count(distinct (store_id, product_id)) filter (
        where stock_balance = 0
    ) as product_branch_combinations_reaching_zero,
    count(distinct (store_id, product_id, movement_datetime::date)) filter (
        where stock_balance = 0
    ) as product_branch_days_reaching_zero
from running_balances;

-- product branch daily cohort

with calendar as (
    select generate_series(
        date '2025-01-01',
        date '2025-12-31',
        interval '1 day'
    )::date as sales_date
)
select count(*) as total_cohort_rows
from calendar c
cross join stores s
cross join products p;

-- check cohort uniqueness

with calendar as (
    select generate_series(
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
    count(distinct (sales_date, store_id, product_id)) as unique_combinations,
    count(*) - count(distinct (sales_date, store_id, product_id)) as duplicate_rows
from cohort;

-- daily product branch sales

with daily_sales as (
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
select count(*) as daily_sales_records
from daily_sales;

-- daily unfulfilled demand

select
    transaction_date as sales_date,
    store_id,
    product_id,
    sum(quantity_demanded - quantity_fulfilled) as unfulfilled_units
from lost_sales_log
group by transaction_date, store_id, product_id
order by sales_date, store_id, product_id;

-- create daily demand base view

create or replace view public.daily_demand_base as
with calendar as (
    select generate_series(
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
),
daily_unfulfilled as (
    select
        transaction_date as sales_date,
        store_id,
        product_id,
        sum(quantity_demanded - quantity_fulfilled) as unfulfilled_units
    from lost_sales_log
    group by transaction_date, store_id, product_id
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

-- add calendar features

create or replace view public.daily_demand_features as
select
    sales_date,
    store_id,
    product_id,
    units_sold,
    unfulfilled_units,
    extract(isodow from sales_date)::integer as day_of_week,
    extract(month from sales_date)::integer as sales_month,
    case
        when extract(isodow from sales_date) in (6, 7) then 1
        else 0
    end as is_weekend
from public.daily_demand_base;

-- add historical sales features

create or replace view public.daily_demand_model as
select
    sales_date,
    store_id,
    product_id,
    units_sold,
    unfulfilled_units,
    day_of_week,
    sales_month,
    is_weekend,
    lag(units_sold, 1) over (
        partition by store_id, product_id
        order by sales_date
    ) as sales_previous_day,
    lag(units_sold, 7) over (
        partition by store_id, product_id
        order by sales_date
    ) as sales_previous_week,
    avg(units_sold) over (
        partition by store_id, product_id
        order by sales_date
        rows between 7 preceding and 1 preceding
    ) as avg_sales_previous_7_days
from public.daily_demand_features;

-- calculate sales for the following seven days

create or replace view public.pharmacy_forecasting_dataset as
select
    *,
    sum(units_sold) over (
        partition by store_id, product_id
        order by sales_date
        rows between 1 following and 7 following
    ) as target_next_7_days
from public.daily_demand_model;

-- create the final modelling dataset

create or replace view public.pharmacy_forecasting_model_data as
select
    sales_date,
    store_id,
    product_id,
    sales_month,
    sales_previous_day,
    sales_previous_week,
    avg_sales_previous_7_days,
    target_next_7_days
from public.pharmacy_forecasting_dataset
where sales_date between date '2025-01-08' and date '2025-12-24'
and sales_previous_day is not null
and sales_previous_week is not null
and avg_sales_previous_7_days is not null
and target_next_7_days is not null;

select count(*) as modelling_records
from public.pharmacy_forecasting_model_data;

-- customer purchase cohorts

with first_purchase as (
    select
        customer_id,
        date_trunc('month', min(transaction_datetime))::date as cohort_month
    from transactions
    where transaction_status = 'Completed'
    and customer_id is not null
    group by customer_id
),
monthly_activity as (
    select distinct
        customer_id,
        date_trunc('month', transaction_datetime)::date as activity_month
    from transactions
    where transaction_status = 'Completed'
    and customer_id is not null
),
cohort_activity as (
    select
        fp.cohort_month,
        ma.activity_month,
        (
            extract(year from age(ma.activity_month, fp.cohort_month)) * 12
            + extract(month from age(ma.activity_month, fp.cohort_month))
        )::integer as months_since_first_purchase,
        ma.customer_id
    from first_purchase fp
    join monthly_activity ma
        on fp.customer_id = ma.customer_id
)
select
    cohort_month,
    months_since_first_purchase,
    count(distinct customer_id) as active_customers,
    round(
        100.0 * count(distinct customer_id)
        / first_value(count(distinct customer_id)) over (
            partition by cohort_month
            order by months_since_first_purchase
        ),
        2
    ) as retention_percentage
from cohort_activity
group by cohort_month, months_since_first_purchase
order by cohort_month, months_since_first_purchase;

-- rfm customer segmentation

with customer_rfm as (
    select
        customer_id,
        (date '2025-12-31' - max(transaction_datetime::date)) as recency_days,
        count(transaction_id) as frequency,
        sum(net_amount) as monetary_value
    from transactions
    where transaction_status = 'Completed'
    and customer_id is not null
    and transaction_datetime >= timestamp '2025-01-01'
    and transaction_datetime < timestamp '2026-01-01'
    group by customer_id
),
rfm_scores as (
    select
        *,
        ntile(5) over (order by recency_days desc) as recency_score,
        ntile(5) over (order by frequency) as frequency_score,
        ntile(5) over (order by monetary_value) as monetary_score
    from customer_rfm
)
select
    customer_id,
    recency_days,
    frequency,
    monetary_value,
    recency_score,
    frequency_score,
    monetary_score,
    case
        when recency_score >= 4
        and frequency_score >= 4
        and monetary_score >= 4 then 'high value'
        when recency_score >= 3
        and frequency_score >= 3 then 'loyal'
        when recency_score >= 4
        and frequency_score <= 2 then 'new or promising'
        when recency_score <= 2
        and frequency_score >= 3 then 'at risk'
        else 'needs attention'
    end as customer_segment
from rfm_scores
order by monetary_value desc;

-- rfm segment summary

with customer_rfm as (
    select
        customer_id,
        (date '2025-12-31' - max(transaction_datetime::date)) as recency_days,
        count(transaction_id) as frequency,
        sum(net_amount) as monetary_value
    from transactions
    where transaction_status = 'Completed'
    and customer_id is not null
    and transaction_datetime >= timestamp '2025-01-01'
    and transaction_datetime < timestamp '2026-01-01'
    group by customer_id
),
rfm_scores as (
    select
        *,
        ntile(5) over (order by recency_days desc) as recency_score,
        ntile(5) over (order by frequency) as frequency_score,
        ntile(5) over (order by monetary_value) as monetary_score
    from customer_rfm
),
segmented_customers as (
    select
        *,
        case
            when recency_score >= 4
            and frequency_score >= 4
            and monetary_score >= 4 then 'high value'
            when recency_score >= 3
            and frequency_score >= 3 then 'loyal'
            when recency_score >= 4
            and frequency_score <= 2 then 'new or promising'
            when recency_score <= 2
            and frequency_score >= 3 then 'at risk'
            else 'needs attention'
        end as customer_segment
    from rfm_scores
)
select
    customer_segment,
    count(*) as number_of_customers,
    round(avg(recency_days), 2) as average_recency_days,
    round(avg(frequency), 2) as average_frequency,
    round(sum(monetary_value), 2) as total_customer_value
from segmented_customers
group by customer_segment
order by number_of_customers desc;

-- sales by branch

select
    s.store_id,
    s.store_name,
    count(distinct t.transaction_id) as number_of_transactions,
    sum(ti.quantity) as units_sold,
    round(sum(ti.line_net_amount), 2) as net_sales
from stores s
join transactions t
    on s.store_id = t.store_id
join transaction_items ti
    on t.transaction_id = ti.transaction_id
where t.transaction_status = 'Completed'
group by s.store_id, s.store_name
order by net_sales desc;

-- sales by county

select
    s.county,
    count(distinct t.transaction_id) as number_of_transactions,
    sum(ti.quantity) as units_sold,
    round(sum(ti.line_net_amount), 2) as net_sales
from stores s
join transactions t
    on s.store_id = t.store_id
join transaction_items ti
    on t.transaction_id = ti.transaction_id
where t.transaction_status = 'Completed'
group by s.county
order by net_sales desc;

-- sales by product category

select
    p.category,
    sum(ti.quantity) as units_sold,
    round(sum(ti.line_net_amount), 2) as net_sales,
    round(
        sum(ti.line_net_amount) - sum(ti.quantity * ti.unit_cost_at_sale),
        2
    ) as estimated_gross_profit
from transactions t
join transaction_items ti
    on t.transaction_id = ti.transaction_id
join products p
    on ti.product_id = p.product_id
where t.transaction_status = 'Completed'
group by p.category
order by net_sales desc;

-- monthly sales performance

select
    date_trunc('month', t.transaction_datetime)::date as sales_month,
    count(distinct t.transaction_id) as number_of_transactions,
    sum(ti.quantity) as units_sold,
    round(sum(ti.line_net_amount), 2) as net_sales
from transactions t
join transaction_items ti
    on t.transaction_id = ti.transaction_id
where t.transaction_status = 'Completed'
group by date_trunc('month', t.transaction_datetime)
order by sales_month;

-- product performance

select
    p.product_id,
    p.product_name,
    p.category,
    sum(ti.quantity) as units_sold,
    round(sum(ti.line_net_amount), 2) as net_sales,
    round(
        sum(ti.line_net_amount) - sum(ti.quantity * ti.unit_cost_at_sale),
        2
    ) as estimated_gross_profit
from transactions t
join transaction_items ti
    on t.transaction_id = ti.transaction_id
join products p
    on ti.product_id = p.product_id
where t.transaction_status = 'Completed'
group by p.product_id, p.product_name, p.category
order by units_sold desc;
