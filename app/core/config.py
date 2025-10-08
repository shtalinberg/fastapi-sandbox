from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Sandbox"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # External API
    EXTERNAL_API_URL: str = "https://fakestoreapi.com/products"
    SYNC_INTERVAL_SECONDS: int = 300  # 5 minutes
    
    class Config:
        case_sensitive = True


settings = Settings()
