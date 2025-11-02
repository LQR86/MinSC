"""
MinSC IoC/AOP 框架

提供依赖注入容器和面向切面编程支持
"""
from .container import (
    ApplicationContainer,
    GameContainer, 
    ECSContainer,
    get_container,
    wire_container,
    service_inject,
    # 便捷服务获取函数
    get_building_manager,
    get_unit_manager,
    get_game_state,
    get_event_bus,
    get_strategy_service,
    get_tactical_service,
    get_operational_service
)

from .services import (
    IBuildingManagerService,
    IUnitManagerService,
    IGameStateService,
    IEventBusService,
    IResourceManagerService,
    IConfigService,
    ILoggingService,
    IMetricsService,
    IStrategyService,
    ITacticalService,
    IOperationalService,
    BuildingType
)

__all__ = [
    # 容器相关
    'ApplicationContainer',
    'GameContainer',
    'ECSContainer', 
    'get_container',
    'wire_container',
    'service_inject',
    
    # 便捷服务获取
    'get_building_manager',
    'get_unit_manager',
    'get_game_state',
    'get_event_bus',
    'get_strategy_service',
    'get_tactical_service',
    'get_operational_service',
    
    # 服务接口
    'IBuildingManagerService',
    'IUnitManagerService', 
    'IGameStateService',
    'IEventBusService',
    'IResourceManagerService',
    'IConfigService',
    'ILoggingService',
    'IMetricsService',
    'IStrategyService',
    'ITacticalService',
    'IOperationalService',
    'BuildingType'
]