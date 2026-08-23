select

    cast(order_id as integer) as order_id,

    cast(customer_id as integer) as customer_id,

    cast(product_id as integer) as product_id,

    cast(quantity as integer) as quantity,

    cast(unit_price as numeric(12, 2)) as unit_price,

    cast(discount_pct as numeric(5, 2)) as discount_pct,

    cast(total_amount as numeric(12, 2)) as total_amount,

    lower(trim(status)) as order_status,

    cast(order_date as timestamp) as order_date,

    cast(updated_at as timestamp) as updated_at,

    loaded_at

from {{ source('raw', 'orders') }}