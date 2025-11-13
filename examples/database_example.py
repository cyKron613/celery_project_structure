#!/usr/bin/env python3
"""
数据库连接类使用示例 - 使用settings配置
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.db_tools import (
    init_database_connection,
    close_database_connection,
    insert_into_table,
    batch_insert_into_table,
    query_table
)
from src.settings.config import settings

from src.utils.db_tools import std_db


def main():
    """主函数，演示数据库操作"""
    
    # 显示当前数据库配置
    print("当前数据库配置:")
    print(f"  DB_HOST: {settings.POSTGRES_HOST}")
    print(f"  DB_PORT: {settings.POSTGRES_PORT}")
    print(f"  DB_NAME: {settings.POSTGRES_DB}")
    print(f"  DB_USER: {settings.POSTGRES_USERNAME}")
    print(f"  DB_PASSWORD: {settings.POSTGRES_PASSWORD}")
    print(f"  DB_SCHEMA: {settings.POSTGRES_SCHEMA}")
    print(f"  连接池大小: {settings.DB_POOL_SIZE}")
    print(f"  最大溢出连接: {settings.DB_POOL_OVERFLOW}")
    
    # # # 初始化数据库连接
    # print("\n正在初始化数据库连接...")
    # init_database_connection()

    # query_table('sdc_test.algorithm_list')
    
    # print("正在关闭数据库连接...")
    # close_database_connection()
    # print("数据库连接已关闭")

    # 上下文方式
    from sqlalchemy import text

    with std_db._scoped_session() as session:
        result = session.execute(text("SELECT * FROM sdc_data.ex_shipping_information"))
        for row in result:
            print(row)


if __name__ == "__main__":
    main()