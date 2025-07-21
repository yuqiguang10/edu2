from typing import Any, Dict, Optional, List
from pydantic import BaseSettings, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Basic
    PROJECT_NAME: str = "K12智能教育平台"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str
    DATABASE_TEST_URL: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [
        ".jpg", ".jpeg", ".png", ".gif", ".pdf", 
        ".doc", ".docx", ".txt", ".mp4", ".mp3"
    ]
    
    # AI Integration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_MODEL_PROVIDER: str = "openai"
    
    # External Services
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Development
    DEBUG: bool = False
    TESTING: bool = False
    
    # Superuser
    FIRST_SUPERUSER: str = "admin@edu-platform.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123456"
    # AI配置
    AI_MODEL_PROVIDER: str = os.getenv("AI_MODEL_PROVIDER", "openai")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # AI Agent配置
    AI_AGENT_TIMEOUT: int = int(os.getenv("AI_AGENT_TIMEOUT", "300"))  # 5分钟
    AI_RECOMMENDATION_CACHE_TTL: int = int(os.getenv("AI_RECOMMENDATION_CACHE_TTL", "1800"))  # 30分钟
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
