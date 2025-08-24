-- models/processed/orders_clean.sql


with src as (
  select
    cast(order_id as varchar)   as order_id,
    cast(customer  as varchar)  as customer_id,
    try(cast(amount as double)) as amount,
    case
      when dt is null or length(trim(dt)) = 0 then null
      else try(cast(trim(dt) as date))
    end                         as dt
  from "AwsDataCatalog"."analytics"."orders_raw"
)

select *
from src

  where dt > (select coalesce(max(dt), date '1900-01-01') from "AwsDataCatalog"."analytics"."orders_clean")
