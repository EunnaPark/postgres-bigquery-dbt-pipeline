{{ config(materialized='table') }}

select
    order_date,
    status,
    count(*) as order_count,
    sum(amount) as total_amount
from {{ ref('stg_orders') }}
group by order_date, status
