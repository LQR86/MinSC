"""
MinSC工人状态机
使用transitions库实现工人的复杂行为状态管理
解决自动循环采集问题

现在支持IoC依赖注入，解决基地查找问题
"""

from transitions import Machine
from typing import Optional, TYPE_CHECKING
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engine.events import game_events

# IoC 依赖注入支持
try:
    from ioc.services import IBuildingManagerService, BuildingType
    from ioc.container import get_building_manager
    IOC_AVAILABLE = True
except ImportError as e:
    IOC_AVAILABLE = False
    print(f"⚠️ IoC 服务不可用，使用传统方式: {e}")

if TYPE_CHECKING:
    from units.worker import Worker
    from engine.map import ResourcePoint
    from buildings.building import Building

# 导入单位状态枚举
from units.unit import UnitState


class WorkerStateMachine:
    """工人状态机管理器"""
    
    # 定义所有可能的状态
    states = [
        'idle',           # 空闲 - 等待指令
        'moving',         # 移动中 - 前往目标位置
        'gathering',      # 采集中 - 正在采集资源
        'carrying',       # 携带中 - 满载但还在采集点
        'returning',      # 返回中 - 携带资源返回基地
        'unloading',      # 卸载中 - 正在卸载资源
        'building',       # 建造中 - 正在建造建筑
        'dead'            # 死亡 - 单位销毁
    ]
    
    def __init__(self, worker: 'Worker', game_manager=None):
        self.worker = worker
        
        # 调试选项 - 必须在依赖注入之前定义
        self.debug_enabled = True
        
        # 状态机数据
        self.target_resource: Optional['ResourcePoint'] = None
        self.target_building: Optional['Building'] = None
        self.last_gathering_target: Optional['ResourcePoint'] = None
        self.preferred_base: Optional['Building'] = None
        
        # IoC 依赖注入
        self.building_manager: Optional['IBuildingManagerService'] = None
        self._setup_dependencies(game_manager)
        
        # 创建状态机
        self.machine = Machine(
            model=self,
            states=WorkerStateMachine.states,
            initial='idle',
            auto_transitions=False  # 禁用自动转换
        )
        
        # 定义状态转换
        self._setup_transitions()
    
    def _setup_transitions(self):
        """设置状态转换规则"""
        
        # 从空闲状态的转换
        self.machine.add_transition(
            trigger='start_gather',
            source='idle',
            dest='moving',
            conditions=['has_gather_target'],
            after='_on_start_moving_to_resource'
        )
        
        self.machine.add_transition(
            trigger='start_return',
            source='idle', 
            dest='moving',
            conditions=['has_return_target'],
            after='_on_start_moving_to_base'
        )
        
        self.machine.add_transition(
            trigger='start_build',
            source='idle',
            dest='building',
            conditions=['has_build_target']
        )
        
        # 移动状态的转换
        self.machine.add_transition(
            trigger='arrive_at_resource',
            source='moving',
            dest='gathering',
            conditions=['at_resource_point'],
            after='_on_start_gathering'
        )
        
        self.machine.add_transition(
            trigger='arrive_at_base',
            source='moving', 
            dest='unloading',
            conditions=['at_base_building'],
            after='_on_start_unloading'
        )
        
        # 采集状态的转换
        self.machine.add_transition(
            trigger='inventory_full',
            source='gathering',
            dest='carrying',
            conditions=['is_inventory_full'],
            after='_on_inventory_full'
        )
        
        self.machine.add_transition(
            trigger='resource_depleted',
            source='gathering',
            dest='idle',
            conditions=['is_resource_depleted'],
            after='_on_resource_depleted'
        )
        
        # 携带状态的转换
        self.machine.add_transition(
            trigger='start_return_auto',
            source='carrying',
            dest='returning',
            after='_on_auto_return'
        )
        
        # 返回状态的转换  
        self.machine.add_transition(
            trigger='arrive_at_base',
            source='returning',
            dest='unloading',
            conditions=['at_base_building'],
            after='_on_start_unloading'
        )
        
        # 卸载状态的转换
        self.machine.add_transition(
            trigger='unload_complete',
            source='unloading',
            dest='idle',
            after='_on_unload_complete'
        )
        
        # 通用转换
        self.machine.add_transition(
            trigger='stop',
            source='*',
            dest='idle',
            after='_on_stop'
        )
        
        self.machine.add_transition(
            trigger='die',
            source='*', 
            dest='dead'
        )
    
    # 条件检查方法
    def has_gather_target(self):
        """检查是否有采集目标"""
        return self.target_resource is not None
    
    def has_return_target(self):
        """检查是否有返回目标"""
        return self.target_building is not None and self.worker.carrying_resources > 0
    
    def has_build_target(self):
        """检查是否有建造目标"""
        return self.target_building is not None
    
    def at_resource_point(self):
        """检查是否在资源点附近"""
        if not self.target_resource:
            return False
        distance = self.worker.distance_to(self.target_resource.x, self.target_resource.y)
        return distance <= self.worker.gather_range
    
    def at_base_building(self):
        """检查是否在基地建筑附近"""
        if not self.target_building:
            return False
        distance = self.worker.distance_to(
            self.target_building.x + self.target_building.size//2, 
            self.target_building.y + self.target_building.size//2
        )
        return distance <= 40  # 建筑交互范围
    
    def is_inventory_full(self):
        """检查库存是否已满"""
        return self.worker.carrying_resources >= self.worker.max_carry_capacity
    
    def is_resource_depleted(self):
        """检查资源是否耗尽"""
        return self.target_resource and self.target_resource.amount <= 0
    
    # 状态转换后的动作
    def _on_start_moving_to_resource(self):
        """开始移动到资源点"""
        if self.target_resource:
            self.worker._start_move(self.target_resource.x, self.target_resource.y)
            self._debug_log(f"开始移动到资源点{self.target_resource.id}")
    
    def _on_start_moving_to_base(self):
        """开始移动到基地"""
        if self.target_building:
            self.worker._start_move(
                self.target_building.x + self.target_building.size//2,
                self.target_building.y + self.target_building.size//2
            )
            self._debug_log(f"开始返回基地{self.target_building.id}")
    
    def _on_start_gathering(self):
        """开始采集"""
        self.worker.gathering_target = self.target_resource
        self.last_gathering_target = self.target_resource  # 记住采集目标
        self._debug_log(f"开始采集资源点{self.target_resource.id}")
    
    def _on_inventory_full(self):
        """库存满载时"""
        self._debug_log("库存已满，准备返回基地")
        # 自动找到最近的基地
        self._find_nearest_base()
        if self.target_building:
            self.start_return_auto()
    
    def _on_auto_return(self) -> None:
        """自动返回基地"""
        self.worker.state = UnitState.MOVING  # 设置单位状态
        self._on_start_moving_to_base()
    
    def _on_start_unloading(self):
        """开始卸载"""
        self._debug_log(f"开始卸载到建筑{self.target_building.id}")
        # 实际卸载逻辑
        if hasattr(self.target_building, 'accept_resources'):
            unloaded = self.target_building.accept_resources(self.worker)
            if unloaded > 0:
                # 发送事件
                game_events.emit('resource_delivered', self.worker,
                               amount=unloaded,
                               player_id=self.worker.player_id,
                               unit_id=self.worker.id,
                               building_id=self.target_building.id)
        
        # 立即完成卸载
        self.unload_complete()
    
    def _on_unload_complete(self):
        """卸载完成"""
        self.target_building = None
        self._debug_log("卸载完成")
        
        # 关键：自动返回上次采集点继续采集
        if (self.last_gathering_target and 
            self.last_gathering_target.amount > 0):
            
            self._debug_log(f"自动返回继续采集资源点{self.last_gathering_target.id}")
            self.set_gather_target(self.last_gathering_target)
            self.start_gather()
        else:
            self._debug_log("没有可继续采集的资源点，进入空闲状态")
    
    def _on_resource_depleted(self):
        """资源耗尽"""
        self.target_resource = None
        self.last_gathering_target = None
        self.worker.gathering_target = None
        self._debug_log("资源点耗尽")
    
    def _on_stop(self) -> None:
        """停止所有行动"""
        self.target_resource = None
        self.target_building = None
        self.worker.gathering_target = None
        self.worker.state = UnitState.IDLE
        self._debug_log("停止行动，进入空闲状态")
    
    # 公共接口方法
    def set_gather_target(self, resource_point: 'ResourcePoint'):
        """设置采集目标"""
        self.target_resource = resource_point
        self._debug_log(f"设置采集目标: 资源点{resource_point.id}")
    
    def set_return_target(self, building: 'Building'):
        """设置返回目标"""
        self.target_building = building
        self.preferred_base = building  # 记住首选基地
        self._debug_log(f"设置返回目标: 建筑{building.id}")
    
    def update(self, dt: float):
        """状态机更新 - 检查状态转换条件"""
        # 安全获取当前状态，避免transitions库未初始化时的错误
        current_state = getattr(self, 'state', 'idle')
        
        if current_state == 'moving':
            # 检查是否到达目标
            if self.target_resource and self.at_resource_point():
                self.arrive_at_resource()
            elif self.target_building and self.at_base_building():
                self.arrive_at_base()
        
        elif current_state == 'gathering':
            # 检查是否满载或资源耗尽
            if self.is_inventory_full():
                self.inventory_full()
            elif self.is_resource_depleted():
                self.resource_depleted()
        
        elif current_state == 'carrying':
            # 自动开始返回基地
            self._find_nearest_base()
            if self.target_building:
                self.start_return_auto()
        
        elif current_state == 'returning':
            # 检查是否到达基地，准备卸载
            if self.target_building and self.at_base_building():
                self.arrive_at_base()
        
        elif current_state == 'unloading':
            # 卸载过程自动完成，通过回调触发下一步
            pass
    
    def _find_nearest_base(self) -> None:
        """找到最近的己方基地 - 使用IoC注入的服务"""
        # 优先使用首选基地
        if (self.preferred_base and 
            self.preferred_base.alive and 
            self.preferred_base.player_id == self.worker.player_id):
            self.target_building = self.preferred_base
            return
        
        # 使用 BuildingManagerService 查找最近基地
        if self.building_manager and IOC_AVAILABLE:
            try:
                nearest_base = self.building_manager.find_nearest_building(
                    position=(self.worker.x, self.worker.y),
                    building_type=BuildingType.COMMAND_CENTER,
                    player_id=self.worker.player_id
                )
                
                if nearest_base:
                    self.target_building = nearest_base
                    self._debug_log(f"IoC服务找到最近基地: {nearest_base.id}")
                    return
                else:
                    self._debug_log("IoC服务未找到可用基地")
            except Exception as e:
                self._debug_log(f"IoC服务查找基地失败: {e}")
        
        # 传统方式备用 (目前的问题：无法访问 GameManager)
        self._debug_log("需要实现寻找最近基地的逻辑 - 使用传统方式")
    
    def _setup_dependencies(self, game_manager=None):
        """设置依赖注入"""
        if IOC_AVAILABLE and game_manager:
            try:
                # 使用IoC容器获取建筑管理服务
                self.building_manager = get_building_manager()
                # 设置GameManager引用到游戏状态服务
                if hasattr(self.building_manager, 'game_state') and hasattr(self.building_manager.game_state, 'set_game_manager'):
                    self.building_manager.game_state.set_game_manager(game_manager)
                self._debug_log("✅ IoC依赖注入成功")
            except Exception as e:
                self._debug_log(f"❌ IoC依赖注入失败: {e}")
                self.building_manager = None
        else:
            self._debug_log("⚠️ IoC不可用或缺少GameManager")
            self.building_manager = None
    
    def _debug_log(self, message: str):
        """调试日志"""
        if self.debug_enabled:
            # 安全获取状态，避免transitions库未初始化时的错误
            current_state = getattr(self, 'state', 'unknown')
            print(f"🤖 工人{self.worker.id}状态机[{current_state}]: {message}")
    
    @property
    def current_state(self) -> str:
        """获取当前状态"""
        # 安全获取状态，如果transitions库未初始化则返回默认值
        return getattr(self, 'state', 'idle')


# 测试函数
def test_worker_state_machine():
    """测试工人状态机"""
    print("🧪 测试工人状态机...")
    
    # 模拟工人对象
    class MockWorker:
        def __init__(self):
            self.id = 1
            self.carrying_resources = 0
            self.max_carry_capacity = 10
            self.gather_range = 30
            self.UnitState = type('UnitState', (), {'IDLE': 0, 'MOVING': 1})()
            self.state = self.UnitState.IDLE
            
        def distance_to(self, x, y):
            return 25  # 模拟距离
            
        def _start_move(self, x, y):
            print(f"模拟移动到 ({x}, {y})")
    
    # 模拟资源点
    class MockResourcePoint:
        def __init__(self):
            self.id = 1
            self.x = 100
            self.y = 100
            self.amount = 50
    
    # 创建状态机
    worker = MockWorker()
    fsm = WorkerStateMachine(worker)
    
    # 测试状态转换
    assert fsm.current_state == 'idle'
    
    # 设置采集目标并开始采集
    resource = MockResourcePoint()
    fsm.set_gather_target(resource)
    fsm.start_gather()
    
    assert fsm.current_state == 'moving'
    print("✅ 工人状态机测试通过!")


if __name__ == "__main__":
    test_worker_state_machine()