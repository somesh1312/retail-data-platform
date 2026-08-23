select

    cast(order_date as date) as sales_date,

    category,

    customer_state,

    count(distinct order_id) as total_orders,

    count(distinct customer_id) as unique_customers,

    sum(quantity) as units_sold,

    round(
        sum(total_amount),
        2
    ) as revenue,

    round(
        avg(total_amount),
        2
    ) as average_order_value

from {{ ref('fct_orders') }}

where order_status != 'cancelled'

group by

    cast(order_date as date),

    category,

    customer_state