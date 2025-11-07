# Celery数据采集框架

一个基于Celery的可复用数据采集框架，支持快速搭建数据采集、处理和管理的分布式系统。

## 项目结构

```
celery_project_structure/
├── deploy/                 # Docker部署文件
│   ├── Dockerfile          # 容器镜像定义
│   └── docker-compose.yaml # 多服务编排
├── src/                    # 源代码目录
│   ├── main/               # 主工程代码
│   │   ├── __init__.py
│   │   ├── api.py          # FastAPI服务
│   │   └── tasks.py        # Celery任务定义
│   └── settings/           # 配置管理
│       ├── celery_config/   # Celery配置
│       └── config.py        # 应用配置
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

#### 方式三：使用Windows批处理脚本

```bash
# 运行启动脚本（包含所有服务）
start_all_services.bat
```

### 4. 访问服务

- **FastAPI服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **Flower监控**: http://localhost:5555 (用户名: admin, 密码: admin123)
- **健康检查**: http://localhost:8000/health

## API使用示例

### 启动数据采集任务

```bash
curl -X POST "http://localhost:8000/tasks/collect-data" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/json", "data_type": "api"}'
```

### 启动数据处理任务

```bash
curl -X POST "http://localhost:8000/tasks/process-data" \
  -H "Content-Type: application/json" \
  -d '{"raw_data": {"sample": "data"}, "processor_type": "clean"}'
```

### 启动数据采集管道

```bash
curl -X POST "http://localhost:8000/tasks/pipeline" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/json", "data_type": "api"}'
```

### 查询任务状态

```bash
curl "http://localhost:8000/tasks/{task_id}"
```

## 任务类型

### 1. 数据采集任务 (`collect_data_task`)
- 支持网页数据采集（web）
- 支持API数据采集（api）
- 自动重试机制（最多3次）
- 超时控制（30秒）

### 2. 数据处理任务 (`process_data_task`)
- 数据清洗（clean）
- 数据转换（transform）
- 可扩展的处理类型

### 3. 数据清理任务 (`cleanup_old_data_task`)
- 定时清理旧数据
- 可配置保留天数

### 4. 数据采集管道 (`data_collection_pipeline`)
- 组合多个任务的管道
- 顺序执行：采集 → 处理
- 错误处理和状态跟踪

## 定时任务配置

框架预配置了以下定时任务：

- **每小时数据采集**: 整点执行数据采集
- **每日数据清理**: 凌晨2点清理旧数据

配置位置：`celery/celery_app.py` 中的 `beat_schedule`

## 自定义开发

### 添加新的数据采集任务

1. 在 `src/main/tasks.py` 中添加新的任务函数：

```python
@shared_task
def custom_collection_task(parameters):
    # 实现自定义采集逻辑
    pass
```

2. 在 `src/main/api.py` 中添加对应的API接口

### 修改定时任务

编辑 `celery/celery_app.py` 中的 `beat_schedule` 配置：

```python
beat_schedule={
    'custom-task': {
        'task': 'src.main.tasks.custom_task',
        'schedule': crontab(minute=0, hour=0),  # 每天午夜执行
        'args': ()
    }
}
```

### 添加新的数据处理器

在 `src/main/tasks.py` 的 `process_data_task` 函数中添加新的处理逻辑。

## 部署说明

### Docker部署

项目提供了完整的Docker部署方案：

```bash
# 构建和启动所有服务
cd deploy
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
