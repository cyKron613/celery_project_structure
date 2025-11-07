# 任务模块初始化文件
# 确保Celery能够正确发现和注册任务

from .craw_chone_thread import time_task
from .test_tasks import (
    hello_task
)

# 定义导出的任务列表
__all__ = [
    'time_task',
    'hello_task',
]