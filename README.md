
# LLM-Powered Text-to-SQL Analytics Assistant

An end-to-end analytics assistant that converts natural-language business questions into safe, executable PostgreSQL queries and returns structured analytical results.

## Problem Statement

Business users often need analytical insights but may not know SQL.

This project provides a natural-language interface that allows users to ask business questions in plain English and receive validated SQL queries and analytical results from a PostgreSQL analytics database.

## Architecture

```text
Natural Language Question
          ↓
Question Analysis
          ↓
Schema Linking
          ↓
Focused Schema Context
          ↓
Business Metrics + Few-Shot Prompting
          ↓
LLM / Mock Provider
          ↓
SQL Validation
          ↓
Query Cost Guard
          ↓
PostgreSQL
          ↓
Query Results
          ↓
FastAPI / Streamlit
```

## Key Features

- Natural-language to SQL generation
- Schema-aware SQL generation
- Schema linking and focused schema context
- Few-shot SQL prompting
- Business metric definitions
- SQL validation and safety checks
- Table and column allowlisting
- Query cost protection and statement timeouts
- Conversation-aware follow-up questions
- SQL retry using previous error feedback
- FastAPI REST API
- Streamlit analytics interface
- Docker and Docker Compose deployment
- GitHub Actions CI
- Automated testing and golden evaluation

## Tech Stack

| Category | Technologies |
|---|---|
| Language | Python 3.11 |
| Database | PostgreSQL 18, SQL |
| Backend | FastAPI, Uvicorn, Pydantic |
| Analytics | Pandas |
| Visualization | Streamlit, Matplotlib |
| Text-to-SQL | LLM, Few-Shot Prompting, Schema Linking |
| SQL Validation | SQLGlot |
| Testing | Pytest, HTTPX |
| Deployment | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Version Control | Git |
| Configuration | python-dotenv |

## Database Design

The project uses a PostgreSQL analytics star schema.

### Dimension Tables

- `dim_date`
- `dim_customer`
- `dim_product`
- `dim_seller`
- `dim_order_status`
- `dim_payment_type`

### Fact Tables

- `fact_orders`
- `fact_order_items`
- `fact_payments`
- `fact_reviews`

## Text-to-SQL Pipeline

```text
User Question
      ↓
Question Analyzer
      ↓
Schema Linker
      ↓
Focused Schema
      ↓
Business Metrics + Few-Shot Examples
      ↓
LLM Provider
      ↓
Generated SQL
      ↓
SQL Validator
      ↓
Query Cost Guard
      ↓
PostgreSQL
      ↓
Structured Results
```

## SQL Safety

Generated SQL is validated before execution.

- SELECT-only query enforcement
- Single-statement enforcement
- PostgreSQL SQL parsing
- Analytics schema restrictions
- Table allowlisting
- Column allowlisting
- Scope-aware SQL validation
- Query cost protection
- PostgreSQL statement timeouts
- Result-size protection

## API

The project provides a FastAPI REST API.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API status |
| GET | `/health` | Health check |
| POST | `/api/query` | Generate and execute SQL |
| POST | `/api/conversation/clear` | Clear conversation context |

### Example

**User question:**

> What are the total sales?

**Generated SQL:**

```sql
SELECT
    SUM(price) AS total_sales
FROM analytics.fact_order_items;
```

**Example result:**

| total_sales |
|---:|
| 13591643.70 |

*The result above is an example; actual results depend on the database contents.*

## Streamlit Interface

The project includes a Streamlit interface for interactive analytics.

Users can:

- Ask natural-language business questions
- View generated SQL
- View query results
- Visualize suitable analytical results
- Continue conversations with follow-up questions

## Testing and Evaluation

The project includes automated unit, integration, API, validation, visualization, and golden-query evaluation tests.

**Latest recorded results:**

- 129 automated tests passing
- 11/11 golden evaluation cases passing

## Docker

The API is containerized using Docker Compose. Before starting the API, ensure that PostgreSQL is running, the `text-to-sql-ci-postgres` container is reachable from the Compose network, and the `.env` file contains valid database credentials.

Build and start the API:

```powershell
docker compose up -d --build
docker compose ps
```

Access the API at:

- API: [http://localhost:8000](http://localhost:8000)
- Interactive API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

Note: The current Compose configuration does not create the PostgreSQL container automatically.

## CI/CD

GitHub Actions automates the CI workflow, including:

- Setting up Python
- Installing project dependencies
- Starting PostgreSQL
- Running the automated test suite

## Project Structure

```text
TextToSQL-Assistant/
│
├── api/
├── app/
├── core/
├── config/
├── tests/
├── sql/
├── data/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone the Repository

```powershell
git clone https://github.com/AkshatGit-1/TextToSQL-Assistant.git
cd TextToSQL-Assistant
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a local `.env` file using `.env.example` as the template.

Configure the PostgreSQL connection details and required LLM provider settings. Never commit your `.env` file or database credentials.

### 5. Run the Tests

```powershell
pytest -q
```

### 6. Start the API

```powershell
uvicorn api.main:app --reload
```

### 7. Start the Streamlit Interface

Open a separate terminal, activate the virtual environment, and run:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app/streamlit_app.py
```

Ensure PostgreSQL is running, the analytics schema is initialized, and your environment variables match the database configuration before making queries.

## Technologies

`#Python` `#PostgreSQL` `#SQL` `#FastAPI` `#Pandas` `#Streamlit` `#SQLGlot` `#Docker` `#GitHubActions` `#LLM` `#TextToSQL` `#GenerativeAI` `#DataAnalytics` `#AnalyticsEngineering`

## Author

**Akshat Vishnoi**

B.Tech — Computer Science & Engineering

GitHub: [AkshatGit-1](https://github.com/AkshatGit-1)
