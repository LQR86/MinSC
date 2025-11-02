# MinSC IoC/AOP 架构设计文档

## 1. 架构概览

### 1.1 设计目标
- 解决当前组件间的紧耦合问题（如 WorkerStateMachine 访问 GameManager.buildings）
- 为 MCP 接口和 AI 代理集成提供灵活的依赖管理
- 支持横切关注点的统一处理（日志、性能监控、事务等）
- 保持现有代码的兼容性，渐进式重构

### 1.2 技术选型
- **IoC 容器**: `dependency-injector` - 功能完整，类型提示友好
- **AOP 框架**: `aspectlib` - 纯 Python 实现，按需使用
- **集成策略**: 装饰器模式 + 服务定位器模式混合

## 2. IoC 容器设计

### 2.1 容器架构
```
MinSC Container
├── GameServices (游戏核心服务)
│   ├── GameStateService
│   ├── UnitManagerService  
│   ├── BuildingManagerService
│   ├── ResourceManagerService
│   └── EventBusService
├── ECS Services (ECS 相关服务)
│   ├── WorldService
│   ├── ComponentFactoryService
│   └── SystemManagerService
├── AI Services (AI 相关服务)
│   ├── StrategyService
│   ├── TacticalService
│   └── OperationalService
└── Infrastructure (基础设施服务)
    ├── ConfigService
    ├── LoggingService
    └── MetricsService
```

### 2.2 服务生命周期
- **Singleton**: GameStateService, EventBusService, ConfigService
- **Transient**: AI Decision Services, Temporary Calculators
- **Scoped**: Per-game session services

### 2.3 依赖注入策略
```python
# 构造函数注入 (推荐)
@inject
def __init__(self, 
             building_service: BuildingManagerService,
             event_bus: EventBusService):
    pass

# 属性注入 (兼容现有代码)
@inject
class WorkerStateMachine:
    building_service: BuildingManagerService = Provide[Container.game_services.building_manager]

# 方法注入 (按需使用)
@inject
def find_nearest_base(self, building_service: BuildingManagerService):
    pass
```

## 3. AOP 切面设计

### 3.1 切面类型
1. **性能监控切面** - 监控方法执行时间
2. **日志切面** - 自动记录方法调用
3. **事务切面** - 游戏状态变更的事务管理
4. **缓存切面** - 计算结果缓存
5. **权限切面** - AI 代理权限控制

### 3.2 切面应用策略
```python
# 装饰器方式（简单场景）
@performance_monitor
@log_calls
def expensive_calculation(self):
    pass

# 动态代理方式（复杂场景）
building_service = container.building_manager()
proxied_service = aop.wrap(building_service, [
    PerformanceAspect(),
    LoggingAspect(),
    CacheAspect()
])
```

## 4. 服务接口设计

### 4.1 核心服务接口

#### BuildingManagerService
```python
class IBuildingManagerService(Protocol):
    def get_buildings_by_player(self, player_id: int) -> List[Building]
    def find_nearest_building(self, position: Tuple[float, float], 
                            building_type: BuildingType,
                            player_id: int) -> Optional[Building]
    def get_buildings_in_range(self, center: Tuple[float, float], 
                             radius: float) -> List[Building]
```

#### UnitManagerService  
```python
class IUnitManagerService(Protocol):
    def get_units_by_player(self, player_id: int) -> List[Unit]
    def find_units_in_range(self, center: Tuple[float, float],
                           radius: float) -> List[Unit]
    def get_unit_by_id(self, unit_id: int) -> Optional[Unit]
```

#### GameStateService
```python
class IGameStateService(Protocol):
    def get_game_state(self) -> GameState
    def get_player_resources(self, player_id: int) -> Dict[str, int]
    def get_map_info(self) -> MapInfo
```

### 4.2 AI 决策服务接口

#### StrategyService (战略层)
```python
class IStrategyService(Protocol):
    def evaluate_game_situation(self) -> StrategicAssessment
    def recommend_strategy(self, player_id: int) -> StrategicPlan
    def adjust_long_term_goals(self, assessment: StrategicAssessment) -> None
```

