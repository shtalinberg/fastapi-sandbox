# FastAPI Sandbox

A REST API service built with FastAPI that provides user authentication, product management, and automatic product synchronization from external APIs.

## Features

### 1. User Authentication
- **User Registration**: Create new user accounts with username, email, and password
- **User Login**: Authenticate users with JWT tokens
- **Role-Based Access Control**: Support for regular users and administrators

### 2. Product Management
- **View Products**: All users (authenticated and anonymous) can view products
- **Create Products**: Only administrators can create new products
- **Update Products**: Only administrators can edit existing products
- **Delete Products**: Only administrators can delete products

### 3. External API Synchronization
- Automatically synchronizes products from an external public API (FakeStore API)
- Periodic synchronization runs every 5 minutes (configurable)
- Prevents duplicate products by tracking external IDs

## Installation

1. Clone the repository:
```bash
git clone https://github.com/shtalinberg/fastapi-sandbox.git
cd fastapi-sandbox
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive API Documentation (Swagger)**: http://localhost:8000/docs
- **Alternative API Documentation (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Authentication

#### Register a New User
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123"
}
```

#### Login
```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=john_doe&password=secure_password123
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Products

#### List All Products (No Authentication Required)
```bash
GET /api/v1/products/
```

#### Get a Specific Product (No Authentication Required)
```bash
GET /api/v1/products/{product_id}
```

#### Create a Product (Admin Only)
```bash
POST /api/v1/products/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "New Product",
  "price": 29.99,
  "description": "Product description",
  "category": "electronics",
  "image": "https://example.com/image.jpg"
}
```

#### Update a Product (Admin Only)
```bash
PUT /api/v1/products/{product_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Updated Product",
  "price": 39.99
}
```

#### Delete a Product (Admin Only)
```bash
DELETE /api/v1/products/{product_id}
Authorization: Bearer {access_token}
```

## Creating an Admin User

By default, registered users are not administrators. To create an admin user, you need to manually update the database after registration:

```python
from app.db.session import SessionLocal
from app.crud.user import get_user_by_username

db = SessionLocal()
user = get_user_by_username(db, "username")
user.is_admin = True
db.commit()
db.close()
```

Alternatively, you can register a user and then use a database management tool to set `is_admin = 1` for that user.

## Configuration

Configuration can be customized in `app/core/config.py`:

- `SECRET_KEY`: Secret key for JWT token generation (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30 minutes)
- `DATABASE_URL`: Database connection string (default: SQLite)
- `EXTERNAL_API_URL`: URL of the external API for product synchronization
- `SYNC_INTERVAL_SECONDS`: Interval between synchronization runs (default: 300 seconds)

## Testing

Run the test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app tests/
```

## Project Structure

```
fastapi-sandbox/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   └── products.py     # Product endpoints
│   │   └── router.py           # API router configuration
│   ├── core/
│   │   ├── config.py           # Application configuration
│   │   ├── security.py         # Security utilities (JWT, password hashing)
│   │   └── deps.py             # Dependencies (authentication, authorization)
│   ├── crud/
│   │   ├── user.py             # User database operations
│   │   └── product.py          # Product database operations
│   ├── db/
│   │   └── session.py          # Database session and initialization
│   ├── models/
│   │   ├── user.py             # User SQLAlchemy model
│   │   └── product.py          # Product SQLAlchemy model
│   ├── schemas/
│   │   ├── user.py             # User Pydantic schemas
│   │   └── product.py          # Product Pydantic schemas
│   ├── tasks/
│   │   └── sync_products.py    # Background task for product synchronization
│   └── main.py                 # FastAPI application entry point
├── tests/
│   ├── conftest.py             # Test configuration and fixtures
│   ├── test_auth.py            # Authentication tests
│   └── test_products.py        # Product tests
├── .gitignore
├── requirements.txt
└── README.md
```

## Technologies Used

- **FastAPI**: Modern web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **JWT**: JSON Web Tokens for authentication
- **Passlib**: Password hashing library
- **HTTPx**: Async HTTP client for external API calls
- **Pytest**: Testing framework
- **Uvicorn**: ASGI server

## Security Notes

- Change the `SECRET_KEY` in production
- Use environment variables for sensitive configuration
- Use HTTPS in production
- Implement rate limiting for API endpoints
- Add input validation and sanitization
- Use a production-grade database (PostgreSQL, MySQL, etc.)

## License

MIT