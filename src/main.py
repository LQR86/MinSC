"""
MinSC Main - 游戏入口文件
集成所有系统的主游戏实例，包括单位系统
"""

import sys
import os
import pygame
from typing import List, Optional

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engine.game import Game, GameState
from engine.map import Map
from engine.events import game_events, on_event  # 引入事件系统
from units.worker import Worker
from units.unit import Unit, Command, CommandType
from buildings.command_center import CommandCenter
from buildings.building import Building, BuildingState

class MinSCGame(Game):
    """MinSC完整游戏类，继承自基础Game类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_map: Map = None
        
        # 单位系统
        self.units: List[Unit] = []
        self.selected_units: List[Unit] = []
        
        # 建筑系统
        self.buildings: List[Building] = []
        self.selected_buildings: List[Building] = []
        
        # 交互状态
        self.selection_start = None  # 框选起始点
        self.is_selecting = False    # 是否正在框选
        
        # 设置事件监听器
        self._setup_event_listeners()
    
    def _setup_event_listeners(self):
        """设置游戏事件监听器"""
        # 监听单位相关事件
        game_events.connect('unit_created', self._on_unit_created)
        game_events.connect('unit_died', self._on_unit_died)
        game_events.connect('unit_selected', self._on_unit_selected)
        
        # 监听建筑相关事件
        game_events.connect('building_created', self._on_building_created)
        game_events.connect('production_completed', self._on_production_completed)
        
        # 监听资源相关事件
        game_events.connect('resource_gathered', self._on_resource_gathered)
        game_events.connect('resource_delivered', self._on_resource_delivered)
    
    def _on_unit_created(self, sender, **kwargs):
        """处理单位创建事件"""
        unit = kwargs.get('unit')
        if unit and unit not in self.units:
            self.units.append(unit)
            print(f"📡 事件: 单位{unit.id}创建成功")
    
    def _on_unit_died(self, sender, **kwargs):
        """处理单位死亡事件"""
        unit = kwargs.get('unit')
        if unit and unit in self.units:
            self.units.remove(unit)
            if unit in self.selected_units:
                self.selected_units.remove(unit)
            print(f"📡 事件: 单位{unit.id}死亡")
    
    def _on_unit_selected(self, sender, **kwargs):
        """处理单位选择事件"""
        unit = kwargs.get('unit')
        if unit and unit not in self.selected_units:
            self.selected_units.append(unit)
    
    def _on_building_created(self, sender, **kwargs):
        """处理建筑创建事件"""
        building = kwargs.get('building')
        if building and building not in self.buildings:
            self.buildings.append(building)
            print(f"📡 事件: 建筑{building.id}创建成功")
    
    def _on_production_completed(self, sender, **kwargs):
        """处理生产完成事件"""
        unit_info = kwargs.get('unit_info')
        if unit_info:
            new_unit = self._create_unit_from_info(unit_info)
            if new_unit:
                # 通过事件系统通知单位创建
                game_events.emit('unit_created', self, unit=new_unit)
    
    def _on_resource_gathered(self, sender, **kwargs):
        """处理资源采集事件"""
        amount = kwargs.get('amount', 0)
        player_id = kwargs.get('player_id', 0)
        print(f"📡 事件: 玩家{player_id}采集了{amount}资源")
    
    def _on_resource_delivered(self, sender, **kwargs):
        """处理资源运输事件"""
        amount = kwargs.get('amount', 0)
        player_id = kwargs.get('player_id', 0)
        print(f"📡 事件: 玩家{player_id}运输了{amount}资源")

    def initialize(self) -> bool:
        """扩展初始化，添加游戏系统"""
        if not super().initialize():
            return False
        
        try:
            # 初始化地图系统
            self.game_map = Map(width=self.width, height=self.height)
            print("✅ 地图系统初始化成功")
            
            # 初始化单位系统
            self._create_initial_units()
            print("✅ 单位系统初始化成功")
            
            # 初始化建筑系统
            self._create_initial_buildings()
            print("✅ 建筑系统初始化成功")
            
            # TODO: 初始化其他系统
            # - 建筑系统
            # - AI系统
            # - MCP接口
            
            return True
            
        except Exception as e:
            print(f"❌ 游戏系统初始化失败: {e}")
            return False
    
    def _create_initial_units(self):
        """创建初始单位"""
        # 玩家1工人
        worker1 = Worker(100, 100, player_id=0)
        worker2 = Worker(150, 150, player_id=0)
        
        # 玩家2工人
        worker3 = Worker(800, 600, player_id=1)
        # 玩家2工人靠近玩家1基地，用于测试所有权检查
        worker4 = Worker(120, 80, player_id=1)
        
        # 设置GameManager引用，启用IoC依赖注入
        self._setup_ioc_container()
        for worker in [worker1, worker2, worker3, worker4]:
            if hasattr(worker, 'set_game_manager'):
                worker.set_game_manager(self)
        
        self.units.extend([worker1, worker2, worker3, worker4])
        print(f"🔨 创建了 {len(self.units)} 个初始单位（已启用IoC依赖注入）")
    
    def _setup_ioc_container(self):
        """设置IoC容器"""
        try:
            from ioc.container import get_container, wire_container
            # 初始化容器
            container = get_container()
            # 装配依赖
            wire_container(['units.worker_fsm'])
            print("✅ IoC容器初始化成功")
        except Exception as e:
            print(f"⚠️ IoC容器初始化失败: {e}")
    
    def _create_initial_buildings(self):
        """创建初始建筑"""
        # 玩家1指挥中心
        cc1 = CommandCenter(50, 50, player_id=0)
        
        # 玩家2指挥中心
        cc2 = CommandCenter(850, 650, player_id=1)
        
        self.buildings.extend([cc1, cc2])
        print(f"🏗️ 创建了 {len(self.buildings)} 个初始建筑")
    
    def _create_unit_from_info(self, unit_info: dict) -> Optional[Unit]:
        """根据单位信息创建单位实例"""
        unit_type = unit_info.get("type")
        position = unit_info.get("position", (0, 0))
        player_id = unit_info.get("player_id", 0)
        
        if unit_type == "worker":
            return Worker(position[0], position[1], player_id)
        # 可以在这里添加其他单位类型
        
        return None
    
    def handle_events(self) -> None:
        """重写事件处理，不调用父类避免重复处理"""
        # 直接处理pygame事件，不调用super()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.state == GameState.RUNNING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.RUNNING
                elif self.state == GameState.RUNNING:
                    self._handle_key_press(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == GameState.RUNNING:
                    self._handle_mouse_click(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.state == GameState.RUNNING:
                    self._handle_mouse_release(event)
            elif event.type == pygame.MOUSEMOTION:
                if self.state == GameState.RUNNING and self.is_selecting:
                    self._handle_mouse_drag(event)
    
    def _handle_mouse_click(self, event):
        """处理鼠标点击"""
        mx, my = event.pos
        
        if event.button == 1:  # 左键
            # 开始选择
            self.selection_start = (mx, my)
            self.is_selecting = True
            
            # 检查点击的单位或建筑
            clicked_unit = self._get_unit_at_position(mx, my)
            clicked_building = self._get_building_at_position(mx, my)
            
            if clicked_unit:
                # 点击了单位
                if not pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    # 非Shift点击，清空选择
                    self._clear_selection()
                
                clicked_unit.select()
                if clicked_unit not in self.selected_units:
                    self.selected_units.append(clicked_unit)
            elif clicked_building:
                # 点击了建筑
                if not pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    # 非Shift点击，清空选择
                    self._clear_selection()
                
                clicked_building.select()
                if clicked_building not in self.selected_buildings:
                    self.selected_buildings.append(clicked_building)
            else:
                # 点击空地，如果没有按Shift则清空选择
                if not pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    self._clear_selection()
        
        elif event.button == 3:  # 右键
            # 下达命令
            if self.selected_units:
                self._issue_command(mx, my)
    
    def _handle_mouse_release(self, event):
        """处理鼠标释放"""
        if event.button == 1 and self.is_selecting:  # 左键释放
            self.is_selecting = False
            
            # 框选单位
            if self.selection_start:
                self._select_units_in_rectangle()
            
            self.selection_start = None
    
    def _handle_key_press(self, event):
        """处理键盘按键"""
        if event.key == pygame.K_w:
            # W键：生产工人
            for building in self.selected_buildings:
                if isinstance(building, CommandCenter):
                    if building.produce_worker():
                        print(f"🏭 指挥中心开始生产工人")
                    else:
                        print(f"❌ 无法生产工人（队列已满或资源不足）")
        elif event.key == pygame.K_s:
            # S键：停止生产
            for building in self.selected_buildings:
                if hasattr(building, 'production_queue'):
                    building.production_queue.clear()
                    building.current_production = None
                    building.state = BuildingState.IDLE
                    print(f"🛑 停止生产")
    
    def _handle_mouse_drag(self, event):
        """处理鼠标拖拽"""
        # 框选逻辑在渲染时处理显示
        pass
    
    def _get_building_at_position(self, x: int, y: int) -> Optional[Building]:
        """获取指定位置的建筑"""
        for building in self.buildings:
            if building.alive and building.contains_point(x, y):
                return building
        return None
    
    def _get_unit_at_position(self, x: int, y: int) -> Optional[Unit]:
        """获取指定位置的单位"""
        for unit in self.units:
            if unit.alive and unit.contains_point(x, y):
                return unit
        return None
    
    def _select_units_in_rectangle(self):
        """框选矩形区域内的单位"""
        if not self.selection_start:
            return
        
        mx, my = pygame.mouse.get_pos()
        start_x, start_y = self.selection_start
        
        # 计算矩形
        min_x = min(start_x, mx)
        max_x = max(start_x, mx)
        min_y = min(start_y, my)
        max_y = max(start_y, my)
        
        # 只有矩形足够大才框选
        if abs(max_x - min_x) > 10 and abs(max_y - min_y) > 10:
            if not pygame.key.get_pressed()[pygame.K_LSHIFT]:
                self._clear_selection()
            
            for unit in self.units:
                if (unit.alive and
                    min_x <= unit.x <= max_x and
                    min_y <= unit.y <= max_y):
                    unit.select()
                    if unit not in self.selected_units:
                        self.selected_units.append(unit)
    
    def _clear_selection(self):
        """清空选择"""
        for unit in self.selected_units:
            unit.deselect()
        self.selected_units.clear()
        
        for building in self.selected_buildings:
            building.deselect()
        self.selected_buildings.clear()
    
    def _issue_command(self, target_x: int, target_y: int):
        """向选中单位下达命令"""
        # 检查是否点击了建筑
        target_building = self._get_building_at_position(target_x, target_y)
        
        if target_building:
            # 对建筑下达命令
            for unit in self.selected_units:
                if isinstance(unit, Worker) and unit.carrying_resources > 0:
                    # 工人携带资源，尝试卸载
                    if hasattr(target_building, 'accept_resources'):
                        unit.set_return_target(target_building)
                        print(f"🚛 工人前往卸载资源到 {target_building.building_type.value}")
        else:
            # 检查是否点击了资源点
            if self.game_map:
                resource_point = self.game_map.get_resource_at_position(target_x, target_y)
                
                if resource_point:
                    # 采集命令
                    for unit in self.selected_units:
                        if isinstance(unit, Worker) and unit.can_gather(resource_point):
                            command = Command(CommandType.GATHER, target_object=resource_point)
                            unit.add_command(command)
                            print(f"🔨 工人{unit.id} 前往采集资源点{resource_point.id} ({target_x}, {target_y})")
                else:
                    # 移动命令
                    for unit in self.selected_units:
                        command = Command(CommandType.MOVE, target=(target_x, target_y))
                        unit.add_command(command)
                        print(f"📍 单位{unit.id} 移动到 ({target_x}, {target_y})")
    
    def _auto_return_worker_to_base(self, worker):
        """自动让满载的工人返回最近的己方基地"""
        if not hasattr(worker, 'player_id'):
            return
        
        # 优先使用工人记住的首选基地
        if (hasattr(worker, 'preferred_base') and 
            worker.preferred_base and 
            worker.preferred_base.player_id == worker.player_id and
            hasattr(worker.preferred_base, 'can_accept_resources') and
            worker.preferred_base.can_accept_resources()):
            
            worker.needs_return_to_base = False
            worker._start_return_resources(worker.preferred_base)
            print(f"🚛 工人{worker.id} 返回首选基地{worker.preferred_base.id}")
            return
        
        # 如果没有首选基地或首选基地不可用，查找最近的己方指挥中心
        nearest_base = None
        min_distance = float('inf')
        
        for building in self.buildings:
            if (building.building_type.value == 'command_center' and 
                building.player_id == worker.player_id and
                hasattr(building, 'can_accept_resources') and
                building.can_accept_resources()):
                
                distance = worker.distance_to(building.x + building.size//2, 
                                            building.y + building.size//2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_base = building
        
        if nearest_base:
            # 清除需要返回基地的标记
            worker.needs_return_to_base = False
            # 发送返回命令
            worker._start_return_resources(nearest_base)
            print(f"🚛 工人{worker.id} 自动返回最近基地{nearest_base.id} (距离: {min_distance:.1f})")
        else:
            print(f"⚠️ 未找到可用的己方基地")
    
    def update(self, delta_time: float) -> None:
        """扩展游戏逻辑更新"""
        super().update(delta_time)
        
        if self.state != GameState.RUNNING:
            return
        
        # 更新所有单位
        for unit in self.units[:]:  # 使用切片复制，避免迭代时修改列表
            unit.update(delta_time)
            
            # 检查工人是否需要自动返回基地
            if (hasattr(unit, 'needs_return_to_base') and 
                unit.needs_return_to_base and 
                unit.carrying_resources > 0):
                self._auto_return_worker_to_base(unit)
            
            # 移除死亡单位
            if not unit.alive:
                if unit in self.selected_units:
                    self.selected_units.remove(unit)
                self.units.remove(unit)
        
        # 更新所有建筑
        for building in self.buildings[:]:
            building.update(delta_time)
            
            # 检查是否有生产完成的单位
            if (hasattr(building, 'current_production') and 
                building.current_production and 
                building.current_production.remaining_time <= 0):
                
                # 生产完成，创建新单位
                unit_info = building._complete_production()
                if unit_info:
                    new_unit = self._create_unit_from_info(unit_info)
                    if new_unit:
                        self.units.append(new_unit)
            
            # 移除被摧毁的建筑
            if not building.alive:
                if building in self.selected_buildings:
                    self.selected_buildings.remove(building)
                self.buildings.remove(building)
    
    def render(self) -> None:
        """扩展渲染系统"""
        if not self.screen:
            return
        
        # 清空屏幕
        self.screen.fill(self.BLACK)
        
        if self.state == GameState.RUNNING:
            # 渲染地图
            if self.game_map:
                self.game_map.render(self.screen)
            
            # 渲染建筑
            for building in self.buildings:
                building.render(self.screen)
            
            # 渲染单位
            for unit in self.units:
                unit.render(self.screen)
            
            # 渲染选择框
            if self.is_selecting and self.selection_start:
                self._render_selection_box()
            
            # 渲染游戏信息
            self._render_game_info()
            
        elif self.state == GameState.PAUSED:
            # 暂停状态渲染
            self._render_pause_screen()
        
        # 更新显示
        pygame.display.flip()
    
    def _render_selection_box(self):
        """渲染选择框"""
        if not self.selection_start:
            return
        
        mx, my = pygame.mouse.get_pos()
        start_x, start_y = self.selection_start
        
        # 计算矩形
        min_x = min(start_x, mx)
        max_x = max(start_x, mx)
        min_y = min(start_y, my)
        max_y = max(start_y, my)
        
        # 绘制选择框
        rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)
    
    def _render_game_info(self) -> None:
        """渲染游戏信息UI"""
        font = pygame.font.Font(None, 24)
        
        # 游戏状态信息
        info_lines = [
            "MinSC - Minimal StarCraft for MCP",
            "Controls: ESC=Quit, SPACE=Pause, Left=Select, Right=Command, W=Produce Worker, S=Stop",
            f"Map: {self.width}x{self.height}, Resources: {len(self.game_map.resource_points) if self.game_map else 0}",
            f"Units: {len(self.units)}, Buildings: {len(self.buildings)}, Selected: U{len(self.selected_units)} B{len(self.selected_buildings)}"
        ]
        
        y_offset = 10
        for line in info_lines:
            text = font.render(line, True, self.WHITE)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25
        
        # 显示选中单位信息
        if self.selected_units:
            y_offset += 10
            for i, unit in enumerate(self.selected_units[:3]):  # 最多显示3个单位
                info = unit.get_info()
                unit_text = f"Unit {i+1}: {info['type']} HP:{info['hp']} State:{info['state']}"
                if hasattr(unit, 'carrying_resources'):
                    unit_text += f" Resources:{info.get('resources', '0/0')}"
                
                text = font.render(unit_text, True, self.WHITE)
                self.screen.blit(text, (10, y_offset))
                y_offset += 20
    
    def _render_pause_screen(self) -> None:
        """渲染暂停屏幕"""
        # 半透明覆盖层
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 暂停文本
        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 36)
        
        pause_text = font_large.render("PAUSED", True, self.WHITE)
        pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        instruction_text = font_small.render("Press SPACE to resume", True, self.WHITE)
        instruction_rect = instruction_text.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(instruction_text, instruction_rect)

def main():
    """主函数"""
    print("🚀 启动MinSC - Minimal StarCraft for MCP")
    print("=" * 50)
    
    # 创建游戏实例
    game = MinSCGame(
        width=1024,
        height=768,
        fps=60,
        title="MinSC - Minimal StarCraft for MCP v0.1"
    )
    
    # 运行游戏
    try:
        game.run()
    except KeyboardInterrupt:
        print("\n⚠️  游戏被用户中断")
    except Exception as e:
        print(f"❌ 游戏运行错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 50)
    print("👋 MinSC 游戏结束")

if __name__ == "__main__":
    main()