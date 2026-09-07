# Production RAG Assistant

A production-oriented Retrieval-Augmented Generation (RAG) service built
to learn and demonstrate the full lifecycle of an AI application:
ingestion, embeddings, vector retrieval, grounded generation,
evaluation, observability, testing, containerization, CI/CD, and AWS
deployment.

> This repository is intentionally more than a RAG demo. It demonstrates
> the engineering concerns that appear when an LLM application moves
> from a prototype into a deployable service.

## 1. What the system does

The application answers questions using an internal document corpus
rather than relying only on the LLM's pretrained knowledge. The learning
corpus is an Acme Technologies employee handbook.

Example question: `How many vacation days do employees get?`

Expected grounded answer:
`Full-time employees receive 30 days of paid annual leave per calendar year.`

The API returns source metadata such as filename, page number, and
retrieval similarity. If retrieval confidence is too weak, the
application deliberately abstains instead of forcing the LLM to invent
an answer.

## 2. Architecture

``` text
OFFLINE / INGESTION
PDF -> PyMuPDF extraction -> section-aware chunks -> PostgreSQL
                                               -> OpenAI embeddings -> pgvector

ONLINE / QUERY
Client -> POST /chat -> FastAPI -> query embedding -> pgvector retrieval
                                      |                    |
                                      +<-- relevant chunks-+
                                      |
                               similarity threshold
                                  /           \
                          weak evidence      good evidence
                              |                  |
                    deterministic abstain   prompt builder
                                                 |
                                          OpenAI generation
                                                 |
                                          answer + sources
```

Langfuse traces the request, retrieval, embedding, vector search, and
generation stages.

## 3. Stack

  --------------------------------------------------------------------------
  Layer                   Technology                 Purpose
  ----------------------- -------------------------- -----------------------
  API                     FastAPI                    HTTP API and validation

  Language                Python 3.12                Application
                                                     implementation

  Database                PostgreSQL 17              Documents, chunks,
                                                     metadata

  Vector search           pgvector                   Vector storage and
                                                     cosine search

  PDF parsing             PyMuPDF                    Text extraction with
                                                     page metadata

  Embeddings              OpenAI                     1536-dimensional
                          `text-embedding-3-small`   semantic vectors

  Generation              OpenAI `gpt-4.1-mini`      Grounded answer
                                                     generation

  Observability           Langfuse                   Tracing and evaluation

  Testing                 pytest                     Unit/integration tests

  Quality                 Ruff + mypy                Linting, formatting,
                                                     typing

  Containerization        Docker                     Reproducible runtime

  Local orchestration     Docker Compose             API +
                                                     PostgreSQL/pgvector

  CI/CD                   GitHub Actions             Quality gates and
                                                     deployment

  Registry                Amazon ECR                 Container image storage

  Runtime                 Amazon ECS + Fargate       Managed container
                                                     execution

  Cloud DB                Amazon RDS PostgreSQL      Managed
                                                     PostgreSQL/pgvector

  Secrets                 AWS Secrets Manager        Runtime credentials

  Logs                    CloudWatch Logs            ECS/application logs

  CD authentication       GitHub OIDC + AWS STS      Temporary AWS
                                                     credentials
  --------------------------------------------------------------------------

## 4. Repository structure

``` text
production-rag-assistant/
├── app/
│   ├── core/              # config and application errors
│   ├── db/                # pool and schema bootstrap
│   ├── embeddings/        # embedding provider integration
│   ├── ingestion/         # extraction/chunk ingestion
│   ├── observability/     # Langfuse integration
│   ├── repositories/      # database access
│   ├── schemas/           # API contracts
│   ├── main.py            # FastAPI application
│   └── rag_service.py     # RAG orchestration
├── db/init/001_init.sql
├── tests/
├── .github/workflows/ci.yml
├── .github/workflows/cd.yml
├── Dockerfile
├── docker-compose.yml
├── ecs-task-definition.json
├── requirements.txt
├── .env.dummy
└── README.md
```

The exact repository can contain additional modules/tests.

