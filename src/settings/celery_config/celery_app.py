from celery import Celery
from celery.schedules import crontab
from src.settings.config import settings
from datetime import timedelta

# 创建Celery应用 - 更新为新的模块路径
celery_app = Celery('src.settings.celery_config.celery_app')

# 配置Celery - 使用统一的配置管理
celery_app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    broker_pool_limit=settings.CELERY_BROKER_POOL_LIMIT,
    broker_connection_timeout=settings.CELERY_BROKER_CONNECTION_TIMEOUT,

    broker_transport_options={
        'max_retries': 3,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.5,
    },

    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    
    # 定时任务配置
    beat_schedule={
        'collect-data-every-hour': {
            'task': 'src.main.tasks.collect_data_task',
            'schedule': timedelta(seconds=600),  # 每10分钟执行
            'args': ()
        },
        'cleanup-old-data-daily': {
            'task': 'src.main.tasks.cleanup_old_data_task',
            'schedule': crontab(hour=2, minute=0),  # 每天凌晨2点执行
            'args': ()
        }
    }
)

# 自动发现任务
celery_app.autodiscover_tasks(['src.main'])

if __name__ == '__main__':
    celery_app.start()