# Airflow + Athena/S3 + Prometheus/Grafana — Orders Pipeline

Pipeline demonstrativo com **Airflow** orquestrando:
- ingestão de um CSV local para **S3 (raw)**  
- criação de **tabela externa (Athena/Glue)**  
- **CTAS** para **Parquet** em `processed-data/`  
- (opcional) checagens de **Data Quality**  
- **Observabilidade** com StatsD → **Prometheus → Grafana**

> Ideal para entrevistas / POCs de **Modern Data Stack** com governança básica.

---

## Sumário
- [Arquitetura](#arquitetura)
- [O que está incluso](#o-que-está-incluso)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Pré-requisitos](#pré-requisitos)
- [.env (template)](#env-template)
- [Subindo o ambiente](#subindo-o-ambiente)
- [Executando a DAG](#executando-a-dag)
- [Validações & consultas (Athena)](#validações--consultas-athena)
- [Observabilidade (Prometheus/Grafana)](#observabilidade-prometheusgrafana)
- [Governança implementada](#governança-implementada)
- [Troubleshooting](#troubleshooting)
- [Política IAM mínima (anexo)](#política-iam-mínima-anexo)
- [Roadmap / próximos passos](#roadmap--próximos-passos)
- [“Talk track” para entrevista](#talk-track-para-entrevista)

---

## O que está incluso

- **DAG `orders_pipeline`** com as seguintes tasks:
    1. `upload_csv_to_s3`: Envia `data/orders.csv` para `s3://<bucket>/raw-data/orders.csv`.
    2. `ensure_glue_db`: Cria o database no Glue se ele não existir.
    3. `create_external_raw_orders`: Cria uma tabela externa sobre o CSV.
    4. `drop_orders_summary_if_exists`: Garante a idempotência do CTAS.
    5. `clear_output_prefix`: Limpa o prefixo de saída para evitar duplicações.
    6. `ctas_orders_summary`: Gera o arquivo Parquet em `processed-data/orders_summary/`.
- **Observabilidade**: `statsd-exporter`, Prometheus (`:9090`) e Grafana (`:3000`).
- **Governança**: Política de **IAM mínimo**, uso do **Glue Catalog**, logs detalhados por task e recomendações de segurança.

> Funções de **Data Quality (DQ)** já estão prontas no código (checando se o Parquet existe, se há nulos em `raw_orders` e se a contagem de registros em `orders_summary` é maior que zero). Você pode adicioná-las como tasks extras ao pipeline se desejar.

---

## Estrutura do repositório

├─ dags/

│ └─ orders_pipeline.py # DAG completa (Athena + S3 + CTAS)

├─ data/

│ └─ orders.csv # base demo

├─ docker/

│ └─ airflow/ # Dockerfile + requirements do Airflow

├─ prometheus/

│ └─ prometheus.yml # scrape statsd-exporter

├─ grafana/ # (opcional) dashboards/provisioning

├─ .env # variáveis locais (NÃO commitar)

└─ docker-compose.yml

---

## Pré-requisitos
- 1.Bucket S3 criado na sua região (ex.: pt-data-lab em us-east-2).
  
Prefixos utilizados:

`s3://pt-data-lab/`
`raw-data/`
`processed-data/`
`athena-staging/`

- 2.Usuário IAM

- (ex.: airflow-dbt-dev) com Access Key e Secret Key ativas e política mínima (ver Política IAM mínima).

- 3.Docker + Docker Compose instalados.
     
---
## .env (template)
 ⚠️ Nunca commite o .env no Git.

 ---
 #Subindo o ambiente
- 1.Subir tudo:
  `docker compose up -d
---
## Criar usuário admin no Airflow (se necessário):

docker compose exec airflow-webserver airflow users create \
  --role Admin --username admin --password admin \
  --email admin@example.com --firstname Admin --lastname User
## Arquitetura

---
```mermaid
graph TD
    subgraph Data
        CSV(CSV local)
    end

    subgraph Orchestration
        Airflow(Airflow)
    end

    subgraph AWS
        S3(S3: raw-data/ & processed-data/)
        Athena(Athena)
        Glue(Glue Catalog)
    end

    subgraph Monitoring
        StatsD(StatsD Exporter)
        Prometheus(Prometheus)
        Grafana(Grafana)
    end

    CSV --> Airflow
    Airflow -- Upload --> S3
    Airflow -- Create Table --> Athena
    Airflow -- CTAS --> Athena
    Athena -- Query --> S3
    Athena -- Catalog --> Glue
    Airflow -- Metrics --> StatsD
    StatsD --> Prometheus
    Prometheus --> Grafana


