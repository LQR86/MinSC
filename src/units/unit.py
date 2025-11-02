"""
MinSC - 基础单位系统
实现基础Unit类，支持移动、选择、基础AI
"""

import pygame
import math
from typing import Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum

# 单位类型枚举
class UnitType(Enum):
    WORKER = "worker"
    WARRIOR = "warrior"
    BUILDER = "builder"

# 单位状态枚举
class UnitState(Enum):
    IDLE = "idle"
    MOVING = "moving"
    WORKING = "working"
    ATTACKING = "attacking"
    DEAD = "dead"

# 单位命令类型
class CommandType(Enum):
    MOVE = "move"
    ATTACK = "attack"
    GATHER = "gather"
    BUILD = "build"
    STOP = "stop"

@dataclass
class Command:
    """单位命令"""
    type: CommandType
    target: Optional[Tuple[int, int]] = None
    target_object: Optional[object] = None
    priority: int = 1

class Unit:
    """基础单位类"""
    
    _next_id = 1  # 类变量，用于生成唯一ID
    
    def __init__(self, 
                 x: int, 
                 y: int, 
                 unit_type: UnitType,
                 player_id: int = 0):
        # 基本属性
        self.id = Unit._next_id
        Unit._next_id += 1
        self.x = x
        self.y = y
        self.unit_type = unit_type
        self.player_id = player_id
        
        # 状态管理
        self.state = UnitState.IDLE
        self.selected = False
        self.alive = True
        
        # 基础属性（可被子类重写）
        self.max_hp = 100
        self.current_hp = self.max_hp
        self.move_speed = 2.0
        self.size = 20
        
        # 移动系统
        self.target_x = x
        self.target_y = y
        self.path: List[Tuple[int, int]] = []
        
        # 命令队列
        self.command_queue: List[Command] = []
        self.current_command: Optional[Command] = None
        
        # 渲染属性
        self.color = self._get_unit_color()
        self.selected_color = (255, 255, 0)  # 黄色选择框
        
    def _get_unit_color(self) -> Tuple[int, int, int]:
        """根据玩家ID和单位类型获取颜色"""
        base_colors = {
            0: (0, 100, 255),    # 蓝色 - 玩家1
            1: (255, 100, 0),    # 红色 - 玩家2
        }
        return base_colors.get(self.player_id, (128, 128, 128))
    
    def get_position(self) -> Tuple[int, int]:
        """获取单位位置"""
        return (int(self.x), int(self.y))
    
    def get_center(self) -> Tuple[int, int]:
        """获取单位中心点"""
        return (int(self.x + self.size // 2), int(self.y + self.size // 2))
    
    def distance_to(self, target_x: int, target_y: int) -> float:
        """计算到目标位置的距离"""
        dx = target_x - self.x
        dy = target_y - self.y
        return math.sqrt(dx * dx + dy * dy)
    
    def add_command(self, command: Command, queue: bool = False):
        """添加命令到队列"""
        if not queue:
            # 清空现有命令队列
            self.command_queue.clear()
            self.current_command = None
        
        self.command_queue.append(command)
        
        # 如果没有当前命令，立即执行
        if self.current_command is None:
            self._process_next_command()
    
    def _process_next_command(self):
        """处理下一个命令"""
        if self.command_queue:
            self.current_command = self.command_queue.pop(0)
            self._execute_command(self.current_command)
    
    def _execute_command(self, command: Command):
        """执行命令"""
        if command.type == CommandType.MOVE:
            self._start_move(command.target[0], command.target[1])
        elif command.type == CommandType.STOP:
            self._stop()
        # 其他命令类型在子类中实现
        
    def _start_move(self, target_x: int, target_y: int):
        """开始移动到目标位置"""
        self.target_x = target_x
        self.target_y = target_y
        self.state = UnitState.MOVING
        
        # 简单的直线路径（可以后续升级为A*寻路）
        self.path = [(target_x, target_y)]
    
    def _stop(self):
        """停止所有动作"""
        self.state = UnitState.IDLE
        self.current_command = None
        self.command_queue.clear()
        self.path.clear()
    
    def update(self, dt: float):
        """更新单位状态"""
        if not self.alive:
            return
            
        # 处理移动
        if self.state == UnitState.MOVING:
            self._update_movement(dt)
        
        # 处理当前命令完成
        if self.current_command and self._is_command_completed():
            self.current_command = None
            self._process_next_command()
    
    def _update_movement(self, dt: float):
        """更新移动逻辑"""
        if not self.path:
            self.state = UnitState.IDLE
            return
        
        target_x, target_y = self.path[0]
        distance = self.distance_to(target_x, target_y)
        
        # 到达目标点
        if distance < 5:
            self.x = target_x
            self.y = target_y
            self.path.pop(0)
            
            if not self.path:
                self.state = UnitState.IDLE
                return
        else:
            # 向目标移动
            direction_x = (target_x - self.x) / distance
            direction_y = (target_y - self.y) / distance
            
            move_distance = self.move_speed * dt * 60  # 60fps base
            self.x += direction_x * move_distance
            self.y += direction_y * move_distance
    
    def _is_command_completed(self) -> bool:
        """检查当前命令是否完成"""
        if not self.current_command:
            return True
            
        if self.current_command.type == CommandType.MOVE:
            return self.state != UnitState.MOVING
        
        return False
    
    def select(self):
        """选择单位"""
        self.selected = True
    
    def deselect(self):
        """取消选择单位"""
        self.selected = False
    
    def contains_point(self, x: int, y: int) -> bool:
        """检查点是否在单位内"""
        return (self.x <= x <= self.x + self.size and
                self.y <= y <= self.y + self.size)
    
    def take_damage(self, damage: int):
        """受到伤害"""
        self.current_hp -= damage
        if self.current_hp <= 0:
            self.current_hp = 0
            self.alive = False
            self.state = UnitState.DEAD
    
    def heal(self, amount: int):
        """治疗"""
        self.current_hp = min(self.current_hp + amount, self.max_hp)
    
    def render(self, screen: pygame.Surface):
        """渲染单位"""
        if not self.alive:
            return
            
        # 渲染单位主体
        pygame.draw.rect(screen, self.color, 
                        (self.x, self.y, self.size, self.size))
        
        # 渲染选择框
        if self.selected:
            pygame.draw.rect(screen, self.selected_color,
                           (self.x - 2, self.y - 2, self.size + 4, self.size + 4), 2)
        
        # 渲染血条
        if self.current_hp < self.max_hp:
            self._render_health_bar(screen)
        
        # 渲染移动路径
        if self.path and self.selected:
            self._render_path(screen)
    
    def _render_health_bar(self, screen: pygame.Surface):
        """渲染血条"""
        bar_width = self.size
        bar_height = 4
        bar_y = self.y - 8
        
        # 背景
        pygame.draw.rect(screen, (255, 0, 0),
                        (self.x, bar_y, bar_width, bar_height))
        
        # 血量
        health_ratio = self.current_hp / self.max_hp
        health_width = int(bar_width * health_ratio)
        pygame.draw.rect(screen, (0, 255, 0),
                        (self.x, bar_y, health_width, bar_height))
    
    def _render_path(self, screen: pygame.Surface):
        """渲染移动路径"""
        if not self.path:
            return
            
        start_pos = self.get_center()
        
        for target_x, target_y in self.path:
            # 绘制路径线
            pygame.draw.line(screen, (255, 255, 255), start_pos, (target_x, target_y), 2)
            # 绘制目标点
            pygame.draw.circle(screen, (255, 255, 255), (target_x, target_y), 5, 2)
            start_pos = (target_x, target_y)
    
    def get_info(self) -> dict:
        """获取单位信息"""
        return {
            "id": id(self),
            "type": self.unit_type.value,
            "player": self.player_id,
            "position": self.get_position(),
            "hp": f"{self.current_hp}/{self.max_hp}",
            "state": self.state.value,
            "selected": self.selected
        }
    
    def __str__(self):
        return f"{self.unit_type.value}({self.player_id}) at ({self.x:.1f}, {self.y:.1f})"