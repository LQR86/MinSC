"""
ECS 实体工厂

用于创建游戏中的各种实体（单位、建筑、资源点等）。
工厂函数会创建实体并添加必要的组件。
"""

from typing import Tuple, Optional
import logging

from .world import ECSWorld
from .components import *

class EntityFactory:
    """
    实体工厂类
    
    提供创建各种游戏实体的便捷方法。
    """
    
    def __init__(self, ecs_world: ECSWorld):
        """
        初始化实体工厂
        
        Args:
            ecs_world: ECS世界实例
        """
        self.world = ecs_world
    
    def create_worker(self, position: Tuple[float, float], player_id: int = 0) -> int:
        """
        创建工人单位
        
        Args:
            position: 初始位置
            player_id: 玩家ID
            
        Returns:
            int: 新创建的实体ID
        """
        # 根据玩家ID确定颜色
        color = (100, 150, 255) if player_id == 0 else (255, 100, 100)
        
        entity = self.world.create_entity(
            Position(position[0], position[1]),
            Velocity(max_speed=80.0),
            Health(current=40, maximum=40),
            Sprite(color=color, size=(16, 16), layer=1),
            Movement(speed=80.0),
            UnitInfo(unit_type=UnitType.WORKER, player_id=player_id, name="工人"),
            Selectable(selected=False, selection_radius=20.0),
            Resource(amount=0, capacity=10, resource_type="mineral"),
            Collider(radius=8.0),
            Target()
        )
        
        logging.info(f"👷 创建工人实体 {entity}，玩家 {player_id}，位置 {position}")
        return entity
    
    def create_marine(self, position: Tuple[float, float], player_id: int = 0) -> int:
        """
        创建士兵单位
        
        Args:
            position: 初始位置
            player_id: 玩家ID
            
        Returns:
            int: 新创建的实体ID
        """
        # 根据玩家ID确定颜色
        color = (50, 100, 200) if player_id == 0 else (200, 50, 50)
        
        entity = self.world.create_entity(
            Position(position[0], position[1]),
            Velocity(max_speed=100.0),
            Health(current=60, maximum=60),
            Sprite(color=color, size=(14, 14), layer=1),
            Movement(speed=100.0),
            UnitInfo(unit_type=UnitType.MARINE, player_id=player_id, name="士兵"),
            Selectable(selected=False, selection_radius=20.0),
            Collider(radius=7.0),
            Target()
        )
        
        logging.info(f"🎖️ 创建士兵实体 {entity}，玩家 {player_id}，位置 {position}")
        return entity
    
    def create_command_center(self, position: Tuple[float, float], player_id: int = 0) -> int:
        """
        创建指挥中心
        
        Args:
            position: 初始位置
            player_id: 玩家ID
            
        Returns:
            int: 新创建的实体ID
        """
        # 根据玩家ID确定颜色
        color = (0, 100, 200) if player_id == 0 else (200, 0, 50)
        
        entity = self.world.create_entity(
            Position(position[0], position[1]),
            Health(current=500, maximum=500),
            Sprite(color=color, size=(60, 60), layer=0),
            UnitInfo(unit_type=UnitType.COMMAND_CENTER, player_id=player_id, name="指挥中心"),
            Selectable(selected=False, selection_radius=40.0),
            Storage(capacity=500, stored=0, resource_type="mineral"),
            ProductionQueue(queue=[], max_queue_size=5),
            Building(construction_progress=1.0, is_constructed=True, can_produce=True),
            Collider(radius=30.0, solid=True)
        )
        
        logging.info(f"🏛️ 创建指挥中心实体 {entity}，玩家 {player_id}，位置 {position}")
        return entity
    
    def create_barracks(self, position: Tuple[float, float], player_id: int = 0) -> int:
        """
        创建兵营
        
        Args:
            position: 初始位置
            player_id: 玩家ID
            
        Returns:
            int: 新创建的实体ID
        """
        # 根据玩家ID确定颜色
        color = (50, 150, 100) if player_id == 0 else (150, 50, 100)
        
        entity = self.world.create_entity(
            Position(position[0], position[1]),
            Health(current=300, maximum=300),
            Sprite(color=color, size=(50, 50), layer=0),
            UnitInfo(unit_type=UnitType.BARRACKS, player_id=player_id, name="兵营"),
            Selectable(selected=False, selection_radius=35.0),
            ProductionQueue(queue=[], max_queue_size=3),
            Building(construction_progress=1.0, is_constructed=True, can_produce=True),
            Collider(radius=25.0, solid=True)
        )
        
        logging.info(f"🏭 创建兵营实体 {entity}，玩家 {player_id}，位置 {position}")
        return entity
    
    def create_resource_point(self, position: Tuple[float, float], amount: int = 1000) -> int:
        """
        创建资源点
        
        Args:
            position: 位置
            amount: 资源总量
            
        Returns:
            int: 新创建的实体ID
        """
        # 根据资源量确定大小
        size = max(20, min(40, amount // 25))
        
        entity = self.world.create_entity(
            Position(position[0], position[1]),
            Sprite(color=(0, 200, 0), size=(size, size), layer=0),
            ResourcePoint(total_amount=amount, remaining_amount=amount, resource_type="mineral"),
            Collider(radius=size // 2, solid=False)
        )
        
        logging.info(f"💎 创建资源点实体 {entity}，位置 {position}，资源量 {amount}")
        return entity
    
    def create_worker_with_state_machine(self, position: Tuple[float, float], 
                                       player_id: int = 0, state_machine=None) -> int:
        """
        创建带状态机的工人单位
        
        Args:
            position: 初始位置
            player_id: 玩家ID
            state_machine: 状态机实例
            
        Returns:
            int: 新创建的实体ID
        """
        # 先创建基础工人
        entity = self.create_worker(position, player_id)
        
        # 添加状态机组件
        if state_machine:
            self.world.add_component(entity, StateMachine(
                state_machine=state_machine,
                current_state=state_machine.state if hasattr(state_machine, 'state') else 'idle'
            ))
            
            logging.info(f"🤖 为工人实体 {entity} 添加状态机")
        
        return entity
    
    def find_closest_entity_with_component(self, position: Tuple[float, float], 
                                         component_type, max_distance: float = float('inf')) -> Optional[int]:
        """
        查找最近的具有指定组件的实体
        
        Args:
            position: 搜索中心位置
            component_type: 组件类型
            max_distance: 最大搜索距离
            
        Returns:
            Optional[int]: 最近的实体ID，如果没有找到则返回None
        """
        closest_entity = None
        closest_distance = max_distance
        
        search_pos = Position(position[0], position[1])
        
        for entity, (pos, comp) in self.world.get_components(Position, component_type):
            distance = search_pos.distance_to(pos)
            if distance < closest_distance:
                closest_distance = distance
                closest_entity = entity
        
        return closest_entity
    
    def find_resource_points_in_range(self, position: Tuple[float, float], 
                                    range_distance: float) -> list:
        """
        查找范围内的资源点
        
        Args:
            position: 搜索中心位置
            range_distance: 搜索范围
            
        Returns:
            list: 资源点实体ID列表
        """
        resource_points = []
        search_pos = Position(position[0], position[1])
        
        for entity, (pos, resource_point) in self.world.get_components(Position, ResourcePoint):
            if not resource_point.is_depleted():
                distance = search_pos.distance_to(pos)
                if distance <= range_distance:
                    resource_points.append(entity)
        
        return resource_points
    
    def get_entity_position(self, entity: int) -> Optional[Tuple[float, float]]:
        """
        获取实体位置
        
        Args:
            entity: 实体ID
            
        Returns:
            Optional[Tuple[float, float]]: 位置坐标，如果实体不存在则返回None
        """
        pos = self.world.get_component(entity, Position)
        return (pos.x, pos.y) if pos else None
    
    def get_entities_by_player(self, player_id: int, unit_type: UnitType = None) -> list:
        """
        获取指定玩家的所有实体
        
        Args:
            player_id: 玩家ID
            unit_type: 可选的单位类型过滤
            
        Returns:
            list: 实体ID列表
        """
        entities = []
        
        for entity, (unit_info,) in self.world.get_components(UnitInfo):
            if unit_info.player_id == player_id:
                if unit_type is None or unit_info.unit_type == unit_type:
                    entities.append(entity)
        
        return entities

# ============================================================================
# 便捷函数
# ============================================================================

def create_default_game_entities(ecs_world: ECSWorld) -> dict:
    """
    创建默认的游戏实体
    
    Args:
        ecs_world: ECS世界实例
        
    Returns:
        dict: 创建的实体信息
    """
    factory = EntityFactory(ecs_world)
    
    entities = {
        'players': [
            {
                'id': 0,
                'command_center': factory.create_command_center((100, 100), 0),
                'workers': [
                    factory.create_worker((150, 150), 0),
                    factory.create_worker((170, 170), 0)
                ]
            },
            {
                'id': 1,
                'command_center': factory.create_command_center((700, 500), 1),
                'workers': [
                    factory.create_worker((650, 450), 1),
                    factory.create_worker((670, 470), 1)
                ]
            }
        ],
        'resource_points': [
            factory.create_resource_point((300, 200), 800),
            factory.create_resource_point((500, 300), 1000),
            factory.create_resource_point((200, 400), 600),
            factory.create_resource_point((600, 200), 900),
            factory.create_resource_point((400, 500), 750),
            factory.create_resource_point((800, 400), 850)
        ]
    }
    
    logging.info(f"🌍 创建默认游戏实体完成")
    logging.info(f"  👥 玩家数量: {len(entities['players'])}")
    logging.info(f"  💎 资源点数量: {len(entities['resource_points'])}")
    
    return entities

__all__ = [
    'EntityFactory',
    'create_default_game_entities'
]