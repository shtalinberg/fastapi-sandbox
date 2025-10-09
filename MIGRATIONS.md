# Database Migration Guide

This project uses Alembic for database schema migrations.

## Common Commands

### Development Workflow

1. **Create a new migration** (after changing models):
   ```bash
   docker compose exec web_app alembic revision --autogenerate -m "Description of changes"
   ```

2. **Apply migrations**:
   ```bash
   docker compose exec web_app alembic upgrade head
   ```

3. **Check current migration status**:
   ```bash
   docker compose exec web_app alembic current
   ```

4. **See migration history**:
   ```bash
   docker compose exec web_app alembic history
   ```

5. **Rollback to previous migration**:
   ```bash
   docker compose exec web_app alembic downgrade -1
   ```

### Database Utilities

We have a utility script for common database operations:

1. **Show database status**:
   ```bash
   docker compose exec web_app python db_utils.py status
   ```

2. **Create sample data**:
   ```bash
   docker compose exec web_app python db_utils.py create-sample-data
   ```

## Migration Files

Migration files are stored in `alembic/versions/` and contain:
- `upgrade()` function: applies changes
- `downgrade()` function: reverts changes

### File Naming Convention
Migration files use timestamp-based naming: `YYYY_MM_DD_HHMM-{revision_id}_{description}.py`

Example: `2025_10_08_2322-916e3ab6866c_add_user_profile_table.py`

### Code Formatting
Migration files are automatically formatted with Black (line length: 88 characters) during generation.

## Current Schema

### Users Table
- `id`: Primary key (auto-increment)
- `email`: Unique email address
- `password`: Hashed password
- `role`: User role (admin/user)
- `created_at`: Timestamp
- `updated_at`: Timestamp

### Products Table
- `id`: Primary key (auto-increment)
- `title`: Product name
- `description`: Product description
- `price`: Product price (decimal)
- `external_id`: External API identifier (unique)
- `height`, `length`, `depth`: Product dimensions
- `owner_id`: Foreign key to users table
- `created_at`: Timestamp
- `updated_at`: Timestamp

## Environment Setup

The database connection is configured in `core/config.py`:
- `DATABASE_URL`: Sync connection (for compatibility)
- `ASYNC_DATABASE_URL`: Async connection (for FastAPI)

Database URL format: `postgresql+psycopg://user:pass@host:port/dbname`