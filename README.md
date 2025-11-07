# Celery数据采集框架

一个基于Celery的可复用数据采集框架，支持快速搭建数据采集、处理和管理的分布式系统。

## 项目结构

```
celery_project_structure/
├── deploy/                 # Docker部署文件
│   ├── BaseDockerfile      # 基础容器镜像定义
│   ├── Dockerfile          # 应用容器镜像定义
│   └── docker-compose.yaml # 多服务编排
├── src/                    # 源代码目录
│   ├── main/               # 主工程代码
│   │   └── tasks/          # Celery任务模块
│   │       ├── __init__.py
│   │       ├── api.py      # FastAPI服务
│   │       ├── craw_chone_thread.py  # 船讯网数据采集任务
│   │       └── test_tasks.py         # 测试任务
│   ├── settings/           # 配置管理
│   │   ├── celery_config/   # Celery配置
│   │   │   └── celery_app.py
│   │   └── config.py        # 应用配置
│   └── utils/              # 工具模块
│       ├── ai_tools.py     # AI工具函数
│       ├── chromium_manager.py  # 浏览器管理
│       ├── craw_tools.py   # 爬虫工具
│       └── db_tools.py     # 数据库工具
├── requirements.txt        # Python依赖
├── .env.example           # 环境变量示例
├── start_flower.py        # Flower监控服务启动脚本
└── README.md              # 项目文档
```

## 功能特性

- ✅ 基于Celery的分布式任务队列
- ✅ FastAPI RESTful API接口
- ✅ Docker容器化部署
- ✅ 定时任务调度（Celery Beat）
- ✅ Flower实时监控和任务管理
- ✅ 数据采集、处理、清理任务
- ✅ 任务状态查询和管理
- ✅ 可配置的数据源和处理流程
- ✅ 错误重试和日志记录

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd celery_project_structure

# 复制环境配置
cp .env.example .env

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动Redis（任务队列）

```bash
# 使用Docker启动Redis
docker run -d -p 6379:6379 redis:7-alpine

# 或者使用docker-compose启动所有服务
docker-compose -f deploy/docker-compose.yaml up -d
```

### 3. 启动服务

#### 方式一：使用Docker Compose（推荐）

```bash
cd deploy
docker-compose up -d
```

#### 方式二：手动启动各服务

```bash
# 启动Celery Worker（数据处理）
celery -A src.settings.celery_config.celery_app worker --loglevel=info

# 启动Celery Beat（定时任务）
celery -A src.settings.celery_config.celery_app beat --loglevel=info

# 启动FastAPI服务
uvicorn src.main.api:app --host 0.0.0.0 --port 8000 --reload

# 启动Flower监控服务
celery flower --address=0.0.0.0 --port=5555 --basic_auth=admin:admin123
```

### 4. 访问服务

- **FastAPI服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **Flower监控**: http://localhost:5555 (用户名: admin, 密码: admin123)

## API使用示例

### 1. 启动测试任务
```bash
curl -X POST "http://localhost:8000/api/tasks/hello" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello Celery",
    "delay": 5
  }'
```

### 2. 启动船讯网数据采集任务
```bash
curl -X POST "http://localhost:8000/api/tasks/craw-chone"
```


### 3. 获取任务结果
```bash
curl "http://localhost:8000/api/tasks/result?task_id=task-uuid-here"
```

## 任务类型

### 1. 船讯网数据采集任务 (`time_task`)
- 定时采集船讯网新闻数据
- 支持多页面数据解析
- 自动数据入库
- 错误重试和超时控制

### 2. 测试任务 (`hello_task`)
- 简单的测试任务
- 支持自定义消息和延迟
- 用于验证Celery任务系统

## 定时任务配置

框架预配置了以下定时任务：

- **船讯网数据采集**: 每分钟执行船讯网新闻数据采集

配置位置：`src/settings/celery_config/celery_app.py` 中的 `beat_schedule`

