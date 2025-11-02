# MinSC技术架构设计

## 📋 架构概述

MinSC采用**轻量级混合架构**，结合Pygame基础引擎与精选的成熟组件，实现StarCraft风格的RTS游戏机制。

### 🎯 设计原则
- **轻量级优先**：总依赖控制在15MB以内
- **成熟组件**：选择各领域的稳定解决方案
- **松耦合设计**：组件可独立替换和升级
- **渐进式集成**：可以逐步引入，不影响现有功能

## 🏗️ 核心技术栈

### 基础引擎层
```
Pygame 2.x
├── 图形渲染 (pygame.display, pygame.draw)
├── 事件处理 (pygame.event)
├── 游戏循环 (pygame.time.Clock)
└── 基础碰撞 (pygame.sprite.collide_*)
```

### 游戏逻辑层
```
MinSC Game Logic
├── ECS组件系统 (esper)
├── 状态机管理 (transitions)
├── 事件总线 (blinker)
├── 寻路系统 (pathfinding)
├── 物理碰撞 (pymunk)
└── 网络通信 (websockets + asyncio)
```

## 🧩 组件详细设计

### 1. ECS组件系统 (esper)

**职责**：游戏对象的模块化管理

```python
# 组件定义
class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Health:
    def __init__(self, max_hp=100):
        self.max_hp = max_hp
        self.current_hp = max_hp

class GatheringAbility:
    def __init__(self, rate=5, capacity=10):
        self.gather_rate = rate
        self.carry_capacity = capacity
        self.carrying = 0

# 实体创建
worker_entity = world.create_entity(
    Position(100, 100),
    Health(60),
    GatheringAbility(5, 10)
)

# 系统处理
class MovementSystem(esper.Processor):
    def process(self):
        for ent, (pos, vel) in self.world.get_components(Position, Velocity):
            pos.x += vel.dx * dt
            pos.y += vel.dy * dt
```

**优势**：
- 模块化能力定义
- 高性能批量处理
- 易于扩展新单位类型

### 2. 状态机管理 (transitions)

**职责**：单位行为状态转换

```python
class WorkerStateMachine:
    states = [
        'idle',           # 空闲
        'moving',         # 移动中
        'gathering',      # 采集中
        'returning',      # 返回中
        'unloading',      # 卸载中
        'building',       # 建造中
        'attacking'       # 攻击中
    ]
    
    transitions = [
        # 触发器     源状态      目标状态     条件
        ['start_gather', 'idle', 'moving', 'has_target_resource'],
        ['arrive_at_resource', 'moving', 'gathering', 'at_resource_point'],
        ['inventory_full', 'gathering', 'returning', 'carrying_full'],
        ['arrive_at_base', 'returning', 'unloading', 'at_base'],
        ['unload_complete', 'unloading', 'idle', None],
        ['auto_return_gather', 'idle', 'moving', 'has_previous_target'],
    ]
    
    def __init__(self, worker):
        self.worker = worker
        self.machine = Machine(
            model=self,
            states=WorkerStateMachine.states,
            transitions=WorkerStateMachine.transitions,
            initial='idle'
        )
```

**优势**：
- 清晰的状态转换逻辑
- 支持条件检查和回调
- 可视化状态图生成

### 3. 事件总线 (blinker)

**职责**：系统间解耦通信

```python
from blinker import signal

# 定义游戏事件
game_events = {
    'unit_created': signal('unit-created'),
    'unit_died': signal('unit-died'),
    'resource_gathered': signal('resource-gathered'),
    'building_completed': signal('building-completed'),
    'battle_started': signal('battle-started'),
    'game_ended': signal('game-ended')
}

# 事件监听
@game_events['unit_died'].connect
def on_unit_death(sender, **kwargs):
    unit = kwargs['unit']
    position = kwargs['position']
    # 处理单位死亡逻辑
    update_player_stats(unit.player_id, 'unit_lost')
    spawn_death_effect(position)

@game_events['resource_gathered'].connect
def on_resource_collected(sender, **kwargs):
    amount = kwargs['amount']
    player_id = kwargs['player_id']
    # 更新资源统计
    update_player_resources(player_id, amount)

# 事件发送
game_events['unit_died'].send(
    self,
    unit=dead_unit,
    position=(dead_unit.x, dead_unit.y),
    cause='battle'
)
```

