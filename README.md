# data-journey

My 64-session plan (Tue Nov 10, 2026 to Tue Feb 16, 2027) to get familiar with data engineering and AWS, with Tableau analytics built in at every stage.

- **Learning nights:** Monday to Thursday, 8:30 to 9:30 PM (Asia/Manila). One hour: watch, read, optionally try something.
- **Saturday labs:** 2 to 4 PM. Hands-on practice and the milestone builds.
- **No assignments.** Five milestone projects instead. Friday and Sunday stay free. Break from Dec 24 to Jan 3.
- **Can't make a session?** Delete the calendar event and the rest shift forward (see [`plan/`](plan/README.md)).

Daily notes live in Notion; progress is tracked on a live dashboard.

## The 4 stages

| # | Stage | Sessions | Dates | Milestone |
|---|-------|----------|-------|-----------|
| 1 | Data foundations + Tableau: lifecycle, Git, SQL, Python, pandas, APIs, Tableau basics | 1–19 | Nov 10 – Dec 5 | M1: Python ETL pipeline + first Tableau dashboard |
| 2 | Data engineering tools: Docker, Airflow, dbt, streaming and Spark overviews, Tableau LODs | 20–29 | Dec 7 – Dec 19 | M2: Orchestrated pipeline with Airflow and dbt |
| 3 | AWS for data: cloud basics, IAM, S3, EC2, VPC, databases, Lambda, Glue, Athena, Step Functions, Terraform, CI/CD | 30–47 | Dec 21 – Jan 23 | M3: Serverless AWS data pipeline |
| 4 | Analytics with Tableau on AWS: charts, Tableau products, Cloud, RLS, Athena connector, Tableau Next | 48–64 | Jan 25 – Feb 16 | M4: Interactive Tableau dashboard · M5: Capstone, AWS → Tableau Cloud with RLS |

Milestone dates are the original plan. They move if sessions are skipped; the calendar always has the current date.

## Folder map

| Folder | What goes here |
|--------|----------------|
| `week01/` | Day 1–2 notes: DE lifecycle, star schema |
| `sql/` | Daily SQL practice and the cleaning project |
| `python/` | Python scripts (cleaning, validation, API, boto3) |
| `data/` | Small sample datasets (large files are git-ignored) |
| `project1/` … `project4/` | Milestones 1–4, each with its own README |
| `dags/` | Airflow DAGs |
| `dbt/` | dbt project |
| `streaming/` | Kafka producer and consumer |
| `spark/` | PySpark notebooks |
| `aws/` | AWS setup notes, IAM policies, diagrams |
| `iac/` | Terraform and CloudFormation |
| `tableau/` | Tableau notes and links to Tableau Public |
| `review/` | Weekly review answers |
| `capstone/` | Milestone 5: AWS → Tableau Cloud capstone |
| `plan/` | Schedule data and the auto-shift script |

## Rules I follow

- Never commit passwords, access keys or `.env` files (see `.gitignore`).
- Delete AWS resources at the end of every AWS session and check Billing.
- Commit message format: `Session N: <topic>` or `M1: <what changed>`.

## Progress

- [ ] M1 · [ ] M2 · [ ] M3 · [ ] M4 · [ ] M5 (capstone)
