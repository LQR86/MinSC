"""
MinSC 依赖注入容器配置

使用 dependency-injector 管理服务依赖关系
"""
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from .services import (
    IBuildingManagerService, 
    IUnitManagerService,
    IGameStateService,
    IEventBusService,
    IResourceManagerService,
    IConfigService,
    ILoggingService,
    IMetricsService,
    # AI服务接口
    IStrategyService,
    ITacticalService, 
    IOperationalService
)
from aop import initialize_aspects


class GameContainer(containers.DeclarativeContainer):
    """MinSC 游戏服务容器"""
    
    # 配置提供者
    config = providers.Configuration()
    
    # === 基础设施服务 ===
    
    # 配置服务 (单例)
    config_service = providers.Singleton(
        'services.config_service.ConfigService'
    )
    
    # 日志服务 (单例)
    logging_service = providers.Singleton(
        'services.logging_service.SimpleLoggingService',
        config=config_service
    )
    
    # 指标服务 (单例)
    metrics_service = providers.Singleton(
        'services.metrics_service.MetricsService',
        config=config_service
    )
    
    # 事件总线服务 (单例)
    event_bus_service = providers.Singleton(
        'services.event_bus_service.EventBusService'
    )
    
    # === 游戏核心服务 ===
    
    # 游戏状态服务 (单例)
    game_state_service = providers.Singleton(
        'services.game_state_service.GameStateService',
        event_bus=event_bus_service
    )
    
    # 建筑管理服务 (单例)
    building_manager_service = providers.Singleton(
        'services.building_manager_service.BuildingManagerService',
        game_state=game_state_service,
        event_bus=event_bus_service,
        logging=logging_service
    )
    
    # 单位管理服务 (单例)
    unit_manager_service = providers.Singleton(
        'services.unit_manager_service.UnitManagerService',
        game_state=game_state_service,
        event_bus=event_bus_service,
        logging=logging_service
    )
    
    # 资源管理服务 (单例)
    resource_manager_service = providers.Singleton(
        'services.resource_manager_service.ResourceManagerService',
        game_state=game_state_service,
        event_bus=event_bus_service
    )
    
    # === AI 决策服务 ===
    
    # 战略服务 (瞬态 - 每次调用创建新实例)
    strategy_service = providers.Factory(
        'services.ai.strategy_service.StrategyService',
        game_state=game_state_service,
        building_manager=building_manager_service,
        unit_manager=unit_manager_service,
        logging=logging_service
    )
    
    # 战术服务 (瞬态)
    tactical_service = providers.Factory(
        'services.ai.tactical_service.TacticalService',
        strategy=strategy_service,
        building_manager=building_manager_service,
        unit_manager=unit_manager_service,
        resource_manager=resource_manager_service,
        logging=logging_service
    )
    
    # 操作服务 (瞬态)
    operational_service = providers.Factory(
        'services.ai.operational_service.OperationalService',
        tactical=tactical_service,
        unit_manager=unit_manager_service,
        event_bus=event_bus_service,
        logging=logging_service
    )


class ECSContainer(containers.DeclarativeContainer):
    """ECS 相关服务容器"""
    
    # ECS World 服务 (单例)
    world_service = providers.Singleton(
        'services.ecs.world_service.WorldService'
    )
    
    # 组件工厂服务 (单例)
    component_factory_service = providers.Singleton(
        'services.ecs.component_factory_service.ComponentFactoryService'
    )
    
    # 系统管理服务 (单例)
    system_manager_service = providers.Singleton(
        'services.ecs.system_manager_service.SystemManagerService',
        world=world_service
    )


class ApplicationContainer(containers.DeclarativeContainer):
    """应用程序主容器"""
    
    # 包含子容器
    game = providers.DependenciesContainer()
    ecs = providers.DependenciesContainer()
    
    # 应用配置
    config = providers.Configuration()
    
    # 根据配置初始化子容器
    @classmethod
    def initialize(cls, config_path: str = None):
        """初始化容器"""
        container = cls()
        
        # 加载配置
        if config_path:
            container.config.from_yaml(config_path)
        
        # 设置子容器
        container.game.override(GameContainer())
        container.ecs.override(ECSContainer())
        
        # 配置子容器
        if config_path:
            container.game().config.from_yaml(config_path, required=False)
        
        # 初始化AOP切面
        initialize_aspects(container.game().logging_service())
            
        return container


# 全局容器实例
container: ApplicationContainer = None


def get_container() -> ApplicationContainer:
    """获取全局容器实例"""
    global container
    if container is None:
        container = ApplicationContainer.initialize()
    return container


def wire_container(modules: list = None):
    """装配容器到指定模块"""
    if modules is None:
        modules = [
            'units.worker_fsm',
            'main',
            'ecs.systems'
        ]
    
    container = get_container()
    container.wire(modules=modules)


# 便捷的注入装饰器
def service_inject(func):
    """服务注入装饰器"""
    return inject(func)


# 便捷的服务获取函数
def get_building_manager() -> IBuildingManagerService:
    """获取建筑管理服务"""
    return get_container().game().building_manager_service()


def get_unit_manager() -> IUnitManagerService:
    """获取单位管理服务"""
    return get_container().game().unit_manager_service()


def get_game_state() -> IGameStateService:
    """获取游戏状态服务"""
    return get_container().game().game_state_service()


def get_event_bus() -> IEventBusService:
    """获取事件总线服务"""
    return get_container().game().event_bus_service()


def get_strategy_service() -> IStrategyService:
    """获取战略服务"""
    return get_container().game().strategy_service()


def get_tactical_service() -> ITacticalService:
    """获取战术服务"""
    return get_container().game().tactical_service()


def get_operational_service() -> IOperationalService:
    """获取操作服务"""
    return get_container().game().operational_service()