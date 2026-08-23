select

    i.product_id,

    p.product_name,

    p.category,

    i.warehouse,

    i.quantity_on_hand,

    i.reorder_level,

    case

        when i.quantity_on_hand = 0
            then 'OUT_OF_STOCK'

        when i.quantity_on_hand
             <= i.reorder_level
            then 'LOW_STOCK'

        else 'HEALTHY'

    end as inventory_status

from {{ ref('stg_inventory') }} i

left join {{ ref('stg_products') }} p

    on i.product_id = p.product_id