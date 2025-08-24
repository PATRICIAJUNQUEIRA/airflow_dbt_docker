FROM apache/airflow:2.9.2-python3.11
USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
COPY dags/ /opt/airflow/dags/
COPY plugins/ /opt/airflow/plugins/
COPY dbt/ /opt/airflow/dbt/
