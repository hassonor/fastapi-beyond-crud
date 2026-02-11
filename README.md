# 🚀 FastAPI Beyond CRUD
## Advanced FastAPI Patterns & Production Best Practices

<div align="center">

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-%3E%3D3.11-blue)
![FastAPI](https://img.shields.io/badge/fastapi-%3E%3D0.109.0-green)
![PostgreSQL](https://img.shields.io/badge/postgresql-15+-blue)

**A production-ready FastAPI application demonstrating advanced patterns beyond basic CRUD**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Patterns](#-advanced-patterns)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Advanced Patterns](#-advanced-patterns)
- [Database Migrations](#-database-migrations-with-alembic)
- [Testing](#-testing)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Best Practices](#-best-practices)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**FastAPI Beyond CRUD** goes beyond basic create-read-update-delete operations to showcase **production-grade FastAPI development**. This project demonstrates advanced patterns including dependency injection, repository pattern, async database operations, background tasks, caching, authentication, and comprehensive testing.

### Why This Project?

- ✅ **Production Patterns**: Repository pattern, service layer, dependency injection
- ✅ **Async Everything**: AsyncIO, async database operations, async testing
- ✅ **Type Safety**: Pydantic v2, type hints, runtime validation
- ✅ **Database Migrations**: Alembic with async support
- ✅ **Authentication**: JWT with refresh tokens, OAuth2
- ✅ **Testing**: pytest, async fixtures, test coverage > 90%
- ✅ **Educational**: Clean architecture, SOLID principles, comprehensive docs

---

## ✨ Features

### Core Functionality
- 🔐 **JWT Authentication**: Access/refresh tokens with OAuth2
- 👤 **User Management**: Registration, profiles, roles, permissions
- 📧 **Email Service**: Async email sending with templates
- 🗄️ **Advanced Queries**: Filtering, sorting, pagination, search
- 📊 **Analytics**: Aggregations, statistics, reporting
- 🔄 **Background Tasks**: Celery integration, scheduled jobs
- 💾 **Caching**: Redis caching with TTL strategies

### Technical Features
- 🎯 **Repository Pattern**: Clean separation of data access
- 🏗️ **Service Layer**: Business logic isolation
- 💉 **Dependency Injection**: FastAPI's built-in DI system
- 🔍 **Full-Text Search**: PostgreSQL full-text search
- 📝 **Request Validation**: Pydantic v2 models with custom validators
- 🚨 **Error Handling**: Custom exceptions, structured errors
- 📊 **Observability**: Logging, metrics, health checks
- 🧪 **100% Typed**: Full type coverage with mypy strict mode

---

## 🛠 Tech Stack

### Backend Framework
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Programming language |
| **FastAPI** | 0.109+ | Modern web framework |
| **Pydantic** | 2.x | Data validation |
| **SQLAlchemy** | 2.x | Async ORM |
| **Alembic** | 1.x | Database migrations |

### Database & Cache
| Technology | Version | Purpose |
|------------|---------|---------|
| **PostgreSQL** | 15+ | Primary database |
| **Redis** | 7.x | Caching & sessions |
| **asyncpg** | Latest | Async PostgreSQL driver |

### Testing & Quality
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **coverage** - Code coverage
- **mypy** - Static type checking
- **ruff** - Fast Python linter
- **black** - Code formatter

### DevOps
- **Docker** & **Docker Compose** - Containerization
- **Uvicorn** - ASGI server
- **Gunicorn** - Process manager (production)

---

## 🏗 Architecture

### Layered Architecture Diagram

```
┌────────────────────────────────────────────────────┐
│              API Layer (FastAPI)                    │
│  ┌──────────────┐  ┌──────────────┐               │
│  │   Routes     │  │  Schemas     │               │
│  │ (Endpoints)  │  │ (Pydantic)   │               │
│  └──────┬───────┘  └──────────────┘               │
│         │                                          │
└─────────┼──────────────────────────────────────────┘
          │ Dependency Injection
          ▼
┌────────────────────────────────────────────────────┐
│           Service Layer (Business Logic)           │
│  ┌──────────────┐  ┌──────────────┐               │
│  │  Services    │  │  Validators  │               │
│  └──────┬───────┘  └──────────────┘               │
│         │                                          │
└─────────┼──────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────┐
│        Repository Layer (Data Access)              │
│  ┌──────────────┐  ┌──────────────┐               │
│  │Repositories  │  │   Models     │               │
│  │(SQLAlchemy)  │  │ (ORM Models) │               │
│  └──────┬───────┘  └──────────────┘               │
│         │                                          │
└─────────┼──────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────┐
│            Database Layer                          │
│  ┌──────────────┐  ┌──────────────┐               │
│  │ PostgreSQL   │  │    Redis     │               │
│  │  (asyncpg)   │  │  (aioredis)  │               │
│  └──────────────┘  └──────────────┘               │
└────────────────────────────────────────────────────┘
```

### Request Flow Example

```
1. Client Request
   └─▶ GET /api/users?limit=10&offset=0

2. API Layer (Route)
   ├─▶ Validate query parameters (Pydantic)
   ├─▶ Check authentication (JWT)
   └─▶ Inject dependencies (UserService)

3. Service Layer
   ├─▶ Apply business logic
   ├─▶ Check permissions
   └─▶ Call repository

4. Repository Layer
   ├─▶ Build SQLAlchemy query
   ├─▶ Execute async query
   └─▶ Return domain models

5. Response
   ├─▶ Convert to Pydantic schema
   ├─▶ Serialize to JSON
   └─▶ Return HTTP 200 with data
```

---

## 🚀 Quick Start

Get the application running in **5 minutes**:

### Prerequisites

- **Python** >= 3.11
- **Docker** & **Docker Compose** (recommended)
- **PostgreSQL** 15+ (if running locally)
- **Redis** 7+ (if running locally)

### Installation

#### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/hassonor/fastapi-beyond-crud.git
cd fastapi-beyond-crud

# 2. Start services (PostgreSQL, Redis, FastAPI)
docker-compose up -d

# 3. Run migrations
docker-compose exec api alembic upgrade head

# 4. Access the API
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Redoc: http://localhost:8000/redoc
```

#### Option 2: Local Development

```bash
# 1. Clone the repository
git clone https://github.com/hassonor/fastapi-beyond-crud.git
cd fastapi-beyond-crud

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 5. Start PostgreSQL and Redis (if not using Docker)
# PostgreSQL: postgresql://user:pass@localhost:5432/fastapi_db
# Redis: redis://localhost:6379

# 6. Run migrations
alembic init -t async migrations
alembic revision --autogenerate -m "init"
alembic upgrade head

# 7. Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access: http://localhost:8000/docs
```

---

## 📁 Project Structure

```
fastapi-beyond-crud/
├── app/                          # Application source code
│   ├── api/                      # API layer
│   │   ├── dependencies/         # FastAPI dependencies
│   │   │   ├── auth.py          # Auth dependencies
│   │   │   ├── database.py      # DB session dependency
│   │   │   └── pagination.py   # Pagination dependency
│   │   │
│   │   ├── routes/              # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── users.py         # User CRUD endpoints
│   │   │   └── health.py        # Health check endpoint
│   │   │
│   │   └── schemas/             # Pydantic models
│   │       ├── auth.py          # Auth schemas
│   │       ├── user.py          # User schemas
│   │       └── pagination.py   # Pagination schemas
│   │
│   ├── core/                    # Core application config
│   │   ├── config.py            # Settings (Pydantic Settings)
│   │   ├── security.py          # JWT, password hashing
│   │   ├── logging.py           # Logging configuration
│   │   └── exceptions.py        # Custom exceptions
│   │
│   ├── db/                      # Database layer
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── base.py          # Base model with common fields
│   │   │   ├── user.py          # User model
│   │   │   └── __init__.py
│   │   │
│   │   ├── repositories/        # Repository pattern
│   │   │   ├── base.py          # Generic repository
│   │   │   ├── user.py          # User repository
│   │   │   └── __init__.py
│   │   │
│   │   └── session.py           # Async session factory
│   │
│   ├── services/                # Business logic layer
│   │   ├── auth.py              # Auth service
│   │   ├── user.py              # User service
│   │   ├── email.py             # Email service
│   │   └── cache.py             # Caching service
│   │
│   ├── utils/                   # Utility functions
│   │   ├── email_templates.py  # Email HTML templates
│   │   ├── validators.py       # Custom validators
│   │   └── helpers.py          # Helper functions
│   │
│   └── main.py                  # FastAPI application entry point
│
├── migrations/                  # Alembic migrations
│   ├── versions/                # Migration files
│   ├── env.py                   # Alembic environment
│   └── script.py.mako           # Migration template
│
├── tests/                       # Test suite
│   ├── conftest.py              # Pytest fixtures
│   ├── unit/                    # Unit tests
│   │   ├── test_services.py
│   │   └── test_repositories.py
│   ├── integration/             # Integration tests
│   │   └── test_api.py
│   └── fixtures/                # Test data fixtures
│
├── .env.example                 # Environment variables template
├── .gitignore
├── docker-compose.yml           # Docker services
├── Dockerfile                   # FastAPI container
├── pyproject.toml               # Python project config
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
└── README.md
```

---

## 🎯 Advanced Patterns

### 1. Repository Pattern

```python
# app/db/repositories/base.py
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: int) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create(self, data: dict) -> ModelType:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: int, data: dict) -> Optional[ModelType]:
        instance = await self.get(id)
        if not instance:
            return None

        for key, value in data.items():
            setattr(instance, key, value)

        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: int) -> bool:
        instance = await self.get(id)
        if not instance:
            return False

        await self.session.delete(instance)
        await self.session.commit()
        return True
```

### 2. Service Layer with Dependency Injection

```python
# app/services/user.py
from fastapi import Depends
from app.db.repositories.user import UserRepository
from app.db.session import get_session
from app.core.security import get_password_hash, verify_password

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, email: str, password: str, name: str):
        # Business logic validation
        existing_user = await self.repository.get_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")

        # Hash password
        hashed_password = get_password_hash(password)

        # Create user
        user = await self.repository.create({
            "email": email,
            "hashed_password": hashed_password,
            "name": name
        })

        return user

