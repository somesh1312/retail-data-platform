select

    customer_id,

    first_name,

    last_name,

    email,

    state,

    membership_tier,

    customer_created_date

from {{ ref('stg_customers') }}