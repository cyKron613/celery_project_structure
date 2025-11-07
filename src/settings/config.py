from pathlib import Path
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # 兼容旧版本pydantic
    from pydantic import BaseSettings
from typing import Optional

from decouple import config

# 获取项目根目录的绝对路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

class Settings(BaseSettings):
    """应用配置"""
    
    # Celery配置
    CELERY_BROKER_URL: str = config("CELERY_BROKER_URL", cast=str)  # type: ignore
    CELERY_RESULT_BACKEND: str = config("CELERY_RESULT_BACKEND", cast=str)  # type: ignore
    CELERY_BROKER_POOL_LIMIT: int = config("CELERY_BROKER_POOL_LIMIT", cast=int)
    CELERY_BROKER_CONNECTION_TIMEOUT: int = config("CELERY_BROKER_CONNECTION_TIMEOUT", cast=int)
    
    # 数据采集配置
    DEFAULT_DATA_SOURCE: str = config("DEFAULT_DATA_SOURCE", cast=str)  # type: ignore
    REQUEST_TIMEOUT: int = config("REQUEST_TIMEOUT", cast=int)
    MAX_RETRIES: int = config("MAX_RETRIES", cast=int)
    OPENAI_API_KEY: str = config("OPENAI_API_KEY", cast=str)  # type: ignore
    
    # 数据库配置（可选）
    DATABASE_URL: Optional[str] = config("DATABASE_URL", cast=str, default=None)
    
    # 日志配置
    LOG_LEVEL: str = config("LOG_LEVEL", cast=str, default="INFO")
    
    class Config:
        env_file = ENV_FILE
        # extra = "ignore"  # 忽略未知的环境变量

# 全局配置实例
settings = Settings()


if __name__ == "__main__":
    print(settings.CELERY_BROKER_URL)
    print(settings.CELERY_RESULT_BACKEND)
    print(settings.DEFAULT_DATA_SOURCE)
    print(settings.REQUEST_TIMEOUT)
    print(settings.MAX_RETRIES)
    print(settings.OPENAI_API_KEY)