# Dependency injection
async def get_user_service(
    session: AsyncSession = Depends(get_session)
) -> UserService:
    repository = UserRepository(session)
    return UserService(repository)
```

### 3. Pydantic v2 Schemas with Validators

```python
# app/api/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=100)

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    created_at: datetime
    is_active: bool

    model_config = {
        "from_attributes": True  # Pydantic v2 config
    }

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
```

### 4. JWT Authentication with Refresh Tokens

```python
# app/core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# app/api/routes/auth.py
@router.post("/login")
async def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    user = await user_service.authenticate(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
```

### 5. Async Caching with Redis

```python
# app/services/cache.py
import json
from typing import Optional, Any
import aioredis
from app.core.config import settings

class CacheService:
    def __init__(self):
        self.redis = aioredis.from_url(settings.REDIS_URL)

    async def get(self, key: str) -> Optional[Any]:
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        await self.redis.set(key, json.dumps(value), ex=ttl)

    async def delete(self, key: str):
        await self.redis.delete(key)

# Usage in route
@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    cache: CacheService = Depends(get_cache_service)
):
    # Try cache first
    cached_user = await cache.get(f"user:{user_id}")
    if cached_user:
        return cached_user

    # Fetch from database
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Cache for 1 hour
    await cache.set(f"user:{user_id}", user.dict(), ttl=3600)

    return user
