"""
MinSC - 工人单位
实现Worker类，具备采集资源能力
"""

import pygame
import math
import sys
import os
from typing import Optional, TYPE_CHECKING

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .unit import Unit, UnitType, UnitState, Command, CommandType
from engine.events import game_events  # 修复导入路径
from aop import logged, performance_monitored, transactional

if TYPE_CHECKING:
    from engine.map import ResourcePoint

class Worker(Unit):
    """工人单位 - 负责采集资源"""
    
    def __init__(self, x: int, y: int, player_id: int = 0):
        super().__init__(x, y, UnitType.WORKER, player_id)
        
        # 工人特有属性
        self.max_hp = 60
        self.current_hp = self.max_hp
        self.move_speed = 1.5
        self.size = 18
        
        # 采集相关
        self.carrying_resources = 0
        self.max_carry_capacity = 10
        self.gather_rate = 5  # 每秒采集量
        self.gather_range = 30
        
        # 当前采集目标
        self.gathering_target: Optional['ResourcePoint'] = None
        self.last_gathering_target: Optional['ResourcePoint'] = None  # 记住上次采集的资源点
        self.gather_timer = 0.0
        self.gather_interval = 1.0  # 每秒采集一次
        
        # 资源返回目标
        self.return_target = None  # 返回资源的建筑
        self.preferred_base = None  # 记住玩家指定的首选基地
        self.needs_return_to_base = False  # 标记是否需要返回基地
        
        # 引入状态机
        from .worker_fsm import WorkerStateMachine
        self.state_machine = WorkerStateMachine(self)
        
        # GameManager 引用（延迟设置）
        self._game_manager = None
        
        # 更新颜色 - 工人用更浅的蓝色
        self.color = self._get_worker_color()
    
    def set_game_manager(self, game_manager):
        """设置GameManager引用，启用IoC依赖注入"""
        self._game_manager = game_manager
        # 重新创建状态机以使用IoC
        if hasattr(self, 'state_machine'):
            from .worker_fsm import WorkerStateMachine
            old_state = getattr(self.state_machine, 'state', 'idle')
            self.state_machine = WorkerStateMachine(self, game_manager)
            # 尝试恢复状态
            if hasattr(self.state_machine, 'set_state'):
                try:
                    self.state_machine.set_state(old_state)
                except:
                    pass  # 如果恢复失败，保持默认状态
    
    def _get_worker_color(self) -> tuple[int, int, int]:
        """工人专用颜色"""
        base_colors = {
            0: (100, 150, 255),  # 浅蓝色 - 玩家1工人
            1: (255, 150, 100),  # 浅红色 - 玩家2工人
        }
        return base_colors.get(self.player_id, (150, 150, 150))
    
    def add_command(self, command: Command, queue: bool = False):
        """重写命令添加，处理采集记忆"""
        # 如果是移动或停止命令，清除采集记忆和首选基地
        if command.type in [CommandType.MOVE, CommandType.STOP]:
            self.last_gathering_target = None
            self.preferred_base = None  # 清除首选基地记忆
            self._stop_gathering()
        
        # 调用父类方法
        super().add_command(command, queue)
    
    def _execute_command(self, command: Command):
        """重写命令执行，添加采集命令支持"""
        if command.type == CommandType.GATHER:
            self._start_gather(command.target_object)
        elif command.type == CommandType.BUILD:
            self._start_return_resources(command.target_object)
        else:
            super()._execute_command(command)
    
    @logged
    @transactional
    def _start_gather(self, resource_point: 'ResourcePoint'):
        """开始采集资源"""
        if not resource_point or resource_point.amount <= 0:
            return
            
        print(f"🔨 工人{self.id} 前往采集资源点{resource_point.id} ({resource_point.x}, {resource_point.y})")
        
        # 中断当前状态，重新开始采集
        current_state = getattr(self.state_machine, 'state', 'idle')
        if current_state != 'idle':
            self.state_machine.stop()  # 先停止当前行为
        
        # 使用状态机管理采集
        self.state_machine.set_gather_target(resource_point)
        self.state_machine.start_gather()
        
        # 兼容旧代码
        self.gathering_target = resource_point
        self.last_gathering_target = resource_point
        distance = self.distance_to(resource_point.x, resource_point.y)
        if distance > self.gather_range:
            # 先移动到资源点
            self._start_move(resource_point.x, resource_point.y)
        else:
            # 直接开始采集
            self.state = UnitState.WORKING
    
    @performance_monitored
    def update(self, dt: float):
        """更新工人状态"""
        if not self.alive:
            return
        
        # 更新状态机
        self.state_machine.update(dt)
        
        # 更新基础逻辑
        super().update(dt)
        
        # 根据状态机状态更新采集逻辑
        if (self.state_machine.current_state == 'gathering' and 
            self.gathering_target):
            self._update_gathering(dt)
        
        # 检查是否需要开始采集（兼容旧代码）
        if (self.state == UnitState.IDLE and 
            self.gathering_target and 
            self.distance_to(self.gathering_target.x, self.gathering_target.y) <= self.gather_range):
            self.state = UnitState.WORKING
        
        # 检查是否需要卸载资源
        if (self.state == UnitState.IDLE and 
            self.return_target and 
            self.distance_to(self.return_target.x + self.return_target.size//2, 
                           self.return_target.y + self.return_target.size//2) <= 40):
            self._unload_resources()
    
    def _update_gathering(self, dt: float):
        """更新采集逻辑"""
        if not self.gathering_target or self.gathering_target.amount <= 0:
            self._stop_gathering()
            return
        
        # 检查距离
        distance = self.distance_to(self.gathering_target.x, self.gathering_target.y)
        if distance > self.gather_range:
            # 太远了，移动过去
            self._start_move(self.gathering_target.x, self.gathering_target.y)
            return
        
        # 检查负载是否已满
        if self.carrying_resources >= self.max_carry_capacity:
            self._stop_gathering()
            # 自动寻找最近的指挥中心返回资源
            self._auto_return_resources()
            return
        
        # 采集计时
        self.gather_timer += dt
        if self.gather_timer >= self.gather_interval:
            self.gather_timer = 0.0
            self._gather_resources()
    
    @performance_monitored
    @transactional
    def _gather_resources(self):
        """执行采集动作"""
        if not self.gathering_target:
            return
        
        # 计算本次采集量
        gather_amount = min(
            self.gather_rate,
            self.gathering_target.amount,
            self.max_carry_capacity - self.carrying_resources
        )
        
        if gather_amount > 0:
            # 从资源点扣除
            self.gathering_target.amount -= gather_amount
            # 工人携带
            self.carrying_resources += gather_amount
            
            print(f"🔨 工人{self.id} 采集了 {gather_amount} 资源 (携带: {self.carrying_resources}/{self.max_carry_capacity})")
            
            # 发送资源采集事件
            game_events.emit('resource_gathered', self, 
                           amount=gather_amount, 
                           player_id=self.player_id,
                           unit_id=self.id,
                           resource_point=self.gathering_target)
            
            # 资源点耗尽
            if self.gathering_target.amount <= 0:
                print(f"⛏️ 资源点{self.gathering_target.id} 已耗尽")
                self._stop_gathering()
    
    def _start_return_resources(self, building):
        """开始返回资源到建筑"""
        if not building or self.carrying_resources <= 0:
            return
            
        print(f"🚛 工人{self.id} 开始返回基地{building.id}，当前记忆采集目标: {self.last_gathering_target.id if self.last_gathering_target else 'None'}")
        
        self.return_target = building
        self.preferred_base = building  # 记住这个基地作为首选基地
        
        # 移动到建筑附近
        distance = self.distance_to(building.x + building.size//2, building.y + building.size//2)
        if distance > 40:  # 建筑交互范围
            # 先移动到建筑
            self._start_move(building.x + building.size//2, building.y + building.size//2)
        else:
            # 直接开始卸载
            self._unload_resources()
    
    def _unload_resources(self):
        """卸载资源"""
        if not self.return_target or self.carrying_resources <= 0:
            return
        
        # 检查建筑是否可以接受资源
        if hasattr(self.return_target, 'accept_resources'):
            unloaded = self.return_target.accept_resources(self)
            if unloaded > 0:
                print(f"🚛 工人{self.id} 卸载了 {unloaded} 资源到建筑{self.return_target.id}")
                
                # 发送资源运输事件
                game_events.emit('resource_delivered', self,
                               amount=unloaded,
                               player_id=self.player_id,
                               unit_id=self.id,
                               building_id=self.return_target.id)
        
        # 清除当前返回目标，但保留首选基地
        self.return_target = None
        self.state = UnitState.IDLE
        
        # 卸载完成后，如果有上次的采集目标且资源未耗尽，自动返回继续采集
        if self.last_gathering_target:
            print(f"🔍 工人{self.id} 检查上次采集目标: 资源点{self.last_gathering_target.id} 剩余={self.last_gathering_target.amount}")
            if self.last_gathering_target.amount > 0:
                print(f"♻️ 工人{self.id} 自动返回继续采集资源点{self.last_gathering_target.id}")
                self._start_gather(self.last_gathering_target)
            else:
                print(f"⛏️ 上次采集的资源点{self.last_gathering_target.id} 已耗尽")
        else:
            print(f"ℹ️ 工人{self.id} 卸载完成，等待新指令")
    
    def _auto_return_resources(self):
        """自动寻找最近的资源存储建筑返回资源"""
        # 需要通过游戏引擎找到最近的己方建筑
        print(f"💰 工人{self.id} 携带满载 ({self.carrying_resources}/{self.max_carry_capacity})，需要返回基地卸载")
        self.state = UnitState.IDLE
        self.needs_return_to_base = True  # 标记需要返回基地
    
    def set_return_target(self, building):
        """设置返回目标建筑"""
        if building and hasattr(building, 'accept_resources'):
            # 使用状态机管理返回
            self.state_machine.set_return_target(building)
            # 兼容旧代码
            command = Command(CommandType.BUILD, target_object=building)
            self.add_command(command)
    
    def _stop_gathering(self):
        """停止采集"""
        self.gathering_target = None
        self.last_gathering_target = None  # 清除记忆的采集目标
        self.state = UnitState.IDLE
        self.gather_timer = 0.0
    
    def _is_command_completed(self) -> bool:
        """检查命令是否完成"""
        if not self.current_command:
            return True
        
        if self.current_command.type == CommandType.GATHER:
            # 采集命令在以下情况完成：
            # 1. 资源耗尽
            # 2. 携带量满
            # 3. 手动停止
            return (not self.gathering_target or 
                   self.gathering_target.amount <= 0 or
                   self.carrying_resources >= self.max_carry_capacity or
                   self.state == UnitState.IDLE)
        
        return super()._is_command_completed()
    
    def can_gather(self, resource_point: 'ResourcePoint') -> bool:
        """检查是否可以采集指定资源点"""
        if not resource_point or resource_point.amount <= 0:
            return False
        
        # 移除距离限制，工人可以移动到任何有资源的点
        return True
    
    def drop_resources(self) -> int:
        """卸载资源，返回卸载的数量"""
        dropped = self.carrying_resources
        self.carrying_resources = 0
        return dropped
    
    def render(self, screen: pygame.Surface):
        """渲染工人"""
        super().render(screen)
        
        # 如果正在采集，渲染采集目标连线
        if self.gathering_target and self.state == UnitState.WORKING:
            start_pos = self.get_center()
            target_pos = (self.gathering_target.x, self.gathering_target.y)
            pygame.draw.line(screen, (255, 255, 0), start_pos, target_pos, 2)
        
        # 渲染携带资源信息
        if self.carrying_resources > 0:
            self._render_resource_indicator(screen)
    
    def _render_resource_indicator(self, screen: pygame.Surface):
        """渲染资源携带指示器"""
        # 在单位右上角显示小圆点表示携带资源
        indicator_x = self.x + self.size - 6
        indicator_y = self.y + 2
        
        # 根据携带量改变颜色
        fill_ratio = self.carrying_resources / self.max_carry_capacity
        if fill_ratio < 0.5:
            color = (255, 255, 0)  # 黄色
        elif fill_ratio < 0.8:
            color = (255, 165, 0)  # 橙色
        else:
            color = (255, 0, 0)    # 红色
        
        pygame.draw.circle(screen, color, (indicator_x, indicator_y), 4)
        pygame.draw.circle(screen, (0, 0, 0), (indicator_x, indicator_y), 4, 1)
    
    def get_info(self) -> dict:
        """获取工人信息"""
        info = super().get_info()
        info.update({
            "resources": f"{self.carrying_resources}/{self.max_carry_capacity}",
            "gathering": self.gathering_target is not None,
            "gather_target": f"({self.gathering_target.x}, {self.gathering_target.y})" if self.gathering_target else None
        })
        return info