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

    worker_max_tasks_per_child = 10,  # 每个worker处理10个任务后重启
    worker_max_memory_per_child = 800000,  # 限制worker内存使用(800MB)
    worker_pool_restarts = True,  # 启用worker池重启功能

    task_time_limit = 2400,  # 任务硬超时2400秒
    task_soft_time_limit = 1800,  # 任务软超时1800秒

    task_acks_late = True,  # 确保任务失败后重新排队 （如果失败较多就会导致阻塞）
    worker_send_task_events = True,  # 启用任务事件
    task_track_started = True,  # 跟踪任务开始时间

    worker_prefetch_multiplier = 1,  # 减少预取任务数量
    worker_cancel_long_running_tasks_on_connection_loss = True,  # 连接丢失时取消长任务
    # flower_api_authenticated = False,  # 不使用认证
    

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
        # 'craw-chone-thread-daily': {
        #     'task': 'src.main.tasks.craw_chone_thread.time_task',
        #     'schedule': crontab(minute='*/1'),  # 每1分钟执行一次
        #     'args': ()
        # },
    }
)

# 自动发现任务 - 使用正确的包路径
celery_app.autodiscover_tasks(['src.main.tasks'])


if __name__ == '__main__':
    celery_app.start()