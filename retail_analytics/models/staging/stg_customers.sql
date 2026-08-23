select

    cast(customer_id as integer) as customer_id,

    trim(first_name) as first_name,

    trim(last_name) as last_name,

    lower(trim(email)) as email,

    upper(trim(state)) as state,

    trim(membership_tier) as membership_tier,

    cast(created_at as date) as customer_created_date,

    loaded_at

from {{ source('raw', 'customers') }}