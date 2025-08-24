from __future__ import annotations

import os
import pendulum
from datetime import timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_BIN = "/home/airflow/.local/bin/dbt"
DBT_PROJECT_DIR = "/opt/airflow/dbt"
DBT_PROFILES_DIR = "/opt/airflow/.dbt"

BASE_ENV = {
    "S3_BUCKET": os.getenv("S3_BUCKET", ""),
    "ATHENA_DB": os.getenv("ATHENA_DB", ""),
    "AWS_DEFAULT_REGION": os.getenv("AWS_DEFAULT_REGION", "us-east-2"),
    "DBT_PROFILES_DIR": DBT_PROFILES_DIR,
    "PATH": "/home/airflow/.local/bin:/usr/local/bin:/usr/bin:/bin",
    "HOME": "/home/airflow",
    "DBT_LOG_FORMAT": "text",
    "DBT_SEND_ANONYMOUS_USAGE_STATS": "false",
}

def _cmd(cmd: str) -> str:
    return (
        "set -Eeuo pipefail -x; "
        f"cd {DBT_PROJECT_DIR}; "
        "echo 'which dbt='$(command -v dbt || true); "
        f"{DBT_BIN} --version || true; "
        f"echo \"ENV S3_BUCKET=$S3_BUCKET ATHENA_DB=$ATHENA_DB AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION\"; "
        f"{cmd}"
    )

default_args = {"retries": 1, "execution_timeout": timedelta(minutes=20)}

with DAG(
    dag_id="dbt_athena_pipeline",
    schedule="30 6 * * *",
    start_date=pendulum.datetime(2025, 8, 1, tz="America/Sao_Paulo"),
    catchup=False,
    default_args=default_args,
    tags=["dbt", "athena"],
) as dag:

    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=_cmd(f"{DBT_BIN} deps --profiles-dir {DBT_PROFILES_DIR} -v"),
        env=BASE_ENV,
        do_xcom_push=False,
    )

    dbt_stage_external = BashOperator(
        task_id="dbt_stage_external_sources",
        bash_command=_cmd(
            f"{DBT_BIN} run-operation stage_external_sources "
            f"--profiles-dir {DBT_PROFILES_DIR} --target dev -v"
        ),
        env=BASE_ENV,
        do_xcom_push=False,
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=_cmd(
            f"{DBT_BIN} build --no-use-colors --profiles-dir {DBT_PROFILES_DIR} --target dev -v"
        ),
        env=BASE_ENV,
        do_xcom_push=False,
    )

    dbt_deps >> dbt_stage_external >> dbt_build
