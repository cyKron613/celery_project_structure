import socket
from loguru import logger
from DrissionPage import ChromiumOptions
from multiprocessing import Lock
import time
import random
from threading import Lock
import socket

# 全局端口锁和已分配端口集合
port_lock = Lock()
class ChromiumOptionsManager:
    """ChromiumOptions 单例管理器，确保所有实例使用相同的配置"""
    _instance = None
    _lock = Lock()
    _options = None
    _port = None
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._port = cls.get_available_port()  # 为实例分配固定端口
                    cls._instance._init_options()
                    logger.info(f"ChromiumOptions单例初始化完成，使用固定端口: {cls._instance._port}")
        return cls._instance
    
    def _init_options(self):
        """初始化ChromiumOptions配置"""
        if self._options is None:
            self._options = ChromiumOptions()
            # 设置通用配置
            self._options.set_argument('--no-sandbox')
            self._options.set_argument('--headless=new')
            self._options.set_argument('--disable-blink-features=AutomationControlled')
            self._options.set_argument('--disable-web-security')
            self._options.set_argument('--disable-dev-shm-usage')  # 减少内存使用
            self._options.set_argument('--disable-gpu')  # 减少GPU内存使用
            # 可以根据需要添加更多配置

    def get_available_port():
        """获取可用的端口号（线程安全版本）"""
        with port_lock:
            # 尝试多次以避免竞态条件
            for _ in range(3):  # 最多尝试3次
                port = random.randint(9223, 9323)
                logger.info(f"尝试端口: {port}")

                # 检查端口是否真正可用
                try:
                    pre_port = None
                    for i in range(2):
                        # 初始化socket
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.1)  # 设置超时避免长时间阻塞
                        try:
                            # 3秒后再检查一次是否连接占用.
                            sock.bind(('localhost', port))
                            sock.close()
                            time.sleep(3)
                            if i == 1 and pre_port == port:
                                return port
                            else:
                                pre_port = port

                        except Exception as e:
                            logger.error(f"端口 {port} 绑定失败: {str(e)}")
                            continue
                        finally:
                            try:
                                if sock and not sock._closed:  # 只有在socket未关闭时才关闭
                                    sock.close()
                            except:
                                pass
                except OSError as e:
                    # 端口已被占用，重新随机端口
                    continue
                finally:
                    try:
                        sock.close()
                    except:
                        pass
        raise RuntimeError("No available ports found after cleanup")
    
    def get_options(self, port=None):
        """
        获取配置好的ChromiumOptions实例
        :param port: 可选端口号，如果提供则设置端口
        :return: ChromiumOptions实例
        """
        options = self._options.copy() if hasattr(self._options, 'copy') else ChromiumOptions()
        
        # 重新应用配置（确保copy后的实例也有相同的配置）
        options.set_argument('--no-sandbox')
        options.set_argument('--disable-blink-features=AutomationControlled')
        options.set_argument('--disable-web-security')
        options.set_argument('--disable-dev-shm-usage')
        options.set_argument('--disable-gpu')
        options.set_argument('--headless=new')
        
        # 使用实例的固定端口，除非明确指定其他端口
        final_port = port if port is not None else self._port
        if final_port is not None:
            options.set_local_port(final_port)
            
        return options
    
    def get_port(self):
        """获取当前单例实例使用的固定端口"""
        return self._port
