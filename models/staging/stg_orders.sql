{{ config(materialized='view') }}

select
    order_id,
    customer_id,
    order_date,
    lower(trim(status)) as status,
    amount,
    updated_at
from {{ source('postgres_cdc', 'orders') }}