#### TacticalService (战术层)  
```python
class ITacticalService(Protocol):
    def plan_resource_allocation(self, strategy: StrategicPlan) -> TacticalPlan
    def coordinate_unit_groups(self, units: List[Unit]) -> List[UnitGroup]
    def optimize_build_order(self, resources: Dict[str, int]) -> BuildOrder
```

#### OperationalService (操作层)
```python
class IOperationalService(Protocol):
    def execute_unit_command(self, unit: Unit, command: Command) -> bool
    def manage_worker_tasks(self, workers: List[Worker]) -> List[Task]
    def handle_immediate_threats(self, threats: List[Threat]) -> Response
```

## 5. 配置管理

### 5.1 配置结构
```yaml
# config/ioc_config.yaml
container:
  game_services:
    building_manager:
      provider: singleton
      implementation: game.services.BuildingManagerService
    unit_manager:
      provider: singleton  
      implementation: game.services.UnitManagerService
    
  ai_services:
    strategy:
      provider: transient
      implementation: ai.services.StrategyService
      
aspects:
  performance_monitoring:
    enabled: true
    targets: ["*.expensive_*", "ai.services.*"]
  
  logging:
    enabled: true
    level: INFO
    targets: ["game.services.*"]
```

### 5.2 动态配置热重载
```python
@config_reload_handler
def on_config_change(old_config, new_config):
    container.reload_services(new_config)
    aop_manager.reload_aspects(new_config.aspects)
```

## 6. 集成策略

### 6.1 渐进式重构计划

#### Phase 1: 核心服务抽取
- 创建 BuildingManagerService
- 重构 WorkerStateMachine 使用依赖注入
- 验证基本 IoC 功能

#### Phase 2: ECS 服务集成
- 将 ECS 组件集成到 IoC 容器
- 创建 ECS 相关服务接口
- 添加基础 AOP 支持

#### Phase 3: AI 服务架构
- 实现三层 AI 决策服务
- 集成 MCP 接口支持
- 完善 AOP 切面功能

#### Phase 4: 优化和完善
- 性能优化
- 配置管理完善
- 文档和测试补充

### 6.2 兼容性保证
```python
# 现有代码保持兼容
class WorkerStateMachine:
    def __init__(self, worker):
        self.worker = worker
        # 自动注入依赖，向后兼容
        container.wire(self)
    
    # 新的依赖注入方式
    building_service: IBuildingManagerService = Provide[Container.building_manager]
    
    def _find_nearest_base(self):
        # 使用注入的服务
        return self.building_service.find_nearest_building(
            (self.worker.x, self.worker.y),
            BuildingType.COMMAND_CENTER,
            self.worker.player_id
        )
```

## 7. 测试策略

### 7.1 单元测试
- 服务接口 Mock 测试
- 依赖注入测试
- AOP 切面功能测试

### 7.2 集成测试
- 容器装配测试
- 服务协作测试
- 性能基准测试

### 7.3 端到端测试
- 完整游戏场景测试
- AI 代理集成测试
- MCP 接口测试

## 8. 性能考虑

### 8.1 注入性能优化
- 编译时依赖解析
- 单例服务缓存
- 懒加载机制

### 8.2 AOP 性能优化
- 选择性切面应用
- 字节码缓存
- 热点方法优化

## 9. 监控和诊断

### 9.1 容器健康检查
- 服务注册状态
- 依赖关系图
- 循环依赖检测

### 9.2 AOP 执行监控
- 切面执行统计
- 性能影响分析
- 异常跟踪

## 10. 未来扩展

### 10.1 插件架构支持
- 动态服务注册
- 插件生命周期管理
- 热插拔支持

### 10.2 分布式支持
- 远程服务代理
- 服务发现机制
- 负载均衡

---

**文档版本**: v1.0  
**创建日期**: 2025-11-02  
**更新日期**: 2025-11-02  
**作者**: MinSC 开发团队