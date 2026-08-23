select

    cast(product_id as integer) as product_id,

    trim(warehouse) as warehouse,

    cast(quantity_on_hand as integer)
        as quantity_on_hand,

    cast(reorder_level as integer)
        as reorder_level,

    cast(last_updated as timestamp)
        as last_updated,

    loaded_at

from {{ source('raw', 'inventory') }}