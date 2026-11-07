# data-journey

My 55-day sprint (Nov 7 – Dec 31, 2026) from data engineering foundations to AWS, automation, AI/ML and Tableau.
Each day's work is pushed here. Daily notes live in Notion; progress is tracked on a live dashboard.

## The 8 phases

| # | Phase | Days | Dates | Portfolio output |
|---|-------|------|-------|------------------|
| 1 | DE Foundations: lifecycle, SQL, Python, pandas, APIs | 1–11 | Nov 7 – Nov 17 | Project 1: Python ETL pipeline |
| 2 | DE Tools: Docker, Airflow, dbt, modern data stack | 12–17 | Nov 18 – Nov 23 | Project 2: Airflow + dbt on Postgres |
| 3 | Advanced DE: Kafka, streaming, Spark, Databricks, lakehouse | 18–22 | Nov 24 – Nov 28 | Project 3: Medallion lakehouse |
| 4 | Cloud & AWS: IAM, EC2, S3, VPC, databases, Lambda, Glue, Athena | 23–33 | Nov 29 – Dec 9 | AWS notes and policies |
| 5 | Automation & DevOps: Step Functions, Terraform, CI/CD, n8n | 34–38 | Dec 10 – Dec 14 | Project 4: S3 → Lambda → Glue → Athena |
| 6 | AI & ML: ML basics, SageMaker AI, Bedrock, RAG, agents | 39–44 | Dec 15 – Dec 20 | Project 5: Bedrock RAG assistant |
| 7 | Tableau: products, calculations, LOD, dashboards, RLS | 45–52 | Dec 21 – Dec 28 | Tableau Public dashboard |
| 8 | Integration: Tableau Cloud/Next, Athena, capstone | 53–55 | Dec 29 – Dec 31 | Capstone: AWS → Tableau with RLS |

## Folder map

| Folder | What goes here |
|--------|----------------|
| `week01/` | Day 1–2 notes: DE lifecycle, star schema |
| `sql/` | Daily SQL practice and the cleaning project |
| `python/` | Python scripts (cleaning, validation, API, boto3) |
| `data/` | Small sample datasets (large files are git-ignored) |
| `project1/` … `project5/` | Portfolio projects, each with its own README |
| `dags/` | Airflow DAGs |
| `dbt/` | dbt project |
| `streaming/` | Kafka producer and consumer |
| `spark/` | PySpark notebooks |
| `aws/` | AWS setup notes, IAM policies, diagrams |
| `iac/` | Terraform and CloudFormation |
| `ml/` | ML notebooks and glossary |
| `tableau/` | Tableau notes and links to Tableau Public |
| `review/` | Weekly review answers |
| `capstone/` | Final AWS → Tableau project |

## Rules I follow

- Never commit passwords, access keys or `.env` files (see `.gitignore`).
- Delete AWS resources at the end of every AWS session and check Billing.
- One commit per day, message format: `Day N: <topic>`.

## Progress

- [ ] Phase 1 · [ ] Phase 2 · [ ] Phase 3 · [ ] Phase 4 · [ ] Phase 5 · [ ] Phase 6 · [ ] Phase 7 · [ ] Phase 8
