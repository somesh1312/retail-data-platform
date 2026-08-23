select

    cast(product_id as integer) as product_id,

    trim(product_name) as product_name,

    trim(category) as category,

    cast(price as numeric(12, 2)) as product_price,

    cast(active as boolean) as is_active,

    loaded_at

from {{ source('raw', 'products') }}