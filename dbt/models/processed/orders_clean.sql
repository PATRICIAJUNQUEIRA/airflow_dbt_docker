-- models/processed/orders_clean.sql
{{ config(
  materialized='incremental',
  incremental_strategy='insert_overwrite',
  partitioned_by=['dt'],
  format='parquet',
  external_location='s3://pt-data-lab/processed-data/analytics/orders_clean/'
) }}

with src as (
  select
    cast(order_id as varchar)   as order_id,
    cast(customer  as varchar)  as customer_id,
    try(cast(amount as double)) as amount,
    case
      when dt is null or length(trim(dt)) = 0 then null
      else try(cast(trim(dt) as date))
    end                         as dt
  from {{ source('raw', 'orders_raw') }}
)

select *
from src
{% if is_incremental() %}
  where dt > (select coalesce(max(dt), date '1900-01-01') from {{ this }})
{% endif %}
