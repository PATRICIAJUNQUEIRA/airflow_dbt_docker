# docker/airflow/Dockerfile
FROM apache/airflow:2.9.3-python3.11

# utilitários básicos
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential git curl jq \
 && rm -rf /var/lib/apt/lists/*
USER airflow

# pip atualizado
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

# providers do Airflow com constraints
ARG AIRFLOW_VERSION=2.9.3
ARG PYTHON_VERSION=3.11
ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
RUN python -m pip install --no-cache-dir --constraint "${CONSTRAINT_URL}" \
    apache-airflow-providers-amazon

# dbt + adapter Athena (versões fixadas)
RUN python -m pip install --no-cache-dir \
    dbt-core==1.9.2 \
    dbt-athena-community==1.9.4 \
    awscli

# deps extras do projeto (unificada na raiz)
COPY requirements.txt /tmp/requirements.txt
RUN if [ -s /tmp/requirements.txt ]; then \
      pip install --no-cache-dir -r /tmp/requirements.txt; \
    fi
