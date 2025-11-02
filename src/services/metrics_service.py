"""
指标监控服务实现
"""
from typing import Dict, Optional
from ioc.services import IMetricsService


class MetricsService:
    """指标监控服务实现"""
    
    def __init__(self, config):
        self.config = config
        self._metrics = {}
    
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """记录指标"""
        if self.config.get_config('performance_monitoring', True):
            self._metrics[name] = value
    
    def increment_counter(self, name: str, tags: Optional[Dict[str, str]] = None):
        """增加计数器"""
        current = self._metrics.get(name, 0)
        self._metrics[name] = current + 1
    
    def record_timing(self, name: str, duration: float, tags: Optional[Dict[str, str]] = None):
        """记录时间指标"""
        self._metrics[f"{name}_duration"] = duration