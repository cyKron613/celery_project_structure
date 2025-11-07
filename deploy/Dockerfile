# 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt


# 复制源代码
COPY src/ ./src/

# 设置环境变量 - 确保Python路径包含项目根目录
ENV PYTHONPATH=/app

# 启动命令
CMD ["python", "check_env.py"]