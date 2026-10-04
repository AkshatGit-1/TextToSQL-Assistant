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
Few-Shot Prompting
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

---

## 4. Key Features

```markdown
## Key Features

- Natural language → SQL generation
- Schema-aware SQL generation
- Schema linking and focused schema context
- Few-shot SQL prompting
- Business metric definitions
- SQL validation and safety checks
- Table and column allowlisting
- Query cost protection and statement timeout
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

## Database

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
Result

---

## 8. SQL Safety

```markdown
## SQL Safety

Generated SQL is validated before execution.

- SELECT-only queries
- Single-statement enforcement
- PostgreSQL SQL parsing
- Analytics schema restriction
- Table allowlisting
- Column allowlisting
- Scope-aware SQL validation
- Query cost guard
- PostgreSQL statement timeout
- Result-size protection

## API

The project provides a FastAPI REST API.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API status |
| GET | `/health` | Health check |
| POST | `/api/query` | Generate and execute SQL |
| POST | `/api/conversation/clear` | Clear conversation context |

## Example

### User Question

```text
What are the total sales?

SELECT
    SUM(price) AS total_sales
FROM analytics.fact_order_items;

total_sales
-----------
13591643.70

---

## 11. Streamlit

```markdown
## Streamlit Interface

The project includes a Streamlit interface for interactive analytics.

Users can:

- Ask natural-language business questions
- View generated SQL
- View query results
- Visualize suitable analytical results
- Continue conversations with follow-up questions

## Testing & Evaluation

The project includes automated unit, integration, API, validation, visualization, and golden evaluation tests.

```text
129 automated tests passing
11/11 golden evaluation cases passing

---

## 13. Docker

```markdown
## Docker

The application is containerized using Docker.

```bash
docker compose up -d --build

http://localhost:8000

---

## 14. CI/CD

```markdown
## CI/CD

GitHub Actions is configured to automatically:

- Set up Python
- Install project dependencies
- Start PostgreSQL
- Run the automated test suite

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

---

## 16. Setup

```markdown
## Setup

### Clone the repository

```bash
git clone <your-repository-url>
cd TextToSQL-Assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
pytest -q
uvicorn api.main:app --reload
streamlit run app/streamlit_app.py

---

## 17. Docker Run

```markdown
## Docker Run

```bash
docker compose up -d --build
docker compose ps

---

## 18. Technologies / Hashtags

```markdown
## Technologies

#Python #PostgreSQL #SQL #FastAPI #Uvicorn #Pydantic #Pandas #Streamlit #Matplotlib #SQLGlot #Pytest #HTTPX #Docker #DockerCompose #GitHubActions #Git #LLM #TextToSQL #GenerativeAI #DataAnalytics #AnalyticsEngineering #API #NaturalLanguageProcessing

## Author

**Akshat Vishnoi**

B.Tech — Computer Science & Engineering
