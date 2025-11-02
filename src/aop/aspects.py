"""
AOP切面实现 - 基于aspectlib
提供横切关注点的统一管理
"""

import time
import functools
from typing import Any, Dict, Optional
from aspectlib import weave, Aspect
from ioc.services import ILoggingService


# 全局配置
_logging_service: Optional[ILoggingService] = None


def initialize_aspects(logging_service: ILoggingService):
    """初始化AOP切面系统"""
    global _logging_service
    _logging_service = logging_service


# 日志切面
@Aspect(bind=True)
def logging_aspect(cutpoint, *args, **kwargs):
    """日志记录切面"""
    method_name = cutpoint.__name__
    class_name = getattr(cutpoint, '__qualname__', method_name).split('.')[0]
    
    if _logging_service:
        _logging_service.debug(f"[AOP] 调用 {class_name}.{method_name} 参数: {args}, {kwargs}")
    
    start_time = time.time()
    try:
        result = yield
        duration = time.time() - start_time
        
        if _logging_service:
            _logging_service.debug(f"[AOP] {class_name}.{method_name} 完成，耗时: {duration:.3f}s，结果: {result}")
        
        return result
    except Exception as e:
        duration = time.time() - start_time
        
        if _logging_service:
            _logging_service.error(f"[AOP] {class_name}.{method_name} 异常，耗时: {duration:.3f}s，错误: {e}")
        
        raise


# 性能监控切面
@Aspect(bind=True)
def performance_aspect(cutpoint, *args, **kwargs):
    """性能监控切面"""
    method_name = cutpoint.__name__
    class_name = getattr(cutpoint, '__qualname__', method_name).split('.')[0]
    
    start_time = time.time()
    
    try:
        result = yield
        duration = time.time() - start_time
        
        # 记录性能数据
        if duration > 0.1:  # 超过100ms的慢方法
            if _logging_service:
                _logging_service.warning(f"[PERF] 慢方法检测: {class_name}.{method_name} 耗时 {duration:.3f}s")
        
        # 这里可以添加到指标收集系统
        # metrics_service.record_method_duration(class_name, method_name, duration)
        
        return result
    except Exception as e:
        duration = time.time() - start_time
        
        if _logging_service:
            _logging_service.error(f"[PERF] 方法异常: {class_name}.{method_name} 耗时 {duration:.3f}s")
        
        raise


# 异常处理切面
@Aspect(bind=True)
def exception_aspect(cutpoint, *args, **kwargs):
    """异常处理切面"""
    method_name = cutpoint.__name__
    class_name = getattr(cutpoint, '__qualname__', method_name).split('.')[0]
    
    try:
        result = yield
        return result
    except Exception as e:
        error_key = f"{class_name}.{method_name}.{type(e).__name__}"
        
        if _logging_service:
            _logging_service.error(f"[AOP] 异常处理: {error_key} - {str(e)}")
        
        # 这里可以添加异常统计和处理策略
        # exception_tracker.record_exception(error_key, e)
        
        raise


# 事务切面
@Aspect(bind=True)
def transaction_aspect(cutpoint, *args, **kwargs):
    """事务管理切面"""
    method_name = cutpoint.__name__
    class_name = getattr(cutpoint, '__qualname__', method_name).split('.')[0]
    
    # 备份当前状态（简化实现）
    instance = args[0] if args and hasattr(args[0], '__dict__') else None
    backup_state = None
    
    if instance:
        backup_state = getattr(instance, '__dict__', {}).copy()
    
    if _logging_service:
        _logging_service.debug(f"[TRANS] 开始事务: {class_name}.{method_name}")
    
    try:
        result = yield
        
        if _logging_service:
            _logging_service.debug(f"[TRANS] 提交事务: {class_name}.{method_name}")
        
        return result
    except Exception as e:
        # 回滚状态
        if instance and backup_state:
            instance.__dict__.update(backup_state)
            
        if _logging_service:
            _logging_service.warning(f"[TRANS] 回滚事务: {class_name}.{method_name} - {e}")
        
        raise


# 监控装饰器
def monitored(func):
    """综合监控装饰器 - 包含所有切面"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 应用所有切面
        enhanced_func = logging_aspect(
            performance_aspect(
                exception_aspect(func)
            )
        )
        return enhanced_func(*args, **kwargs)
    return wrapper


# 便捷装饰器
def logged(func):
    """日志装饰器"""
    return logging_aspect(func)


def performance_monitored(func):
    """性能监控装饰器"""
    return performance_aspect(func)


def transactional(func):
    """事务装饰器"""
    return transaction_aspect(func)


# 将切面应用到类
def apply_aspects_to_class(target_class: type, aspects: list = None):
    """将切面应用到类的所有方法"""
    if aspects is None:
        aspects = [logging_aspect, performance_aspect, exception_aspect]
    
    for aspect in aspects:
        if aspect:
            weave(target_class, aspect)


def apply_aspects_to_method(target_method, aspects: list = None):
    """将切面应用到特定方法"""
    if aspects is None:
        aspects = [logging_aspect, performance_aspect, exception_aspect]
    
    enhanced_method = target_method
    for aspect in reversed(aspects):  # 反向应用，保证正确的调用顺序
        if aspect:
            enhanced_method = aspect(enhanced_method)
    
    return enhanced_method