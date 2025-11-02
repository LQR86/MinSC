# MinSC IoC/AOP 实现指南

## 快速开始

### 1. 解决当前的 WorkerStateMachine 问题

当前问题：`WorkerStateMachine` 需要访问 `GameManager.buildings` 来寻找最近基地，但没有直接引用。

#### 解决方案概览
```python
# 1. 创建 BuildingManagerService
class IBuildingManagerService(Protocol):
    def find_nearest_base(self, worker_pos: Tuple[float, float], 
                         player_id: int) -> Optional[Building]

# 2. 在 WorkerStateMachine 中注入服务
class WorkerStateMachine:
    building_service: IBuildingManagerService = Provide[Container.building_manager]
    
    def _find_nearest_base(self):
        return self.building_service.find_nearest_base(
            (self.worker.x, self.worker.y),
            self.worker.player_id
        )
```

### 2. 项目结构调整

```
MinSC/src/
├── ioc/                    # IoC/AOP 框架
│   ├── __init__.py
│   ├── container.py        # DI 容器配置
│   ├── services.py         # 服务接口定义
│   └── aspects.py          # AOP 切面实现
├── services/               # 具体服务实现  
│   ├── __init__.py
│   ├── building_manager.py
│   ├── unit_manager.py
│   └── game_state.py
├── ai/                     # AI 服务
│   ├── strategy/
│   ├── tactical/
│   └── operational/
└── config/                 # 配置文件
    └── container_config.yaml
```

## 实现步骤

### Step 1: 安装依赖并创建基础结构
```bash
pip install dependency-injector aspectlib
```

### Step 2: 创建服务接口
先定义清晰的服务接口，然后实现具体服务类。

### Step 3: 配置 DI 容器
使用 dependency-injector 创建容器配置。

### Step 4: 重构现有代码
逐步将现有代码重构为使用依赖注入。

### Step 5: 添加 AOP 支持
按需添加切面功能，如日志、性能监控等。

## 优先级

1. **High Priority**: 解决 WorkerStateMachine 的基地查找问题
2. **Medium Priority**: 为 MCP 接口准备服务架构
3. **Low Priority**: 完善 AOP 切面功能

## 兼容性原则

- 现有代码必须继续工作
- 渐进式重构，不要一次性大改
- 保持 API 向后兼容
- 新功能优先使用 IoC/AOP 模式

---

这个实现指南将指导我们按步骤实现 IoC/AOP 架构。