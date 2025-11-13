# Celery分布式任务框架

一个基于Celery的现代化分布式任务处理框架，支持快速搭建数据采集、处理和管理的分布式系统。提供完整的Docker容器化部署方案和Kubernetes支持。

## 项目结构

```
celery_project_structure/
├── deploy/                 # Docker部署文件
│   ├── BaseDockerfile      # 基础容器镜像定义
│   ├── Dockerfile          # 应用容器镜像定义
│   └── docker-compose.yaml # 多服务编排
├── k8s/                    # Kubernetes部署配置
│   ├── deploy.sh           # 部署脚本
│   └── deployment.yaml     # K8s部署文件
├── src/                    # 源代码目录
│   ├── main/               # 主工程代码
│   │   └── tasks/          # Celery任务模块
│   ├── settings/           # 配置管理
│   │   ├── celery_config/   # Celery配置
│   │   └── config.py        # 应用配置
│   └── utils/              # 工具模块
│       ├── ai_tools.py     # AI工具函数
│       ├── chromium_manager.py  # 浏览器管理
│       ├── craw_tools.py   # 爬虫工具
│       ├── db_tools.py     # 数据库工具
│       └── wechat_crawler_demo.py  # 微信爬虫示例
├── examples/               # 示例代码
│   └── database_example.py # 数据库操作示例
├── sql/                    # SQL脚本
│   └── ex_shipping_information.sql  # 示例SQL
├── requirements.txt        # Python依赖
├── .env.example           # 环境变量示例
├── start_flower.py        # Flower监控服务启动脚本
├── check_env.py           # 环境检查脚本
├── test-deploy.sh         # 测试部署脚本
└── README.md              # 项目文档
```

## 功能特性

### 核心功能
- ✅ 基于Celery的分布式任务队列
- ✅ 多队列任务路由配置（默认队列、爬虫队列）
- ✅ FastAPI RESTful API接口
- ✅ Docker容器化部署
- ✅ Kubernetes集群部署支持
- ✅ 定时任务调度（Celery Beat）
- ✅ Flower实时监控和任务管理
- ✅ 任务状态查询和管理
- ✅ 错误重试和日志记录

### 数据采集能力
- ✅ 船讯网数据采集任务
- ✅ 微信爬虫示例
- ✅ 浏览器自动化（Chromium）
- ✅ AI工具集成
- ✅ 数据库操作工具

### 开发工具
- ✅ 环境检查脚本
- ✅ 测试部署脚本
- ✅ 示例代码和SQL脚本
- ✅ 自动任务注册机制

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd celery_project_structure

# 复制环境配置
cp .env.example .env

# 检查环境依赖
python check_env.py
```
# 安装依赖
```bash
pip install -r requirements.txt

# 或者安装中间镜像
docker build -f deploy/BaseDockerfile -t craw_service:base .
```


### 2. 启动服务

#### 方式一：使用Docker Compose（推荐）

```bash
cd deploy
docker-compose up -d
```

#### 方式二：使用测试部署脚本

```bash
# 运行测试部署脚本
./test-deploy.sh
```

#### 方式三：手动启动各服务

```bash
# 启动默认队列Worker（处理普通任务）
celery -A src.settings.celery_config.celery_app worker --loglevel=info -Q default

# 启动爬虫队列Worker（处理数据采集任务）
celery -A src.settings.celery_config.celery_app worker --loglevel=info -Q crawler_queue

# 启动Celery Beat（定时任务）
celery -A src.settings.celery_config.celery_app beat --loglevel=info

# 启动FastAPI服务
uvicorn src.main.api:app --host 0.0.0.0 --port 8000 --reload

# 启动Flower监控服务
celery flower --address=0.0.0.0 --port=5555 --basic_auth=admin:admin123
```

### 3. 访问服务

- **FastAPI服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs  # 已注释
- **Flower监控**: http://localhost:5555 (用户名: admin, 密码: admin123)

## API使用示例

### 1. 启动AI基础数据采集任务
```bash
curl -X POST "http://localhost:8000/api/tasks/craw-aibase"
```

### 2. 启动翻译任务
```bash
curl -X POST "http://localhost:8000/api/tasks/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello World",
    "target_language": "zh"
  }'
```

### 3. 获取任务结果
```bash
curl "http://localhost:8000/api/tasks/result?task_id=task-uuid-here"
```

### 4. 查看任务状态
```bash
curl "http://localhost:8000/api/tasks/status"
```

## 任务类型

### 1. AI基础数据采集任务 (`craw_aibase_thread`)
- 定时采集AI基础数据
- 支持多页面数据解析
- 自动数据入库
- 错误重试和超时控制
- **队列分配**: `crawler_queue`（爬虫队列）

### 2. 翻译任务 (`translate_tasks`)
- 文本翻译处理任务
- 支持多种语言翻译
- 批量处理能力
- **队列分配**: `default`（默认队列）

### 3. 新任务模块 (`new_tasks`)
- 预留的新任务开发目录
- 支持快速扩展新功能
- **队列分配**: 根据任务类型自动分配

## 队列配置

项目配置了多队列任务路由，实现任务分类处理：

### 队列定义
- **`default`队列**: 处理普通测试任务和系统任务
- **`crawler_queue`队列**: 专门处理数据采集和爬虫任务

### 任务路由配置

任务路由配置在 `src/settings/celery_config/celery_app.py` 中：

```python
task_routes = {
    'src.main.tasks.time_tasks.craw_aibase_thread.time_task': {'queue': 'crawler_queue'},
    'src.main.tasks.time_tasks.translate_tasks.translate_task': {'queue': 'default'},
}
```

### Docker部署队列服务

在 `deploy/docker-compose.yaml` 中配置了独立的队列服务：

```yaml
# 默认队列Worker服务
celery-worker:
  command: celery -A src.settings.celery_config.celery_app worker --loglevel=info -Q default