**优势**：
- 系统间松耦合
- 支持一对多通信
- 弱引用避免内存泄漏

### 4. 寻路系统 (pathfinding)

**职责**：智能单位导航

```python
from pathfinding.core.grid import Grid
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder

class PathfindingSystem:
    def __init__(self, map_width, map_height):
        self.grid = Grid(width=map_width//10, height=map_height//10)
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    
    def find_path(self, start_pos, end_pos, obstacles=None):
        # 更新障碍物
        if obstacles:
            self.update_obstacles(obstacles)
        
        # 坐标转换：像素 -> 网格
        start_grid = (start_pos[0]//10, start_pos[1]//10)
        end_grid = (end_pos[0]//10, end_pos[1]//10)
        
        # A*寻路
        path, runs = self.finder.find_path(
            self.grid.node(*start_grid),
            self.grid.node(*end_grid),
            self.grid
        )
        
        # 坐标转换：网格 -> 像素
        pixel_path = [(x*10, y*10) for x, y in path]
        return pixel_path
    
    def update_obstacles(self, obstacles):
        # 清除旧障碍
        self.grid.cleanup()
        # 添加新障碍
        for obs in obstacles:
            grid_x, grid_y = obs.x//10, obs.y//10
            self.grid.node(grid_x, grid_y).walkable = False
```

**优势**：
- 高效A*算法实现
- 支持动态障碍物
- 网格和像素坐标转换

### 5. 物理碰撞 (pymunk)

**职责**：精确碰撞检测和物理模拟

```python
import pymunk
import pymunk.pygame_util

class PhysicsSystem:
    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)  # RTS游戏无重力
        
        # 碰撞类型
        self.COLLISION_TYPES = {
            'unit': 1,
            'building': 2,
            'projectile': 3,
            'resource': 4
        }
    
    def add_unit(self, unit):
        # 创建物理体
        moment = pymunk.moment_for_circle(1, 0, unit.size/2)
        body = pymunk.Body(1, moment, body_type=pymunk.Body.KINEMATIC)
        body.position = unit.x, unit.y
        
        # 创建形状
        shape = pymunk.Circle(body, unit.size/2)
        shape.collision_type = self.COLLISION_TYPES['unit']
        shape.unit_ref = unit  # 反向引用
        
        self.space.add(body, shape)
        unit.physics_body = body
        return body
    
    def check_collisions(self):
        # 碰撞回调
        def unit_collision(arbiter, space, data):
            shape_a, shape_b = arbiter.shapes
            unit_a = shape_a.unit_ref
            unit_b = shape_b.unit_ref
            
            # 处理单位间碰撞
            self.handle_unit_collision(unit_a, unit_b)
            return True
        
        # 注册碰撞处理器
        handler = self.space.add_collision_handler(
            self.COLLISION_TYPES['unit'],
            self.COLLISION_TYPES['unit']
        )
        handler.begin = unit_collision
    
    def update(self, dt):
        self.space.step(dt)
```

**优势**：
- 高性能C++底层实现
- 精确的形状碰撞检测
- 与Pygame完美集成

### 6. 网络通信 (websockets + asyncio)

**职责**：多人游戏和AI接口

