select

    product_id,

    product_name,

    category,

    product_price,

    is_active

from {{ ref('stg_products') }}