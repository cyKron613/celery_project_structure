import os
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # 兼容旧版本pydantic
    from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置"""
    
    # Celery配置
    CELERY_BROKER_URL: str = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND: str = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/8')
    CELERY_BROKER_POOL_LIMIT: int = int(os.getenv('CELERY_BROKER_POOL_LIMIT', '10'))
    CELERY_BROKER_CONNECTION_TIMEOUT: int = int(os.getenv('CELERY_BROKER_CONNECTION_TIMEOUT', '5'))
    
    # 数据采集配置
    DEFAULT_DATA_SOURCE: str = os.getenv('DEFAULT_DATA_SOURCE', 'https://httpbin.org/json')
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    
    # 数据库配置（可选）
    DATABASE_URL: Optional[str] = os.getenv('DATABASE_URL')
    
    # 日志配置
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    class Config:
        env_file = ".env"
        # extra = "ignore"  # 忽略未知的环境变量

# 全局配置实例
settings = Settings()


if __name__ == "__main__":
    print(settings.CELERY_BROKER_URL)
    print(settings.CELERY_RESULT_BACKEND)
    print(settings.DEFAULT_DATA_SOURCE)
    print(settings.REQUEST_TIMEOUT)
    print(settings.MAX_RETRIES)
