{{ config(materialized="table") }}
select
  1    as ok,
  current_date as run_dt