```

---

## 🗄️ Database Migrations with Alembic

### Initialize Alembic (Already Done)

```bash
# 1. Initialize async Alembic
alembic init -t async migrations

# 2. Create initial migration
alembic revision --autogenerate -m "initial migration"

# 3. Apply migration
alembic upgrade head
```

### Common Migration Commands

```bash
# Create new migration
alembic revision --autogenerate -m "add users table"

# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

### Example Migration File

```python
# migrations/versions/001_create_users_table.py
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade() -> None:
    op.drop_index('idx_users_email')
    op.drop_table('users')
```

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_services.py

# Run in watch mode
pytest-watch
```

### Example Test

```python
# tests/integration/test_auth.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "Password123!",
            "name": "Test User"
        })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First register
        await client.post("/api/auth/register", json={
            "email": "login@example.com",
            "password": "Password123!",
            "name": "Login Test"
        })

        # Then login
        response = await client.post("/api/auth/login", data={
            "username": "login@example.com",
            "password": "Password123!"
        })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
```

---

## 📚 API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🎯 Best Practices

### ✅ DO:
- Use Pydantic v2 models for validation
- Implement repository pattern for data access
- Use dependency injection for services
- Add type hints everywhere (`mypy --strict`)
- Write async code consistently
- Use Alembic for database migrations
- Cache frequently accessed data (Redis)
- Implement proper error handling
- Write comprehensive tests (>90% coverage)
- Use environment variables for configuration

### ❌ DON'T:
- Mix sync and async code
- Put business logic in routes
- Access database directly from routes
- Store passwords in plain text
- Skip input validation
- Ignore type checking warnings
- Use `SELECT *` queries
- Forget to add indexes
- Skip database migrations
- Hardcode configuration values

---

## 🚢 Deployment

### Production Deployment

```bash
# Build Docker image
docker build -t fastapi-app:latest .

# Run with Gunicorn + Uvicorn workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by [Or Hasson](https://github.com/hassonor)**

⭐ Star this repo if you're learning FastAPI!

</div>
