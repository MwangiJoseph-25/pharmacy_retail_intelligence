-- Pharmacy Customer and Sales Intelligence
-- PostgreSQL table definitions
-- Source: schema-only dump from Customer_sales_intelligence, public schema.
-- This script creates the 15 operational tables and their primary/foreign keys.
-- It does not import data or create the analytical views.

CREATE TABLE public.stores (
    store_id character varying(10) NOT NULL,
    store_name character varying(100),
    county character varying(50),
    town character varying(50),
    opening_date date,
    store_status character varying(30),
    CONSTRAINT stores_pkey PRIMARY KEY (store_id)
);

CREATE TABLE public.products (
    product_id character varying(10) NOT NULL,
    product_name character varying(150),
    active_ingredient character varying(100),
    strength character varying(50),
    dosage_form character varying(50),
    category character varying(80),
    unit_of_measure character varying(80),
    unit_cost numeric(12,2),
    selling_price numeric(12,2),
    product_status character varying(30),
    CONSTRAINT products_pkey PRIMARY KEY (product_id)
);

CREATE TABLE public.suppliers (
    supplier_id character varying(10) NOT NULL,
    supplier_name character varying(150),
    supplier_type character varying(100),
    supplier_status character varying(30),
    CONSTRAINT suppliers_pkey PRIMARY KEY (supplier_id)
);

CREATE TABLE public.customers (
    customer_id character varying(20) NOT NULL,
    registration_date date,
    customer_segment character varying(50),
    customer_status character varying(30),
    CONSTRAINT customers_pkey PRIMARY KEY (customer_id)
);

CREATE TABLE public.promotions (
    promotion_id character varying(20) NOT NULL,
    promotion_name character varying(150),
    promotion_type character varying(50),
    product_id character varying(20),
    category character varying(80),
    start_date date,
    end_date date,
    discount_type character varying(30),
    discount_value numeric(12,2),
    CONSTRAINT promotions_pkey PRIMARY KEY (promotion_id)
);

CREATE TABLE public.transactions (
    transaction_id character varying(20) NOT NULL,
    transaction_datetime timestamp without time zone,
    store_id character varying(10),
    customer_id character varying(20),
    payment_method character varying(30),
    transaction_status character varying(30),
    currency_code character varying(5),
    gross_amount numeric(12,2),
    discount_amount numeric(12,2),
    net_amount numeric(12,2),
    CONSTRAINT transactions_pkey PRIMARY KEY (transaction_id),
    CONSTRAINT transactions_customer_id_fkey
        FOREIGN KEY (customer_id) REFERENCES public.customers(customer_id),
    CONSTRAINT transactions_store_id_fkey
        FOREIGN KEY (store_id) REFERENCES public.stores(store_id)
);

CREATE TABLE public.purchase_orders (
    purchase_order_id character varying(20) NOT NULL,
    supplier_id character varying(10),
    store_id character varying(10),
    order_date date,
    expected_delivery_date date,
    order_status character varying(30),
    CONSTRAINT purchase_orders_pkey PRIMARY KEY (purchase_order_id),
    CONSTRAINT purchase_orders_store_id_fkey
        FOREIGN KEY (store_id) REFERENCES public.stores(store_id),
    CONSTRAINT purchase_orders_supplier_id_fkey
        FOREIGN KEY (supplier_id) REFERENCES public.suppliers(supplier_id)
);

CREATE TABLE public.transaction_items (
    transaction_id character varying(20) NOT NULL,
    line_id integer NOT NULL,
    product_id character varying(10),
    quantity integer,
    unit_price numeric(12,2),
    discount_amount numeric(12,2),
    unit_cost_at_sale numeric(12,2),
    line_gross_amount numeric(12,2),
    line_net_amount numeric(12,2),
    promotion_id character varying(20),
    CONSTRAINT transaction_items_pkey PRIMARY KEY (transaction_id, line_id),
    CONSTRAINT transaction_items_product_id_fkey
        FOREIGN KEY (product_id) REFERENCES public.products(product_id),
    CONSTRAINT transaction_items_promotion_id_fkey
        FOREIGN KEY (promotion_id) REFERENCES public.promotions(promotion_id),
    CONSTRAINT transaction_items_transaction_id_fkey
        FOREIGN KEY (transaction_id) REFERENCES public.transactions(transaction_id)
);

