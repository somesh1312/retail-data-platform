select *

from {{ ref('fct_orders') }}

where total_amount < 0