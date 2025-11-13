# 基础镜像
FROM craw_service:base

# 设置工作目录
WORKDIR /app

# 复制源代码
COPY . /app/

# 设置环境变量 - 确保Python路径包含项目根目录
ENV PYTHONPATH=/app

# 启动命令
CMD ["python", "check_env.py"]