CREATE TABLE public.purchase_order_items (
    purchase_order_id character varying(20) NOT NULL,
    line_id integer NOT NULL,
    product_id character varying(10),
    quantity_ordered integer,
    quantity_received integer,
    unit_purchase_cost numeric(12,2),
    CONSTRAINT purchase_order_items_pkey PRIMARY KEY (purchase_order_id, line_id),
    CONSTRAINT purchase_order_items_product_id_fkey
        FOREIGN KEY (product_id) REFERENCES public.products(product_id),
    CONSTRAINT purchase_order_items_purchase_order_id_fkey
        FOREIGN KEY (purchase_order_id) REFERENCES public.purchase_orders(purchase_order_id)
);

CREATE TABLE public.inventory_movements (
    movement_id character varying(20) NOT NULL,
    movement_datetime timestamp without time zone,
    store_id character varying(10),
    product_id character varying(10),
    movement_type character varying(50),
    quantity_change integer,
    reference_type character varying(30),
    reference_id character varying(30),
    CONSTRAINT inventory_movements_pkey PRIMARY KEY (movement_id),
    CONSTRAINT inventory_movements_product_id_fkey
        FOREIGN KEY (product_id) REFERENCES public.products(product_id),
    CONSTRAINT inventory_movements_store_id_fkey
        FOREIGN KEY (store_id) REFERENCES public.stores(store_id)
);

CREATE TABLE public.open_inventory (
    store_id character varying(10) NOT NULL,
    product_id character varying(10) NOT NULL,
    opening_quantity integer,
    as_of_date date,
    CONSTRAINT open_inventory_pkey PRIMARY KEY (store_id, product_id),
    CONSTRAINT open_inventory_product_id_fkey
        FOREIGN KEY (product_id) REFERENCES public.products(product_id),
    CONSTRAINT open_inventory_store_id_fkey
        FOREIGN KEY (store_id) REFERENCES public.stores(store_id)
);

CREATE TABLE public.sales_returns (
    return_id character varying(20) NOT NULL,
    original_transaction_id character varying(20),
    return_datetime timestamp without time zone,
    store_id character varying(10),
    return_reason character varying(100),
    refund_amount numeric(12,2),
    CONSTRAINT sales_returns_pkey PRIMARY KEY (return_id),
    CONSTRAINT sales_returns_original_transaction_id_fkey
        FOREIGN KEY (original_transaction_id) REFERENCES public.transactions(transaction_id),
    CONSTRAINT sales_returns_store_id_fkey
        FOREIGN KEY (store_id) REFERENCES public.stores(store_id)
);

CREATE TABLE public.sales_return_items (
    return_id character varying(20) NOT NULL,
    line_id integer NOT NULL,
    product_id character varying(10),
    quantity_returned integer,
    unit_refund_amount numeric(12,2),
    restockable boolean,
    CONSTRAINT sales_return_items_pkey PRIMARY KEY (return_id, line_id),
    CONSTRAINT sales_return_items_product_id_fkey
        FOREIGN KEY (product_id) REFERENCES public.products(product_id),
    CONSTRAINT sales_return_items_return_id_fkey
        FOREIGN KEY (return_id) REFERENCES public.sales_returns(return_id)
);

CREATE TABLE public.price_changes (
    product_id character varying(10) NOT NULL,
    effective_date date NOT NULL,
    new_unit_cost numeric(12,2),
    new_selling_price numeric(12,2),
    reason character varying(150),
    CONSTRAINT price_changes_pkey PRIMARY KEY (product_id, effective_date),
    CONSTRAINT price_changes_product_id_fkey
        FOREIGN KEY (product_id) REFERENCES public.products(product_id)
);

CREATE TABLE public.lost_sales_log (
    transaction_id character varying(20) NOT NULL,
    transaction_date date,
    store_id character varying(10),
    product_id character varying(10) NOT NULL,
    quantity_demanded integer,
    quantity_fulfilled integer,
    outcome character varying(50),
    CONSTRAINT lost_sales_log_pkey PRIMARY KEY (transaction_id, product_id),
    CONSTRAINT lost_sales_log_product_id_fkey
        FOREIGN KEY (product_id) REFERENCES public.products(product_id),
    CONSTRAINT lost_sales_log_store_id_fkey
        FOREIGN KEY (store_id) REFERENCES public.stores(store_id)
);
