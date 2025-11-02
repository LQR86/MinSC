"""
ECS 世界管理器

负责管理所有实体、组件和系统的核心类。
使用esper库提供高性能的ECS架构。
"""

import esper
from typing import List, Any, Dict, Type
import logging

class ECSWorld:
    """
    ECS世界管理器
    
    这个类封装了esper的World功能，并提供了一些便利方法
    用于管理实体、组件和系统。
    """
    
    def __init__(self):
        """初始化ECS世界"""
        # esper使用全局单例，不需要创建World对象
        self.systems: List[Any] = []
        self.system_priorities: Dict[Type, int] = {}
        
        # 统计信息
        self.entity_count = 0
        self.component_count = 0
        
        # 清空现有数据
        esper.clear_database()
        
        logging.info("🌍 ECS世界已初始化")
    
    def create_entity(self, *components) -> int:
        """
        创建新实体并添加组件
        
        Args:
            *components: 要添加到实体的组件实例
            
        Returns:
            int: 新创建的实体ID
        """
        entity = esper.create_entity(*components)
        self.entity_count += 1
        self.component_count += len(components)
        
        logging.debug(f"🎯 创建实体 {entity}，添加 {len(components)} 个组件")
        return entity
    
    def delete_entity(self, entity: int) -> None:
        """
        删除实体
        
        Args:
            entity: 要删除的实体ID
        """
        # 统计组件数量（用于统计）
        components = esper.components_for_entity(entity)
        component_count = len(components)
        
        esper.delete_entity(entity)
        self.entity_count -= 1
        self.component_count -= component_count
        
        logging.debug(f"🗑️ 删除实体 {entity}，移除 {component_count} 个组件")
    
    def add_component(self, entity: int, component: Any) -> None:
        """
        为实体添加组件
        
        Args:
            entity: 实体ID
            component: 组件实例
        """
        esper.add_component(entity, component)
        self.component_count += 1
        
        logging.debug(f"➕ 实体 {entity} 添加组件 {type(component).__name__}")
    
    def remove_component(self, entity: int, component_type: Type) -> None:
        """
        从实体移除组件
        
        Args:
            entity: 实体ID
            component_type: 组件类型
        """
        esper.remove_component(entity, component_type)
        self.component_count -= 1
        
        logging.debug(f"➖ 实体 {entity} 移除组件 {component_type.__name__}")
    
    def get_component(self, entity: int, component_type: Type) -> Any:
        """
        获取实体的组件
        
        Args:
            entity: 实体ID
            component_type: 组件类型
            
        Returns:
            Any: 组件实例，如果不存在则返回None
        """
        try:
            return esper.component_for_entity(entity, component_type)
        except KeyError:
            return None
    
    def has_component(self, entity: int, component_type: Type) -> bool:
        """
        检查实体是否有指定组件
        
        Args:
            entity: 实体ID
            component_type: 组件类型
            
        Returns:
            bool: 如果实体有该组件则返回True
        """
        return esper.has_component(entity, component_type)
    
    def get_components(self, *component_types):
        """
        获取包含指定组件的所有实体
        
        Args:
            *component_types: 组件类型列表
            
        Returns:
            generator: 返回 (entity, components) 的生成器
        """
        return esper.get_components(*component_types)
    
    def add_processor(self, processor: Any, priority: int = 0) -> None:
        """
        添加系统处理器
        
        Args:
            processor: 系统处理器实例
            priority: 处理优先级，数字越小优先级越高
        """
        esper.add_processor(processor, priority)
        self.systems.append(processor)
        self.system_priorities[type(processor)] = priority
        
        logging.info(f"🔧 添加系统 {type(processor).__name__}，优先级 {priority}")
    
    def remove_processor(self, processor_type: Type) -> None:
        """
        移除系统处理器
        
        Args:
            processor_type: 系统处理器类型
        """
        esper.remove_processor(processor_type)
        self.systems = [s for s in self.systems if type(s) != processor_type]
        if processor_type in self.system_priorities:
            del self.system_priorities[processor_type]
        
        logging.info(f"🔧 移除系统 {processor_type.__name__}")
    
    def process(self, dt: float = 0.0) -> None:
        """
        处理所有系统
        
        Args:
            dt: 时间增量（秒）
        """
        esper.process(dt)
    
    def clear(self) -> None:
        """清空世界中的所有实体和组件"""
        esper.clear_database()
        
        self.entity_count = 0
        self.component_count = 0
        
        logging.info("🧹 ECS世界已清空")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取ECS世界统计信息
        
        Returns:
            dict: 包含实体数量、组件数量等统计信息
        """
        return {
            'entity_count': self.entity_count,
            'component_count': self.component_count,
            'system_count': len(self.systems),
            'systems': [type(s).__name__ for s in self.systems]
        }
    
    def debug_info(self) -> str:
        """
        返回ECS世界的调试信息
        
        Returns:
            str: 格式化的调试信息
        """
        stats = self.get_stats()
        info = f"🌍 ECS世界状态:\n"
        info += f"  📊 实体数量: {stats['entity_count']}\n"
        info += f"  🧩 组件数量: {stats['component_count']}\n"
        info += f"  ⚙️ 系统数量: {stats['system_count']}\n"
        
        if stats['systems']:
            info += f"  🔧 活动系统: {', '.join(stats['systems'])}\n"
        
        return info