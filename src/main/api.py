from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from celery.result import AsyncResult
from .tasks import collect_data_task, process_data_task, data_collection_pipeline, hello_task

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Celery数据采集框架API",
    description="基于Celery的数据采集框架API服务",
    version="1.0.0"
)

# 数据模型
class DataCollectionRequest(BaseModel):
    url: Optional[str] = None
    data_type: str = 'web'
    
class DataProcessingRequest(BaseModel):
    raw_data: Dict[str, Any]
    processor_type: str = 'clean'

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
            "/tasks/collect-data - POST - 启动数据采集任务",
            "/tasks/process-data - POST - 启动数据处理任务",
            "/tasks/pipeline - POST - 启动数据采集管道",
            "/tasks/{task_id} - GET - 获取任务状态"
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

@app.post("/tasks/collect-data", response_model=TaskStatusResponse)
async def start_data_collection(request: DataCollectionRequest):
    """启动数据采集任务"""
    try:
        task = collect_data_task.delay(request.url, request.data_type)
        return TaskStatusResponse(
            task_id=task.id,
            status="started",
            result=None
        )
    except Exception as e:
        logger.error(f"启动数据采集任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks/process-data", response_model=TaskStatusResponse)
async def start_data_processing(request: DataProcessingRequest):
    """启动数据处理任务"""
    try:
        task = process_data_task.delay(request.raw_data, request.processor_type)
        return TaskStatusResponse(
            task_id=task.id,
            status="started",
            result=None
        )
    except Exception as e:
        logger.error(f"启动数据处理任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks/pipeline", response_model=TaskStatusResponse)
async def start_data_pipeline(request: DataCollectionRequest):
    """启动数据采集管道"""
    try:
        task = data_collection_pipeline.delay(request.url, request.data_type)
        return TaskStatusResponse(
            task_id=task.id,
            status="started",
            result=None
        )
    except Exception as e:
        logger.error(f"启动数据采集管道失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """获取任务状态"""
    try:
        task_result = AsyncResult(task_id)
        
        response_data = TaskStatusResponse(
            task_id=task_id,
            status=task_result.status
        )
        
        if task_result.ready():
            if task_result.successful():
                response_data.result = task_result.result
            else:
                response_data.error = str(task_result.result)
        
        return response_data
        
    except Exception as e:
        logger.error(f"获取任务状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"  # 在实际应用中应该使用当前时间
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)