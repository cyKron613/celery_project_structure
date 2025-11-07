from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from celery.result import AsyncResult
from src.main.tasks.test_tasks import hello_task
from src.main.tasks.craw_chone_thread import time_task


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Celery数据采集框架API",
    description="基于Celery的数据采集框架API服务",
    version="1.0.0"
)

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class HelloRequest(BaseModel):
    message: str = "hello"
    delay_seconds: int = 0

# API路由
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Celery数据采集框架API服务",
        "version": "1.0.0",
        "endpoints": [
            "/tasks/hello - POST - 发送hello消息到Celery队列",
        ]
    }

@app.post("/tasks/hello", response_model=TaskStatusResponse)
async def send_hello_message(request: HelloRequest):
    """发送hello消息到Celery队列"""
    try:
        task = hello_task.delay(request.message, request.delay_seconds)
        return TaskStatusResponse(
            task_id=task.id,
            status="started",
            result=None
        )
    except Exception as e:
        logger.error(f"发送hello消息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 2. 启动船讯网数据采集任务
@app.post("/tasks/craw-chone", response_model=TaskStatusResponse)
async def start_craw_chone_task():
    """启动船讯网数据采集任务"""
    try:
        task = time_task.delay()
        return TaskStatusResponse(
            task_id=task.id,
            status="started",
            result=None
        )
    except Exception as e:
        logger.error(f"启动船讯网数据采集任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# /tasks/{task_id}
@app.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """获取任务状态"""
    try:
        result = AsyncResult(task_id)
        return TaskStatusResponse(
            task_id=task_id,
            status=result.status,
            result=result.result if result.status == 'SUCCESS' else None,
            error=result.traceback if result.status == 'FAILURE' else None
        )
    except Exception as e:
        logger.error(f"获取任务状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)