# python-etl-sql-postgres

## Overview

This project performs a full ETL (Extract, Transform, Load) pipeline using Python to migrate data from the AdventureWorks2022 SQL Server database to the AW_Sales PostgreSQL database. It includes:

- Creating a PostgreSQL database and user
- Granting full table-level permissions
- Creating tables that mirror the AdventureWorks2022 schema
- Extracting data from SQL Server
- Inserting transformed data into PostgreSQL

## 🛠️ Prerequisites

### 🔧 Tools & Libraries

- Python 3.8+
- PostgreSQL 13+
- SQL Server (with AdventureWorks2022 installed)
- Required Python packages:

  ```bash
  pdm add psycopg2
  pdm add pyodbc
  pdm add python-dotenv
  ```

### 📂 Environment Setup

Ensure the following environment variables are set or configure them in a `.env` file:

```ini
# SQL Server
SQL_SERVER=your_sql_server_host
SQL_DATABASE=AdventureWorks2022
SQL_USER=your_sql_user
SQL_PASSWORD=your_sql_password

# PostgreSQL
PG_HOST=localhost
PG_PORT=5432
PG_DATABASE=adventureworks_pg
PG_USER=etl_user
PG_PASSWORD=secure_password
```

---

## 🧱 Database Initialization

### 🐘 PostgreSQL Setup

The script performs the following:

- Creates a new PostgreSQL database: `adventureworks_pg`
- Creates a user: `etl_user`
- Grants the following permissions on all tables:
  - CONNECT
  - SELECT
  - INSERT
  - UPDATE
  - DELETE

### 📜 SQL Snippet (Executed via Python)

```sql
CREATE DATABASE adventureworks_pg;

CREATE USER etl_user WITH PASSWORD 'secure_password';

GRANT CONNECT ON DATABASE adventureworks_pg TO etl_user;

-- After tables are created:
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO etl_user;
```

---

## 🗂️ Table Creation

Tables are created in PostgreSQL to match the AdventureWorks2022 schema. This includes:

- `Person.Person`
- `HumanResources.Employee`
- `Sales.Customer`
- `Production.Product`
- ...and others as needed

The schema is defined using SQLAlchemy ORM or raw DDL statements.

Example (SQLAlchemy):

```python
from sqlalchemy import Table, Column, Integer, String, MetaData

metadata = MetaData()

person = Table('Person', metadata,
    Column('BusinessEntityID', Integer, primary_key=True),
    Column('FirstName', String),
    Column('LastName', String),
    # Add other columns...
)
```

## 🔄 ETL Workflow

### 1. 🧪 Extract

Connect to SQL Server using `pyodbc` and query data from AdventureWorks2022.

```python
import pyodbc
conn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=...;DATABASE=...;UID=...;PWD=...")
df = pd.read_sql("SELECT * FROM Person.Person", conn)
```

### 2. 🔧 Transform

Clean or reformat data if needed (e.g., date formats, null handling).

### 3. 📥 Load

Insert data into PostgreSQL using `psycopg2` or `SQLAlchemy`.

```python
from sqlalchemy import create_engine
engine = create_engine("postgresql+psycopg2://etl_user:secure_password@localhost:5432/adventureworks_pg")
df.to_sql('Person', engine, if_exists='append', index=False)
```

## 🚀 Running the Project

```bash
python etl_adventureworks.py
```

This script will:

1. Connect to both databases
2. Create the PostgreSQL schema
3. Extract data from SQL Server
4. Insert it into PostgreSQL

## 📁 Project Structure

```plaintext
├── etl_adventureworks.py
├── db_setup.py
├── models/
│   └── tables.py
├── .env
├── README.md
```

## ✅ Permissions Recap

| Permission | Scope         | Granted To |
|------------|---------------|------------|
| CONNECT    | Database      | `etl_user` |
| SELECT     | All Tables    | `etl_user` |
| INSERT     | All Tables    | `etl_user` |
| UPDATE     | All Tables    | `etl_user` |
| DELETE     | All Tables    | `etl_user` |

## 📌 Notes

- Ensure SQL Server allows remote connections and the firewall permits access.
- Use `pgAdmin` or `psql` to verify table creation and data insertion.
- Consider batching inserts for large tables to improve performance.
