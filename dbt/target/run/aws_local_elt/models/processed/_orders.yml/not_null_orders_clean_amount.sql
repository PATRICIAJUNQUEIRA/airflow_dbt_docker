
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select amount
from "AwsDataCatalog"."analytics"."orders_clean"
where amount is null



  
  
      
    ) dbt_internal_test