from celery import shared_task
import requests
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@shared_task
def hello_task(message="hello", delay_seconds=0):
    """
    测试任务：向Celery队列发送hello消息
    
    Args:
        message: 要发送的消息
        delay_seconds: 延迟秒数
    """
    try:
        logger.info(f"开始执行hello任务: {message}")
        
        # 如果有延迟，先等待
        if delay_seconds > 0:
            logger.info(f"等待 {delay_seconds} 秒...")
            time.sleep(delay_seconds)
        
        # 模拟任务处理
        result = {
            'message': message,
            'received_at': datetime.now().isoformat(),
            'processed_at': datetime.now().isoformat(),
            'status': 'success',
            'task_type': 'hello'
        }
        
        logger.info(f"hello任务完成: {result}")
        return result
        
    except Exception as e:
        logger.error(f"hello任务异常: {e}")
        return {'error': str(e), 'status': 'failed'}

