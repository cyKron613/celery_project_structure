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
    
    # 数据库配置
    DATABASE_TYPE: str = config("DATABASE_TYPE", cast=str, default="postgresql")  # 数据库类型: postgresql, oceanbase
    POSTGRES_CONNECT: str = config("POSTGRES_CONNECT", cast=str)  # type: ignore
    POSTGRES_HOST: str = config("POSTGRES_HOST", cast=str)  # type: ignore
    POSTGRES_PORT: int = config("POSTGRES_PORT", cast=int)  # type: ignore
    POSTGRES_DB: str = config("POSTGRES_DB", cast=str)  # type: ignore
    POSTGRES_USERNAME: str = config("POSTGRES_USERNAME", cast=str)  # type: ignore
    POSTGRES_PASSWORD: str = config("POSTGRES_PASSWORD", cast=str)  # type: ignore
    POSTGRES_SCHEMA: str = config("POSTGRES_SCHEMA", cast=str)  # type: ignore
    
    # OceanBase配置
    OCEANBASE_HOST: str = config("OCEANBASE_HOST", cast=str, default="")  # type: ignore
    OCEANBASE_PORT: int = config("OCEANBASE_PORT", cast=int, default=2881)  # type: ignore
    OCEANBASE_DB: str = config("OCEANBASE_DB", cast=str, default="")  # type: ignore
    OCEANBASE_USERNAME: str = config("OCEANBASE_USERNAME", cast=str, default="")  # type: ignore
    OCEANBASE_PASSWORD: str = config("OCEANBASE_PASSWORD", cast=str, default="")  # type: ignore

    DB_MAX_POOL_CON: int = config("DB_MAX_POOL_CON", cast=int)  # type: ignore
    DB_POOL_SIZE: int = config("DB_POOL_SIZE", cast=int)  # type: ignore
    DB_POOL_OVERFLOW: int = config("DB_POOL_OVERFLOW", cast=int)  # type: ignore
    DB_TIMEOUT: int = config("DB_TIMEOUT", cast=int)  # type: ignore
    DB_POOL_RECYCLE: int = config("DB_POOL_RECYCLE", cast=int)  # type: ignore
    DB_POOL_TIMEOUT: int = config("DB_POOL_TIMEOUT", cast=int)  # type: ignore
    DB_POOL_RESET_ON_RETURN: str = config("DB_POOL_RESET_ON_RETURN", cast=str)  # type: ignore
    IS_DB_ECHO_LOG: bool = config("IS_DB_ECHO_LOG", cast=bool)  # type: ignore


    # 数据采集配置
    CRAWL_TABLE_NAME: str = config("CRAWL_TABLE_NAME", cast=str)  # type: ignore

    # 微信配置
    WECHAT_TOKEN: str = config("WECHAT_TOKEN", cast=str)  # type: ignore
    WECHAT_COOKIE: str = config("WECHAT_COOKIE", cast=str)  # type: ignore
    

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
