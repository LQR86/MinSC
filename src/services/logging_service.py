"""
简单日志服务实现
"""
import logging
from typing import Optional, Dict
from ioc.services import ILoggingService


class SimpleLoggingService(ILoggingService):
    """简单的日志服务实现"""
    
    def __init__(self, config=None, level=logging.INFO):
        # 如果传入了config服务，可以从中读取日志级别
        if config and hasattr(config, 'get'):
            level = getattr(logging, config.get('logging.level', 'INFO').upper(), logging.INFO)
        
        self.logger = logging.getLogger('MinSC')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(level)
    
    def debug(self, message: str, **kwargs) -> None:
        """调试日志"""
        if kwargs:
            message = f"{message} {kwargs}"
        self.logger.debug(message)
    
    def info(self, message: str, **kwargs) -> None:
        """信息日志"""
        if kwargs:
            message = f"{message} {kwargs}"
        self.logger.info(message)
    
    def warning(self, message: str, **kwargs) -> None:
        """警告日志"""
        if kwargs:
            message = f"{message} {kwargs}"
        self.logger.warning(message)
    
    def error(self, message: str, **kwargs) -> None:
        """错误日志"""
        if kwargs:
            message = f"{message} {kwargs}"
        self.logger.error(message)