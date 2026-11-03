-- Completed revenue must be the same whether grouped by customer or by date.
with customer_total as (
    select coalesce(sum(completed_revenue), 0) as completed_revenue
    from {{ ref('dim_customers') }}
),

daily_total as (
    select coalesce(sum(completed_revenue), 0) as completed_revenue
    from {{ ref('fct_daily_sales') }}
)

select
    customer_total.completed_revenue as customer_completed_revenue,
    daily_total.completed_revenue as daily_completed_revenue
from customer_total
cross join daily_total
where customer_total.completed_revenue != daily_total.completed_revenue
