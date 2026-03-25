# BuyerForeSight — User Management REST API

Enterprise-grade User Management API built with **FastAPI** + **SQLite** (async).

---

## Tech Stack

| Layer       | Choice                        |
|-------------|-------------------------------|
| Framework   | FastAPI 0.111                 |
| Language    | Python 3.11+                  |
| Database    | SQLite via SQLAlchemy (async) |
| Validation  | Pydantic v2                   |
| Testing     | Pytest + httpx                |
| Deployment  | Railway / Render              |

---

## Project Structure

```
buyerforesight-api/
├── app/
│   ├── api/v1/
│   │   └── endpoints/
│   │       └── users.py          # Route handlers
│   ├── core/
│   │   ├── config.py             # Env-based settings
│   │   └── logging.py            # Structured logger
│   ├── db/
│   │   └── database.py           # Async SQLAlchemy engine
│   ├── middleware/
│   │   ├── exception_handlers.py # Global error handling
│   │   └── request_logger.py     # Per-request timing logs
│   ├── models/
│   │   └── user.py               # SQLAlchemy ORM model
│   ├── schemas/
│   │   └── user.py               # Pydantic schemas (request/response)
│   ├── services/
│   │   ├── user_repository.py    # Data access layer
│   │   └── user_service.py       # Business logic layer
│   ├── utils/
│   │   └── seeder.py             # DB seed with 15 users
│   └── main.py                   # App factory
├── tests/
│   ├── conftest.py               # Fixtures & test DB
│   └── test_users.py             # 32 integration tests
├── data/                         # SQLite DB stored here (gitignored)
├── logs/                         # Log output directory
├── main.py                       # Uvicorn entry point
├── Procfile                      # Heroku/Railway process file
├── railway.json                  # Railway deployment config
├── render.yaml                   # Render deployment config
├── requirements.txt
├── pytest.ini
└── .env
```

---

## API Endpoints

| Method | Path              | Description                           |
|--------|-------------------|---------------------------------------|
| GET    | /api/v1/users     | List users (search, sort, paginate)   |
| GET    | /api/v1/users/:id | Get user by ID                        |
| POST   | /api/v1/users     | Create a new user                     |
| PUT    | /api/v1/users/:id | Update an existing user               |
| DELETE | /api/v1/users/:id | Delete a user                         |
| GET    | /health           | Health check                          |
| GET    | /docs             | Interactive Swagger UI                |

### Query Parameters for GET /api/v1/users

| Param      | Type    | Description                              | Example              |
|------------|---------|------------------------------------------|----------------------|
| search     | string  | Search name, email, or department        | `?search=alice`      |
| sort       | string  | Sort field: name, email, department, created_at | `?sort=name`  |
| order      | string  | asc or desc                              | `?order=desc`        |
| page       | int     | Page number (default: 1)                 | `?page=2`            |
| limit      | int     | Items per page, max 100 (default: 10)    | `?limit=20`          |
| role       | string  | Filter by role: admin, manager, employee, viewer | `?role=admin` |
| is_active  | bool    | Filter by active status                  | `?is_active=true`    |

---

## Response Format

All responses follow a consistent envelope:

```json
{
  "success": true,
  "message": "Users retrieved successfully",
  "data": { ... },
  "timestamp": "2024-01-01T12:00:00+00:00"
}
```

Error responses:

```json
{
  "success": false,
  "message": "User with id '...' not found",
  "timestamp": "2024-01-01T12:00:00+00:00"
}
```

---

## Running Locally

### Prerequisites
- Python 3.11 or higher
- pip

### Steps

```bash
# 1. Clone / unzip the project
cd buyerforesight-api

# 2. Create and activate virtual environment
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- **API Base**: http://localhost:8000/api/v1/users
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health**: http://localhost:8000/health

The database is auto-created and seeded with 15 users on first startup.

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run a specific test class
pytest tests/test_users.py::TestCreateUser -v
```

---

## Deploying to Railway

1. Push your project to a GitHub repository.
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**.
3. Select your repository. Railway auto-detects `railway.json`.
4. Add the following environment variables in Railway dashboard:
   - `DATABASE_URL` = `sqlite+aiosqlite:///./data/users.db`
   - `ENVIRONMENT` = `production`
   - `LOG_LEVEL` = `INFO`
5. Deploy — Railway assigns a public URL automatically.

---

## Deploying to Render

1. Push your project to a GitHub repository.
2. Go to [render.com](https://render.com) → **New** → **Web Service** → connect your repo.
3. Render auto-detects `render.yaml`.
4. The build command (`pip install -r requirements.txt`) and start command (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`) are pre-configured.
5. Click **Create Web Service** — Render assigns a public URL automatically.

---

## Sample Requests

### Create a user
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "role": "employee",
    "department": "Engineering",
    "phone": "+91-9876543210"
  }'
```

### List users with search and sort
```bash
curl "http://localhost:8000/api/v1/users?search=alice&sort=name&order=asc"
```

### Update a user
```bash
curl -X PUT http://localhost:8000/api/v1/users/<user-id> \
  -H "Content-Type: application/json" \
  -d '{"role": "admin", "is_active": true}'
```

### Delete a user
```bash
curl -X DELETE http://localhost:8000/api/v1/users/<user-id>
```
