select
    order_id,
    status,
    amount
from {{ ref('stg_orders') }}
where amount < 0
   or (status = 'completed' and amount = 0)
