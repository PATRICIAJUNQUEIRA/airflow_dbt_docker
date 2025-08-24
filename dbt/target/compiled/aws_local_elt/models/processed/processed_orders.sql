

SELECT
  cast(order_id as varchar)  as order_id,
  cast(order_date as date)   as order_date,
  upper(customer)            as customer,
  cast(amount as double)     as amount,
  date_trunc('day', order_date) as order_day
FROM "AwsDataCatalog"."analytics"."orders_raw"
WHERE amount > 0