# 爬虫队列Worker服务  
celery-crawler-worker:
  command: celery -A src.settings.celery_config.celery_app worker --loglevel=info -Q crawler_queue
```

### 队列优势
- **资源隔离**: 爬虫任务和普通任务分离，避免相互影响
- **优先级管理**: 可为不同队列设置不同的优先级和资源限制
- **故障隔离**: 单个队列故障不影响其他队列的正常运行
- **扩展性**: 可根据需要轻松添加新的专用队列

## 定时任务配置

框架预配置了以下定时任务：

- **AI基础数据采集**: 定时执行AI基础数据采集任务
- **翻译任务**: 定时执行文本翻译处理

配置位置：`src/settings/celery_config/celery_app.py` 中的 `beat_schedule`

当前启用的定时任务：
```python
# AI基础数据采集任务
'craw-aibase-daily': {
    'task': 'src.main.tasks.time_tasks.craw_aibase_thread.time_task',
    'schedule': crontab(minute='*/5'),  # 每5分钟执行一次
    'args': ()
},

# 翻译任务
'translate-daily': {
    'task': 'src.main.tasks.time_tasks.translate_tasks.translate_task',
    'schedule': crontab(hour=0, minute=0),  # 每天午夜执行
    'args': ()
}
```

## 自定义开发

### 任务模块结构

项目采用模块化任务结构，支持多类型任务组织：

```
src/main/tasks/
├── __init__.py      # 任务自动注册文件
├── api.py           # FastAPI服务
├── time_tasks/      # 定时任务目录
│   ├── __init__.py  # 定时任务注册
│   ├── craw_aibase_thread.py  # AI基础数据采集任务
│   └── translate_tasks.py     # 翻译任务
└── new_tasks/       # 新任务开发目录
```

### 自动任务注册机制 ⭐

**重要更新：不再需要手动注册任务！**

框架已实现智能任务自动发现机制，只需将任务文件放置在 `src/main/tasks/time_tasks/` 目录下，系统会自动：

1. **自动扫描**：扫描 `time_tasks` 目录下的所有Python文件
2. **自动识别**：识别以 `_task` 或 `_tasks` 结尾的任务函数
3. **自动注册**：自动注册到Celery任务系统
4. **自动导出**：自动添加到 `__all__` 列表

### 添加新的任务

1. **创建新的任务文件**：在 `src/main/tasks/time_tasks/` 或 `src/main/tasks/new_tasks/` 目录下创建新的Python文件

```python
# src/main/tasks/time_tasks/custom_task.py
from celery import shared_task

@shared_task
def custom_collection_task(parameters):
    """自定义数据采集任务"""
    # 实现自定义采集逻辑
    return {"status": "success", "data": "custom data"}

@shared_task
def another_custom_task():
    """另一个自定义任务"""
    return {"status": "completed"}
```

2. **系统自动注册**：任务会自动被发现和注册

3. **验证任务注册**：启动服务后，系统会显示已注册的任务列表

```
✅ 成功导入模块: src.main.tasks.time_tasks.custom_task
🎯 已注册的任务函数: ['custom_collection_task', 'another_custom_task']
```

4. **在API中添加接口**（可选）：

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
        'task': 'src.main.tasks.time_tasks.custom_task.custom_collection_task',
        'schedule': crontab(minute=0, hour=0),  # 每天午夜执行
        'args': ()
    }
}
```

### 验证任务注册（自动验证）

**无需手动验证！** 系统启动时会自动显示已注册的任务：

```
✅ 成功导入模块: src.main.tasks.time_tasks.test_tasks
✅ 成功导入模块: src.main.tasks.time_tasks.craw_chone_thread
🎯 已注册的任务函数: ['hello_task', 'time_task']
```

### 高级功能：动态导入任意文件夹

框架支持动态导入任意文件夹下的任务：

```python
from src.main.tasks import import_modules_from_folder

# 导入自定义文件夹下的任务
custom_tasks = import_modules_from_folder(
    folder_path="/path/to/custom/tasks",
    base_package_path="custom.tasks.package",
    task_suffixes=('_task', '_job')  # 自定义任务后缀
)
```

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

### Kubernetes部署

项目支持Kubernetes集群部署：

```bash
# 使用部署脚本
cd k8s
./deploy.sh

# 或者手动应用部署配置
kubectl apply -f deployment.yaml

# 查看部署状态
kubectl get pods
kubectl get services
```

### 生产环境配置

1. 修改 `deploy/docker-compose.yaml` 中的环境变量
2. 配置持久化存储（Redis数据）
3. 设置适当的资源限制
4. 配置日志收集和监控
5. 配置Kubernetes Ingress和Service

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
