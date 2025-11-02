"""
MinSC IoC 服务接口定义

定义所有服务的协议接口，支持依赖注入和类型检查
"""
from typing import Protocol, List, Optional, Tuple, Dict
from enum import Enum


class BuildingType(Enum):
    """建筑类型枚举"""
    COMMAND_CENTER = "command_center"
    RESOURCE_DEPOT = "resource_depot"
    PRODUCTION_FACILITY = "production_facility"


class IBuildingManagerService(Protocol):
    """建筑管理服务接口"""
    
    def get_buildings_by_player(self, player_id: int) -> List['Building']:
        """获取指定玩家的所有建筑"""
        ...
    
    def find_nearest_building(self, 
                            position: Tuple[float, float], 
                            building_type: BuildingType,
                            player_id: int) -> Optional['Building']:
        """找到最近的指定类型建筑"""
        ...
    
    def get_buildings_in_range(self, 
                             center: Tuple[float, float], 
                             radius: float,
                             player_id: Optional[int] = None) -> List['Building']:
        """获取范围内的建筑"""
        ...
    
    def can_building_accept_resources(self, building: 'Building') -> bool:
        """检查建筑是否可以接受资源"""
        ...


class IUnitManagerService(Protocol):
    """单位管理服务接口"""
    
    def get_units_by_player(self, player_id: int) -> List['Unit']:
        """获取指定玩家的所有单位"""
        ...
    
    def find_units_in_range(self, 
                          center: Tuple[float, float],
                          radius: float,
                          player_id: Optional[int] = None) -> List['Unit']:
        """获取范围内的单位"""
        ...
    
    def get_unit_by_id(self, unit_id: int) -> Optional['Unit']:
        """根据ID获取单位"""
        ...


class IGameStateService(Protocol):
    """游戏状态服务接口"""
    
    def get_game_state(self) -> 'GameState':
        """获取当前游戏状态"""
        ...
    
    def get_player_resources(self, player_id: int) -> Dict[str, int]:
        """获取玩家资源"""
        ...
    
    def get_map_info(self) -> 'MapInfo':
        """获取地图信息"""
        ...


class IEventBusService(Protocol):
    """事件总线服务接口"""
    
    def emit(self, event_name: str, **kwargs):
        """发送事件"""
        ...
    
    def subscribe(self, event_name: str, callback):
        """订阅事件"""
        ...
    
    def unsubscribe(self, event_name: str, callback):
        """取消订阅"""
        ...


class IResourceManagerService(Protocol):
    """资源管理服务接口"""
    
    def get_resource_points(self) -> List['ResourcePoint']:
        """获取所有资源点"""
        ...
    
    def find_nearest_resource(self, 
                            position: Tuple[float, float],
                            resource_type: Optional[str] = None) -> Optional['ResourcePoint']:
        """找到最近的资源点"""
        ...
    
    def is_resource_available(self, resource_point: 'ResourcePoint') -> bool:
        """检查资源点是否可用"""
        ...


# AI 决策服务接口

class StrategicAssessment:
    """战略评估数据"""
    def __init__(self):
        self.player_id: int = 0
        self.economic_status: str = ""
        self.military_strength: str = ""
        self.tech_level: str = ""
        self.threats: list = []
        self.opportunities: list = []


class StrategicPlan:
    """战略计划"""
    def __init__(self):
        self.player_id: int = 0
        self.primary_goal: str = ""
        self.secondary_goals: list = []
        self.resource_allocation: dict = {}
        self.timeline: str = ""


class TacticalPlan:
    """战术计划"""
    def __init__(self):
        self.player_id: int = 0
        self.unit_assignments: dict = {}
        self.build_queue: list = []
        self.resource_targets: list = []


class UnitGroup:
    """单位组"""
    def __init__(self):
        self.units: list = []
        self.formation: str = ""
        self.objective: str = ""


class BuildOrder:
    """建造顺序"""
    def __init__(self):
        self.buildings: list = []
        self.priority: int = 0


class Command:
    """命令"""
    def __init__(self):
        self.type: str = ""
        self.target: object = None


class Task:
    """任务"""
    def __init__(self):
        self.name: str = ""
        self.priority: int = 0
        

class Threat:
    """威胁"""
    def __init__(self):
        self.type: str = ""
        self.severity: str = ""


class Response:
    """响应"""
    def __init__(self):
        self.actions: list = []


class IStrategyService(Protocol):
    """战略层服务接口 - AI决策的最高层"""
    
    def evaluate_game_situation(self, player_id: int) -> StrategicAssessment:
        """评估整体游戏局势"""
        ...
    
    def recommend_strategy(self, player_id: int) -> StrategicPlan:
        """推荐战略方案"""
        ...
    
    def adjust_long_term_goals(self, assessment: StrategicAssessment) -> None:
        """调整长期目标"""
        ...


class ITacticalService(Protocol):
    """战术层服务接口 - 中层决策和协调"""
    
    def plan_resource_allocation(self, strategy: StrategicPlan) -> TacticalPlan:
        """规划资源分配"""
        ...
    
    def coordinate_unit_groups(self, units: List['Unit']) -> List['UnitGroup']:
        """协调单位组"""
        ...
    
    def optimize_build_order(self, resources: Dict[str, int]) -> 'BuildOrder':
        """优化建造顺序"""
        ...


class IOperationalService(Protocol):
    """操作层服务接口 - 具体执行操作"""
    
    def execute_unit_command(self, unit: 'Unit', command: 'Command') -> bool:
        """执行单位命令"""
        ...
    
    def manage_worker_tasks(self, workers: List['Worker']) -> List['Task']:
        """管理工人任务"""
        ...
    
    def handle_immediate_threats(self, threats: List['Threat']) -> 'Response':
        """处理即时威胁"""
        ...


# 基础设施服务接口

class IConfigService(Protocol):
    """配置服务接口"""
    
    def get_config(self, key: str, default=None):
        """获取配置值"""
        ...
    
    def set_config(self, key: str, value):
        """设置配置值"""
        ...
    
    def reload_config(self):
        """重新加载配置"""
        ...


class ILoggingService(Protocol):
    """日志服务接口"""
    
    def debug(self, message: str, **kwargs):
        """调试日志"""
        ...
    
    def info(self, message: str, **kwargs):
        """信息日志"""
        ...
    
    def warning(self, message: str, **kwargs):
        """警告日志"""
        ...
    
    def error(self, message: str, **kwargs):
        """错误日志"""
        ...


class IMetricsService(Protocol):
    """指标监控服务接口"""
    
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """记录指标"""
        ...
    
    def increment_counter(self, name: str, tags: Optional[Dict[str, str]] = None):
        """增加计数器"""
        ...
    
    def record_timing(self, name: str, duration: float, tags: Optional[Dict[str, str]] = None):
        """记录时间指标"""
        ...