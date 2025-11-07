#!/usr/bin/env python3
"""
Celery数据采集框架 - 主应用入口
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """主函数"""
    logger.info("启动Celery数据采集框架...")
    
    # 使用统一的配置管理
    from src.settings.config import settings
    logger.info(f"Celery Broker URL: {settings.CELERY_BROKER_URL}")
    logger.info(f"Result Backend: {settings.CELERY_RESULT_BACKEND}")
    
    # 这里可以添加更多的启动逻辑
    # 比如检查Redis连接、初始化数据库等
    
    logger.info("Celery数据采集框架启动完成")
    logger.info("使用以下命令启动服务:")
    logger.info("1. Celery Worker: celery -A src.settings.celery_config.celery_app worker --loglevel=info")
    logger.info("2. Celery Beat: celery -A src.settings.celery_config.celery_app beat --loglevel=info")
    logger.info("3. FastAPI: uvicorn src.main.api:app --host 0.0.0.0 --port 8000 --reload")
    logger.info("4. Docker Compose: docker-compose -f deploy/docker-compose.yaml up -d")

if __name__ == "__main__":
    main()