{{
    config(
        materialized='incremental',
        unique_key='order_id'
    )
}}


select

    o.order_id,

    o.customer_id,

    o.product_id,

    o.quantity,

    o.unit_price,

    o.discount_pct,

    o.total_amount,

    o.order_status,

    o.order_date,

    o.updated_at,

    c.state as customer_state,

    c.membership_tier,

    p.product_name,

    p.category

from {{ ref('stg_orders') }} o

left join {{ ref('stg_customers') }} c
    on o.customer_id = c.customer_id

left join {{ ref('stg_products') }} p
    on o.product_id = p.product_id


{% if is_incremental() %}

where o.updated_at >=
(
    select
        coalesce(
            max(updated_at)
            - interval '2 days',
            '1900-01-01'
        )

    from {{ this }}
)

{% endif %}