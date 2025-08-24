FROM apache/airflow:2.9.3-python3.11

# utilitários de sistema (compilação etc.)
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl jq \
 && rm -rf /var/lib/apt/lists/*
USER airflow

# pip atualizado
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

# providers do Airflow com constraints correspondentes à versão da imagem
ARG AIRFLOW_VERSION=2.9.3
ARG PYTHON_VERSION=3.11
ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
RUN python -m pip install --no-cache-dir --constraint "${CONSTRAINT_URL}" \
    apache-airflow-providers-amazon

# dbt 1.9 + adapter Athena (sem constraints do Airflow)
RUN python -m pip install --no-cache-dir \
    dbt-core==1.9.2 \
    dbt-athena-community==1.9.4 \
    awscli
