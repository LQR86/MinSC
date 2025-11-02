"""
配置服务实现
"""
from typing import Dict, Any
from ioc.services import IConfigService


class ConfigService:
    """配置服务实现"""
    
    def __init__(self):
        self._config: Dict[str, Any] = {
            'debug': True,
            'logging_level': 'INFO',
            'performance_monitoring': True
        }
    
    def get_config(self, key: str, default=None):
        """获取配置值"""
        return self._config.get(key, default)
    
    def set_config(self, key: str, value):
        """设置配置值"""
        self._config[key] = value
    
    def reload_config(self):
        """重新加载配置"""
        pass  # 简单实现