## 5. RAG design decisions

### Extraction and chunking

PyMuPDF extracts text while page numbers are preserved for citations.
The project uses section-aware chunking rather than blindly splitting
every N characters. Chunking is a retrieval decision: chunks must be
specific enough for precision while retaining enough context to answer
the question.

The sample handbook is mostly simple text. Tables, scanned PDFs, images,
source code, or complex nested documents would require a different
parsing/chunking strategy.

### Embeddings

Document chunks use `text-embedding-3-small`; vectors are persisted in
`document_chunks.embedding vector(1536)`. Persisting document embeddings
avoids recomputation across requests. Query embeddings are generated at
request time and are ephemeral for this use case.

### Retrieval

The question is embedded and compared with stored vectors using pgvector
cosine distance. A bound query vector must be cast correctly,
e.g. `%s::vector`, because PostgreSQL otherwise may infer an array type
incompatible with pgvector's operator.

Database rows are converted into typed `RetrievedChunk` objects rather
than leaking positional tuples through the application.

### Weak retrieval

A RAG system should not assume every question is answerable. The
development system used a minimum similarity threshold around `0.45`. If
no sufficiently relevant evidence remains, it returns:

``` json
{
  "answer": "I don't know based on the available company documents.",
  "sources": []
}
```

The LLM is not called on this branch. The threshold is experimental and
must be calibrated against representative evaluation data; it is not a
universal value.

### Generation and sources

Retrieved evidence is inserted into a controlled prompt and passed to
the generation model. The response includes source metadata so the
caller can inspect where the answer came from.

## 6. Local setup

### Prerequisites

Install Git, Python 3.12, PostgreSQL 17 + pgvector (or Docker Desktop),
Docker/Compose, and obtain OpenAI credentials. Langfuse credentials are
needed for tracing. AWS CLI is needed only to reproduce AWS
infrastructure/deployment operations; it is a developer/infrastructure
tool and does **not** belong in `requirements.txt`.

### Clone and install

``` bash
git clone <repository-url>
cd production-rag-assistant
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment

``` bash
cp .env.dummy .env
```

Populate `.env` locally. Never commit it or real credentials.

### Database

The schema lives in `db/init/001_init.sql`. It enables pgvector and
creates `documents` and `document_chunks`.

Docker Compose automatically executes files mounted into
`/docker-entrypoint-initdb.d` when a **fresh PostgreSQL container data
directory** is initialized. This is PostgreSQL Docker image behavior;
RDS does not know about local repository files.

### Run API

``` bash
uvicorn app.main:app --reload
```

Health check:

``` bash
curl http://localhost:8000/health
```

### Ingest sample document

Place `acme_employee_handbook.pdf` where the runner expects it:

``` bash
python -m app.ingestion.run_ingestion
```

The learning handbook produced 3 pages and 9 chunks. Do not rerun
ingestion casually against the same DB: the current learning pipeline
should not be assumed idempotent/deduplicating.

### Generate missing embeddings

``` bash
python -m app.embeddings.embed_chunks
```

### Query

``` bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"How many vacation days do employees get?"}'
```

## 7. Docker and Compose

Build:

``` bash
docker build -t production-rag-assistant .
```

Run the local stack:

``` bash
docker compose up --build
```

Compose runs API + pgvector PostgreSQL. PostgreSQL is exposed to the
host on `5433` while containers communicate internally on `5432`. A
named volume persists data. The DB health check prevents the API from
racing an unready database.

`.dockerignore` excludes local secrets, virtual environments, Git
metadata, Python caches, and other unnecessary build context.

## 8. Database and provider reliability

The application uses a Psycopg connection pool instead of unbounded new
connections. Development settings included roughly min 2, max 5, pool
wait 5s, and PostgreSQL statement timeout 2s.

Understand the distinction:

-   **Pool timeout:** no connection became available in time.
-   **Statement timeout:** PostgreSQL cancelled a long-running query.
-   **Operational error:** database connectivity/availability problem.

Provider calls use bounded retries with exponential backoff + jitter for
transient failures such as 429, 5xx, network errors, and timeouts.
Permanent request/auth errors such as 400/401/403 should not be blindly
retried. Unlimited retries create latency, cost, loops, and cascading
load.

Internal exceptions are mapped to safe API responses; stack traces,
credentials, and DSNs belong in controlled telemetry, not client
responses.

## 9. Observability

Langfuse trace hierarchy is approximately:

``` text
rag-request
├── retrieval
│   ├── query-embedding
│   │   └── OpenAI embedding
│   └── pgvector-search
└── answer-generation
    └── OpenAI generation
