{{ config(materialized='table') }}

select
    customer_id,
    min(order_date) as first_order_date,
    max(order_date) as last_order_date,
    count(*) as order_count,
    countif(status = 'completed') as completed_order_count,
    coalesce(sum(case when status = 'completed' then amount end), 0) as completed_revenue
from {{ ref('stg_orders') }}
group by customer_id
