# Book Library Management System (FastAPI)

A book library management system built with FastAPI, PostgreSQL, and SQLAlchemy 2.0.

## Features
- **Authentication**: JWT-based auth (Register/Login/Me).
- **CRUD Operations**: Manage personal Books, Authors, and Categories.
- **Security**: Each user manages only their own data.
- **Pagination & Filtering**: Advanced search and filtering for books.
- **API Documentation**: Interactive Swagger UI at `/docs`.

## Tech Stack
- **Python 3.11+**
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy 2.0** (Declarative Mapping)
- **Alembic** (Migrations)
- **Pydantic v2** (Validation)
- **JWT** (Authentication)

## Project Structure (MVC)
- **Models**: `app/models/` (SQLAlchemy models)
- **Views/Schemas**: `app/schemas/` (Pydantic validation)
- **Controllers/Routes**: `app/routes/` (API endpoints)

## Setup Instructions

### 1. Database Setup (PostgreSQL)
Ensure you have PostgreSQL running. You can run it via Docker:
```bash
docker run --name lib-pg -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16
```

Create the database:
```sql
CREATE DATABASE book_library;
```

### 2. Environment Variables
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/book_library
SECRET_KEY=your_very_secret_key_here
ALGORITHM=HS256
```

### 3. Installation
Using `uv` (recommended):
```bash
# Sync dependencies and create venv
uv sync
```
If you don't have `uv` installed, you can use `pip` to install the dependencies from `pyproject.toml`:
```bash
pip install .
```

### 4. Database Migrations
Generate the initial migration based on the models:
```bash
uv run alembic revision --autogenerate -m "initial schema"
```

Apply the migrations to create the tables in PostgreSQL:
```bash
uv run alembic upgrade head
```

### 5. Start the Server
```bash
uv run uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.
Visit `http://localhost:8000/docs` for the interactive documentation.

## Design Choice: JWT over Sessions
I chose **JWT (JSON Web Tokens)** for authentication because it allows the API to be stateless. This makes the system more scalable as the server doesn't need to store session data in memory or a database. The client simply sends the token in the `Authorization` header, and the server validates it using a secret key.

## SQLAlchemy 2.0 Style
The project uses the modern **SQLAlchemy 2.0 declarative style** with `Mapped` and `mapped_column` type annotations. This provides better IDE support, type safety, and is the current industry standard for SQLAlchemy projects.
