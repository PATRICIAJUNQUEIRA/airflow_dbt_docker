from __future__ import annotations

import os
import pendulum
from datetime import timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
S3_BUCKET = os.getenv("S3_BUCKET", "")
ATHENA_DB = os.getenv("ATHENA_DB", "analytics")

LOCAL_CSV = "/tmp/orders.csv"
S3_KEY = "raw-data/orders/orders.csv"

BASE_ENV = {
    "AWS_DEFAULT_REGION": AWS_REGION,
    "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID", ""),
    "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
    "S3_BUCKET": S3_BUCKET,
    "ATHENA_DB": ATHENA_DB,
    "PATH": "/home/airflow/.local/bin:/usr/local/bin:/usr/bin:/bin",
    "HOME": "/home/airflow",
}

def _sh(cmd: str) -> str:
    return "set -Eeuo pipefail -x; " + cmd

default_args = {"retries": 1, "execution_timeout": timedelta(minutes=10)}

with DAG(
    dag_id="orders_pipeline",
    schedule=None,
    start_date=pendulum.datetime(2025, 8, 1, tz="America/Sao_Paulo"),
    catchup=False,
    default_args=default_args,
    tags=["orders", "s3", "athena"],
) as dag:

    generate_orders_csv = BashOperator(
        task_id="generate_orders_csv",
        bash_command=_sh(f"""
cat > {LOCAL_CSV} <<'CSV'
order_id,order_date,customer,amount
1,2024-01-05,Ana,120.50
2,2024-01-07,Bruno,89.90
3,2024-01-08,Carla,45.00
4,2024-01-09,Ana,77.10
CSV
ls -lah {LOCAL_CSV}
head -n 3 {LOCAL_CSV} || true
"""),
        env=BASE_ENV,
        do_xcom_push=False,
    )

    upload_to_s3 = BashOperator(
        task_id="upload_to_s3",
        bash_command=_sh(f"""
test -f {LOCAL_CSV}
aws s3 cp {LOCAL_CSV} s3://$S3_BUCKET/{S3_KEY} --content-type text/csv
aws s3 ls s3://$S3_BUCKET/raw-data/orders/ || true
"""),
        env=BASE_ENV,
        do_xcom_push=False,
    )

    create_external_table_if_not_exists = BashOperator(
        task_id="create_external_table_if_not_exists",
        bash_command=_sh("""
SQL=\"\"\"
CREATE EXTERNAL TABLE IF NOT EXISTS analytics.orders_raw (
  order_id    int,
  order_date  string,
  customer    string,
  amount      double
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES ('serialization.format' = ',', 'field.delim' = ',')
LOCATION 's3://$S3_BUCKET/raw-data/orders/'
TBLPROPERTIES ('skip.header.line.count'='1');
\"\"\"
aws athena start-query-execution \
  --query-string "$SQL" \
  --query-execution-context "Database=$ATHENA_DB" \
  --work-group primary >/dev/null
"""),
        env=BASE_ENV,
        do_xcom_push=False,
    )

    add_partition = BashOperator(
        task_id="add_partition",
        bash_command=_sh("""
SQL="SELECT count(*) AS cnt FROM analytics.orders_raw;"
QID=$(aws athena start-query-execution \
  --query-string "$SQL" \
  --query-execution-context "Database=$ATHENA_DB" \
  --work-group primary \
  --query 'QueryExecutionId' --output text)
aws athena get-query-execution --query-execution-id "$QID" --query 'QueryExecution.Status.State' --output text
"""),
        env=BASE_ENV,
        do_xcom_push=False,
    )

    generate_orders_csv >> upload_to_s3 >> create_external_table_if_not_exists >> add_partition