当前启用的定时任务：
```python
'craw-chone-thread-daily': {
    'task': 'src.main.tasks.craw_chone_thread.time_task',
    'schedule': crontab(minute='*/1'),  # 每1分钟执行一次
    'args': ()
}
```

## 自定义开发

### 任务模块结构

项目采用模块化任务结构，所有任务位于 `src/main/tasks/` 目录下：

```
src/main/tasks/
├── __init__.py      # 任务注册文件
├── api.py           # FastAPI服务
├── craw_chone_thread.py  # 船讯网数据采集任务
└── test_tasks.py    # 测试任务
```

### 任务注册机制

为确保Celery能正确发现和注册任务，需要在 `src/main/tasks/__init__.py` 文件中显式导入所有任务：

```python
# src/main/tasks/__init__.py
from .craw_chone_thread import time_task
from .test_tasks import hello_task, add_task, multiply_task

# 导出所有任务，确保Celery自动发现机制正常工作
__all__ = [
    'time_task',
    'hello_task', 
    'add_task',
    'multiply_task'
]
```

### 添加新的任务

1. **创建新的任务文件**：在 `src/main/tasks/` 目录下创建新的Python文件

```python
# src/main/tasks/custom_task.py
from celery import shared_task

@shared_task
def custom_collection_task(parameters):
    # 实现自定义采集逻辑
    return {"status": "success", "data": "custom data"}
```

2. **在 `__init__.py` 中注册新任务**：

```python
# 更新 src/main/tasks/__init__.py
from .custom_task import custom_collection_task

# 添加到 __all__ 列表
__all__ = [
    'time_task',
    'hello_task',
    'add_task',
    'multiply_task',
    'custom_collection_task'  # 新增任务
]
```

3. **在API中添加接口**（可选）：

```python
# 在 src/main/tasks/api.py 中添加API接口
@router.post("/custom-task")
async def start_custom_task():
    task = custom_collection_task.delay({})
    return {"task_id": task.id, "status": "started"}
```

### 修改或新增定时任务

编辑 `src/settings/celery_config/celery_app.py` 中的 `beat_schedule` 配置：

```python
beat_schedule={
    'custom-task': {
        'task': 'src.main.tasks.custom_task.custom_collection_task',
        'schedule': crontab(minute=0, hour=0),  # 每天午夜执行
        'args': ()
    }
}
```

### 验证任务注册

使用以下脚本验证任务是否正确注册：

```python
from src.settings.celery_config.celery_app import celery_app

# 检查已注册的任务
print("已注册的任务:")
for task_name in celery_app.tasks:
    if 'src.main.tasks' in task_name:
        print(f"  - {task_name}")
```

## 部署说明

### Docker部署

项目提供了完整的Docker部署方案：

```bash
# 构建和启动所有服务
cd deploy
docker build -f docker/BaseDockerfile -t port-congestion-api:base .

docker-compose up -d

# 查看服务状态
docker-compose ps

# 停止服务
docker-compose down
```

### 生产环境配置

1. 修改 `deploy/docker-compose.yaml` 中的环境变量
2. 配置持久化存储（Redis数据）
3. 设置适当的资源限制
4. 配置日志收集和监控

## 故障排除

### 常见问题

1. **Redis连接失败**
   - 检查Redis服务是否运行
   - 验证 `CELERY_BROKER_URL` 配置

2. **任务执行失败**
   - 查看Celery Worker日志
   - 检查任务参数和依赖

3. **API服务无法访问**
   - 确认FastAPI服务端口（8000）是否开放
   - 检查防火墙设置

### 日志查看

```bash
# 查看Celery Worker日志
celery -A celery.celery_app worker --loglevel=debug

# 查看Docker容器日志
docker-compose logs [service-name]
```

## 扩展建议

- 添加数据库支持（PostgreSQL/MySQL）
- 实现数据存储和查询接口
- 添加用户认证和权限控制
- 集成监控和告警系统
- 支持更多数据源类型（数据库、消息队列等）

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个框架。
