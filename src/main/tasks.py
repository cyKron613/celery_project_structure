from celery import shared_task
import requests
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def collect_data_task(self, url=None, data_type='web'):
    """
    数据采集任务
    
    Args:
        url: 采集的URL地址
        data_type: 数据类型（web, api, database等）
    """
    try:
        logger.info(f"开始采集数据: {url or '默认数据源'}, 类型: {data_type}")
        
        # 模拟数据采集过程
        if data_type == 'web':
            # 网页数据采集
            if url:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = {
                    'url': url,
                    'content': response.text[:1000],  # 只取前1000字符
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                }
            else:
                # 默认数据采集
                data = {
                    'source': 'default',
                    'data': f"Sample data at {datetime.now().isoformat()}",
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                }
        elif data_type == 'api':
            # API数据采集
            if url:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
                data['timestamp'] = datetime.now().isoformat()
                data['status'] = 'success'
            else:
                data = {
                    'error': 'API URL required',
                    'status': 'failed'
                }
        else:
            data = {
                'error': f'Unsupported data type: {data_type}',
                'status': 'failed'
            }
        
        logger.info(f"数据采集完成: {data}")
        return data
        
    except requests.RequestException as e:
        logger.error(f"数据采集失败: {e}")
        # 重试逻辑
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries  # 指数退避
            raise self.retry(countdown=countdown, exc=e)
        return {'error': str(e), 'status': 'failed'}
    except Exception as e:
        logger.error(f"数据采集异常: {e}")
        return {'error': str(e), 'status': 'failed'}

@shared_task
def process_data_task(raw_data, processor_type='clean'):
    """
    数据处理任务
    
    Args:
        raw_data: 原始数据
        processor_type: 处理类型
    """
    try:
        logger.info(f"开始处理数据，类型: {processor_type}")
        
        # 模拟数据处理
        if processor_type == 'clean':
            # 数据清洗
            processed_data = {
                'original': raw_data,
                'cleaned': f"Cleaned data at {datetime.now().isoformat()}",
                'processor': 'clean',
                'timestamp': datetime.now().isoformat()
            }
        elif processor_type == 'transform':
            # 数据转换
            processed_data = {
                'original': raw_data,
                'transformed': f"Transformed data at {datetime.now().isoformat()}",
                'processor': 'transform',
                'timestamp': datetime.now().isoformat()
            }
        else:
            processed_data = {
                'original': raw_data,
                'processor': 'default',
                'timestamp': datetime.now().isoformat()
            }
        
        logger.info(f"数据处理完成")
        return processed_data
        
    except Exception as e:
        logger.error(f"数据处理异常: {e}")
        return {'error': str(e), 'status': 'failed'}

@shared_task
def cleanup_old_data_task(days_old=30):
    """
    清理旧数据任务
    
    Args:
        days_old: 保留天数
    """
    try:
        logger.info(f"开始清理超过{days_old}天的旧数据")
        
        # 模拟清理过程
        # 在实际应用中，这里会连接数据库删除旧数据
        cleanup_result = {
            'action': 'cleanup',
            'days_old': days_old,
            'cleaned_count': 0,  # 模拟清理数量
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }
        
        logger.info(f"数据清理完成: {cleanup_result}")
        return cleanup_result
        
    except Exception as e:
        logger.error(f"数据清理异常: {e}")
        return {'error': str(e), 'status': 'failed'}

@shared_task
def data_collection_pipeline(url, data_type='web'):
    """
    数据采集管道任务 - 组合多个任务
    """
    try:
        logger.info(f"开始数据采集管道: {url}")
        
        # 第一步：采集数据
        collection_result = collect_data_task.delay(url, data_type)
        raw_data = collection_result.get(timeout=300)  # 5分钟超时
        
        if raw_data.get('status') == 'success':
            # 第二步：处理数据
            processing_result = process_data_task.delay(raw_data)
            processed_data = processing_result.get(timeout=300)
            
            pipeline_result = {
                'collection': raw_data,
                'processing': processed_data,
                'pipeline_status': 'completed',
                'timestamp': datetime.now().isoformat()
            }
        else:
            pipeline_result = {
                'collection': raw_data,
                'pipeline_status': 'failed_at_collection',
                'timestamp': datetime.now().isoformat()
            }
        
        logger.info(f"数据采集管道完成: {pipeline_result}")
        return pipeline_result
        
    except Exception as e:
        logger.error(f"数据采集管道异常: {e}")
        return {'error': str(e), 'status': 'failed'}

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

# 测试接口 向celery队列delay发送 hello

