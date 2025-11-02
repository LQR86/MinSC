"""
AOP (面向切面编程) 模块
提供横切关注点的统一管理
"""

from .aspects import (
    initialize_aspects,
    logging_aspect,
    performance_aspect,
    exception_aspect,
    transaction_aspect,
    apply_aspects_to_class,
    apply_aspects_to_method,
    logged,
    performance_monitored,
    transactional,
    monitored
)

__all__ = [
    'initialize_aspects',
    'logging_aspect',
    'performance_aspect', 
    'exception_aspect',
    'transaction_aspect',
    'apply_aspects_to_class',
    'apply_aspects_to_method',
    'logged',
    'performance_monitored',
    'transactional',
    'monitored'
]