```

One development trace was approximately 3.92s overall, 2.47s retrieval,
2.44s embedding, 0.04s pgvector, and 1.45s generation. The lesson is not
that these are universal timings; it is that tracing showed remote model
calls dominated that request. Production analysis should use
distributions such as p50/p95/p99 over representative traffic.

## 10. Evaluation

The project evaluates retrieval separately from answer generation. The
small handbook set covers annual leave, remote work, learning budget,
expenses, confidential information, and an intentionally unanswerable
car-allowance question.

The small retrieval set achieved strong top-1/top-3 results during
development. That proves those examples passed, not that the system is
globally accurate.

Langfuse dataset experiments included deterministic checks, correctness,
and groundedness. A deliberate unsupported claim about additional
personal days demonstrated that an answer can preserve the correct core
fact while still fail groundedness. A single evaluation metric is
therefore insufficient.

## 11. Tests and CI

Run locally:

``` bash
python -m pytest
ruff check .
ruff format --check .
mypy app
```

The protected `main` branch requires changes through pull requests and
required checks:

``` text
test
integration-test
docker-build
```

Workflow:

``` text
feature branch -> PR -> CI quality gates -> merge to main -> CD
```

A direct push to `main` being rejected is expected behavior, not a Git
failure.

## 12. AWS learning deployment

``` text
GitHub Actions
     |
   OIDC
     v
AWS IAM deployment role
     |
 temporary STS credentials
     |
     +------> ECR (image)
                 |
                 v
Internet ---> ECS/Fargate FastAPI
                 |
               :5432
                 v
          private RDS PostgreSQL + pgvector

ECS startup -> Secrets Manager
ECS logs    -> CloudWatch
API         -> OpenAI + Langfuse
```

### ECR

Stores Docker images. It does not execute them.

### ECS

Container orchestrator. It manages task definitions, tasks, and
services.

### Fargate

Managed compute for ECS. Servers exist, but AWS manages the worker
infrastructure.

### Task definition / task / service

-   **Task definition:** versioned runtime specification: image, CPU,
    memory, ports, secrets, roles, logs, architecture.
-   **Task:** running instance of a task definition.
-   **Service:** maintains desired task count and performs
    replacements/deployments.

### RDS

Managed PostgreSQL. The team still owns schema, indexes, queries,
migrations, data correctness, and capacity decisions.

### Secrets Manager

Stores runtime secret values. ECS task definitions reference secrets
instead of containing secret plaintext.

### CloudWatch

Receives ECS/application logs and is a key runtime debugging surface.

## 13. Networking and security groups

Cost-conscious learning topology:

``` text
Developer public IP /32
        |
      :8000
        v
ECS task SG
        |
      :5432
        v
