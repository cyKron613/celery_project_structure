# 任务模块初始化文件
import importlib
from pathlib import Path
import sys

root_path = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.append(str(root_path))

# 通用任务模块导入函数
def import_task_modules(folder_name):
    """自动导入指定文件夹下的所有模块"""
    tasks_path = Path(__file__).parent / folder_name
    
    if not tasks_path.exists():
        print(f"⚠️  {folder_name} 文件夹不存在")
        return []
    
    imported_tasks = []
    
    # 遍历指定目录下的所有Python文件
    for file_path in tasks_path.glob("*.py"):
        if file_path.name == "__init__.py":
            continue
            
        module_name = file_path.stem  # 去掉.py后缀
        # 使用正确的包路径
        full_module_path = f"src.main.tasks.{folder_name}.{module_name}"
        
        try:
            module = importlib.import_module(full_module_path)
            
            # 获取模块中所有以_task结尾的函数，但排除装饰器
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                # 检查是否是函数且以_task结尾，同时排除装饰器名称
                if (callable(attr) and 
                    (attr_name.endswith('_task') or attr_name.endswith('_tasks')) and
                    attr_name not in ['shared_task', 'celery_task']):  # 排除装饰器名称
                    
                    # 为函数名添加文件夹和模块前缀，避免不同模块间的函数名冲突
                    prefixed_attr_name = f"{folder_name}.{module_name}.{attr_name}"
                    
                    # 只使用带前缀的函数名，避免重复
                    if prefixed_attr_name not in imported_tasks:
                        imported_tasks.append(prefixed_attr_name)
                        # 将函数添加到当前模块的命名空间
                        globals()[prefixed_attr_name] = attr
                    
                    # 对于第一个遇到的原始函数名，也添加到命名空间（但不添加到__all__列表）
                    if attr_name not in globals():
                        globals()[attr_name] = attr
            
            print(f"✅ 成功导入模块: {full_module_path}")
            
        except ImportError as e:
            print(f"❌ 导入模块失败 {full_module_path}: {e}")
    
    return imported_tasks

# 自动导入time_tasks和new_tasks下的任务
time_tasks_list = import_task_modules("time_tasks")
new_tasks_list = import_task_modules("new_tasks")

# 定义导出的任务列表
__all__ = [
    *time_tasks_list,  # 包含所有time_tasks导入的任务
    *new_tasks_list    # 包含所有new_tasks导入的任务
]

print(f"🎯 已注册的任务函数总数: {len(__all__)}")
print(f"📁 time_tasks 任务: {time_tasks_list}")
print(f"📁 new_tasks 任务: {new_tasks_list}")