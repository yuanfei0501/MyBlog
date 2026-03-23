from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    APP_NAME: str = "MyBlog"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # API 配置
    API_V1_PREFIX: str = "/api/v1"

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://blog:blog123@localhost:5432/blog"

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT 配置
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小时
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "gif", "webp"}

    # 分页配置
    PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    # CORS 配置
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