RDS SG -> private RDS
```

RDS inbound PostgreSQL traffic is allowed from the ECS security group
rather than `0.0.0.0/0`.

For this temporary learning deployment, ECS can run in a public subnet
with a public IP to avoid ALB/NAT costs while inbound API traffic is
restricted to the developer IP. A mature internet-facing production
topology would more commonly be:

``` text
Internet -> HTTPS ALB -> private ECS tasks -> private RDS
```

with controlled outbound connectivity, TLS, multiple AZs/tasks as
required, autoscaling, and stronger monitoring.

Remember:

``` text
IAM             = who can perform AWS API actions
VPC/subnets     = network placement and routing
Security Groups = allowed network traffic
```

## 14. Secrets and ECS startup

Secret runtime keys include:

``` text
DATABASE_URL
OPENAI_API_KEY
LANGFUSE_PUBLIC_KEY
LANGFUSE_SECRET_KEY
```

Non-secret configuration includes `LANGFUSE_BASE_URL` and
`LANGFUSE_TRACING_ENVIRONMENT`.

A previous startup failure occurred because Secrets Manager JSON key
names contained spaces while ECS requested exact keys such as
`OPENAI_API_KEY`. That failure happened during resource initialization,
before application logs existed.

Another failure occurred when the Secrets Manager ARN itself was set as
literal `DATABASE_URL`. Psycopg then tried to parse an ARN as a DSN.
Correct design:

``` text
ECS DATABASE_URL --ValueFrom--> Secrets Manager JSON key --> actual DSN
```

## 15. Schema bootstrap, ingestion, embeddings

Docker Compose initialization does not transfer to RDS. The project
therefore added a one-off runner:

``` bash
python -m app.db.init_schema
```

AWS lifecycle jobs were separated:

``` text
schema bootstrap -> one-off ECS task
PDF ingestion    -> one-off ECS task
embedding        -> one-off ECS task
API              -> long-running ECS service
```

A mature system should use proper versioned migrations such as
Alembic/Flyway or an equivalent deployment migration job.

## 16. IAM roles

### ECS task execution role

Used by ECS infrastructure for operations such as pulling ECR images,
retrieving startup secrets, and writing logs.

### ECS task role

Credentials available to the application if application code itself
needs AWS APIs. This app does not need broad AWS API access, so its task
role can remain absent/minimal.

Least privilege applies to both.

## 17. GitHub OIDC deployment

The deployment does not store long-lived AWS credentials in GitHub.

``` text
GitHub workflow -> OIDC token -> IAM trust policy -> AWS STS
                                               -> temporary credentials
                                               -> ECR/ECS deployment
```

Two IAM concepts must stay separate:

-   **Trust policy:** WHO may assume the deployment role?
-   **Permission policy:** WHAT may that role do after assumption?

The trust relationship is restricted to the intended repository and
`main`. For GitHub repositories using immutable OIDC subjects, the
subject can look like:

``` text
repo:OWNER@OWNER_ID/REPOSITORY@REPOSITORY_ID:ref:refs/heads/main
```

Use the exact subject issued for the repository; never copy example IDs.

The deployment role receives only required actions such as ECR push, ECS
task-definition/service operations, and narrowly scoped `iam:PassRole`.

### OIDC debugging lesson

`sts:AssumeRoleWithWebIdentity` initially returned AccessDenied. The
provider and workflow looked correct, so CloudTrail was inspected.
GitHub's actual immutable OIDC subject did not match the name-only
subject in the role trust policy. The narrow fix is to make the trust
condition match the exact authorized repository/main identity---not to
broaden the role to every repository.

## 18. Immutable deployments and CPU architecture

Images should use the Git commit SHA as the ECR tag:

``` text
Git SHA -> ECR image tag -> ECS task definition revision
```

This improves traceability and rollback compared with a mutable `latest`
tag.

The ECS task definition in this project is ARM64. A normal GitHub
`ubuntu-latest` runner is commonly x86/AMD64, so CD must explicitly
build an ARM64 image, e.g. with Buildx/QEMU:

``` bash
docker buildx build \
  --platform linux/arm64 \
  --push \
  -t "$IMAGE_URI" \
  .
