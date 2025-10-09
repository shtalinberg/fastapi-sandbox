# fastapi-sandbox

## Project Folders

```
repo_root/                     # Project root directory
├── docs/                      # Documentation
│── volumes/                   # Docker volumes files
│── requirements/              # Dependency management
│   ├── base.pip               # Base dependencies
│   ├── code-checks.pip        # Linters and code formatting dependencies
│   └── local.pip              # Local development dependencies
│── sc_backend/                # Source Code for Backend
│   ├── faproject/             # FastAPI application
│   │   ├── alembic/           # Database migrations
│   │   ├── api/                 # FastAPI app API
│   │   │   ├── __init__.py
│   │   │   └── v1/              # API version 1
│   │   │       ├── __init__.py
│   │   │       ├── router.py    # Aggregate all v1 routes
│   │   │       └── endpoints/   # Route handlers
│   │   │           ├── __init__.py
│   │   │           └── products.py    # /products/ CRUD
│   │   ├── db/                  # Database layer
│   │   ├── core/                # FastAPI app core
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py    # Celery configuration
│   │   │   ├── config.py
│   │   ├── middleware/          # Custom middleware
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── repositories/        # Data access layer
│   │   ├── schemas/             # Pydantic schemas (validation)
│   │   ├── services/            # Business logic layer
│   │   ├── tasks/               # Celery tasks
│   │   ├── utils/               # Utility functions
│   │   ├── __init__.py
│   │   ├── alembic.ini
│   │   ├── dependencies.py      # Shared dependencies (f.e. DB session, auth)
│   │   ├── main.py
│   └── tests/                   # Tests directory
│       ├── __init__.py
│       ├── conftest.py          # Pytest fixtures
│       ├── api/                 # API tests
├── scripts/                     # Utility scripts
│── .gitignore
├── .env
├── .env.example
├── pyproject.toml               # Project metadata & tool configs
│── README.md
└── Makefile                     # Common commands
```