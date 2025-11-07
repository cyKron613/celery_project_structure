#!/usr/bin/env python3
"""
启动Flower监控服务的脚本
"""

import os
import subprocess
import sys
from src.settings.config import settings

def start_flower():
    """启动Flower监控服务"""
    
    # 设置环境变量
    os.environ.setdefault('CELERY_BROKER_URL', settings.CELERY_BROKER_URL)
    
    print("🚀 启动Flower监控服务...")
    print("监控地址: http://localhost:5555")
    print("=" * 50)
    
    try:
        # 启动Flower服务
        cmd = [
            sys.executable, '-m', 'flower',
            '-A', 'src.settings.celery_config.celery_app',
            '--port=5555',
            '--broker=redis://localhost:6379/0',
            '--basic_auth=admin:admin123',  # 基本认证，用户名:admin 密码:admin123
            '--persistent=True',
            '--db=flower.db',
            '--max_tasks=10000'
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Flower服务已停止")
    except Exception as e:
        print(f"❌ 启动Flower服务失败: {e}")
        print("💡 请确保Redis和Celery Worker正在运行")

if __name__ == "__main__":
    start_flower()