```python
import asyncio
import websockets
import json

class NetworkManager:
    def __init__(self):
        self.clients = set()
        self.game_state = {}
    
    async def register_client(self, websocket, path):
        self.clients.add(websocket)
        try:
            await self.handle_client(websocket)
        finally:
            self.clients.remove(websocket)
    
    async def handle_client(self, websocket):
        async for message in websocket:
            data = json.loads(message)
            await self.process_command(websocket, data)
    
    async def process_command(self, websocket, data):
        command_type = data.get('type')
        
        if command_type == 'move_unit':
            unit_id = data['unit_id']
            target_pos = data['target_position']
            # 处理移动指令
            self.game.move_unit(unit_id, target_pos)
        
        elif command_type == 'get_game_state':
            # 发送游戏状态
            await websocket.send(json.dumps(self.game_state))
    
    async def broadcast_event(self, event_data):
        if self.clients:
            await asyncio.gather(
                *[client.send(json.dumps(event_data)) for client in self.clients]
            )
```

**优势**：
- 现代异步编程
- WebSocket实时通信
- 易于调试和扩展

## 🔄 系统集成架构

### 游戏主循环集成
```python
class MinSCGame:
    def __init__(self):
        # 初始化各个系统
        self.world = esper.World()  # ECS世界
        self.physics = PhysicsSystem()  # 物理系统
        self.pathfinding = PathfindingSystem(1024, 768)  # 寻路
        self.network = NetworkManager()  # 网络
        
        # 注册ECS系统
        self.world.add_processor(MovementSystem())
        self.world.add_processor(GatheringSystem())
        self.world.add_processor(CombatSystem())
        
        # 注册事件监听
        self.setup_event_listeners()
    
    def update(self, dt):
        # ECS系统更新
        self.world.process(dt)
        
        # 物理系统更新
        self.physics.update(dt)
        
        # 状态机更新（通过ECS组件处理）
        for entity, (unit_comp,) in self.world.get_components(UnitComponent):
            if hasattr(unit_comp, 'state_machine'):
                unit_comp.state_machine.check_transitions()
```

### 渐进式迁移策略
1. **阶段1**：保持现有代码，引入blinker事件系统
2. **阶段2**：工人逻辑迁移到transitions状态机
3. **阶段3**：单位系统重构为ECS架构
4. **阶段4**：集成pymunk物理系统
5. **阶段5**：添加pathfinding寻路功能

## 📦 依赖管理

### requirements.txt
```txt
# 基础引擎
pygame>=2.5.0

# 核心组件
esper>=2.1.0          # ECS系统
transitions>=0.9.0     # 状态机
blinker>=1.6.0        # 事件系统
pathfinding>=1.0.0    # 寻路算法
pymunk>=6.5.0         # 物理引擎

# 网络通信
websockets>=12.0      # WebSocket服务器
asyncio               # 异步编程 (标准库)

# 开发工具
pytest>=7.0.0         # 单元测试
black>=23.0.0         # 代码格式化
mypy>=1.0.0           # 类型检查
```

### 安装脚本
```bash
# setup_dependencies.sh
#!/bin/bash

echo "正在安装MinSC核心依赖..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误：需要Python 3.8或更高版本，当前版本：$python_version"
    exit 1
fi

# 安装依赖
pip install -r requirements.txt

echo "✅ 依赖安装完成"
echo "📊 总大小：约15MB"
echo "🚀 运行: python launcher.py"
```

## 🎯 架构优势

### 1. **性能优化**
- pymunk的C++底层保证碰撞检测性能
- esper的批量处理优化游戏对象管理
- pathfinding的优化A*算法提供高效寻路

### 2. **开发效率**
- transitions提供可视化状态图，便于调试
- blinker的事件系统简化系统间通信
- 每个组件都有完整文档和示例

### 3. **可维护性**
- 松耦合设计，组件可独立测试
- 清晰的职责分离
- 渐进式迁移，降低重构风险

### 4. **扩展性**
- ECS架构支持轻松添加新功能
- 事件系统支持插件式扩展
- 网络架构支持多人游戏

这个架构既保持了轻量级的特点，又提供了实现复杂StarCraft机制所需的所有基础设施。