```

Do not deploy an AMD64 image into an ARM64 ECS runtime.

## 19. Deployment verification

After deployment verify progressively:

1.  ECS service reaches a stable running task.
2.  CloudWatch shows expected startup/application logs.
3.  `/health` succeeds.
4.  `/chat` succeeds with a known handbook question.
5.  Answer is grounded and sources are present.
6.  Langfuse receives the production trace if enabled.

A green deployment job is not by itself proof of application health.

## 20. Troubleshooting record

### `vector <=> double precision[]`

PostgreSQL inferred the wrong parameter type. Cast the bound value to
pgvector `vector`.

### ECS DB pool timeout

The one-off task used the wrong/default security group. RDS allowed 5432
only from the intended ECS SG. Explicitly attaching the correct SG fixed
connectivity.

### Secret JSON key missing

The key name in Secrets Manager did not exactly match `OPENAI_API_KEY`.
This was a startup resource-initialization failure, not an OpenAI
authentication failure.

### Psycopg parsing an ARN

`DATABASE_URL` was supplied as a literal Secrets Manager ARN instead of
using ECS `ValueFrom` to inject the actual DSN.

### GitHub OIDC AccessDenied

The role trust policy's expected `sub` did not match GitHub's immutable
OIDC subject. CloudTrail exposed the actual identity.

### Direct push rejected

Branch protection required PR + three status checks. Correct solution:
feature branch -\> PR -\> checks -\> merge; do not disable protection.

## 21. Production improvements

Potential next steps, driven by actual requirements and risk:

-   Alembic migrations
-   idempotent ingestion/document versioning
-   hybrid BM25 + vector retrieval
-   reranking and metadata filtering
-   larger representative/adversarial eval datasets
-   authentication and authorization
-   API rate limiting/backpressure
-   request IDs + true structured JSON logging
-   metrics/SLOs/alerts
-   HTTPS ALB + private ECS
-   Multi-AZ/high availability where required
-   autoscaling and load testing
-   explicit rollback strategy
-   image/dependency security scanning
-   infrastructure as code
-   dev/staging/prod environment strategy

## 22. Terraform: where it fits

Terraform is an Infrastructure-as-Code tool. Instead of manually
creating ECR, ECS, RDS, IAM, networking, and secrets through the
console, infrastructure definitions can be version-controlled, reviewed,
and reproduced.

``` text
Terraform      -> provisions/manages infrastructure
Docker         -> packages application
GitHub Actions -> automates CI/CD
ECR            -> stores images
ECS/Fargate    -> runs containers
RDS            -> stores relational/vector data
```

This project intentionally created AWS resources manually first so each
component could be understood. A future iteration can encode the same
architecture in Terraform.

## 23. Cost and cleanup

This is a temporary learning deployment on an older AWS account without
promotional credits. Remove resources when finished:

-   ECS service/running tasks and cluster
-   ECR images/repository
-   RDS instance and unwanted retained backups/snapshots
-   Secrets Manager secret
-   CloudWatch log groups
-   project security groups
-   deployment IAM roles/policies/OIDC provider if no longer used

Also inspect any region accidentally used during setup as well as
Frankfurt (`eu-central-1`). A budget alert is useful but is **not a hard
spending cap**.

## 24. Interview summary

> I built a production-oriented RAG API using FastAPI,
> PostgreSQL/pgvector and OpenAI. I implemented PDF ingestion,
> section-aware chunking, persisted embeddings, semantic retrieval,
> grounded generation, source attribution, weak-retrieval abstention,
> provider retries, database connection pooling and controlled errors. I
> added Langfuse tracing and dataset-based evaluation, unit/integration
> tests, static quality gates and Docker packaging. CI runs through
> GitHub Actions with protected-branch checks. I deployed the system to
> AWS using ECR, ECS/Fargate, private RDS PostgreSQL with pgvector,
> Secrets Manager and CloudWatch. Deployment uses GitHub OIDC and an IAM
> role rather than long-lived AWS credentials. I debugged real
> deployment failures across Secrets Manager, security groups and OIDC
> using ECS stop reasons, CloudWatch and CloudTrail.

## 25. Core lesson

Production RAG is not merely:

``` text
PDF -> embedding -> LLM
```

It is an engineered system involving data lifecycle, retrieval quality,
failure handling, database reliability, provider reliability,
observability, evaluation, testing, security, secrets, containers,
networking, CI/CD, deployment, cost, and operations.

In interviews, explain **why a layer exists, what can fail there, how
you observe the failure, and what trade-off you made** rather than
reciting service names.
