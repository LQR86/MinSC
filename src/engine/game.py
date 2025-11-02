"""
MinSC Game Engine - 核心游戏引擎
简化的StarCraft游戏引擎，为MCP协议AI Agent提供RTS环境
"""

import pygame
import sys
from typing import Optional, Tuple
from enum import Enum

class GameState(Enum):
    """游戏状态枚举"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    GAME_OVER = "game_over"

class Game:
    """MinSC游戏主类"""
    
    def __init__(self, 
                 width: int = 1024, 
                 height: int = 768, 
                 fps: int = 60,
                 title: str = "MinSC - Minimal StarCraft for MCP"):
        """
        初始化游戏
        
        Args:
            width: 窗口宽度
            height: 窗口高度
            fps: 目标帧率
            title: 窗口标题
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        
        # 游戏状态
        self.state = GameState.INITIALIZING
        self.running = False
        self.clock: Optional[pygame.time.Clock] = None
        self.screen: Optional[pygame.Surface] = None
        
        # 颜色常量
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        
        print(f"MinSC Game Engine 初始化 - {width}x{height} @ {fps}FPS")
    
    def initialize(self) -> bool:
        """
        初始化Pygame和游戏系统
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 初始化Pygame
            pygame.init()
            
            # 创建游戏窗口
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption(self.title)
            
            # 创建时钟对象
            self.clock = pygame.time.Clock()
            
            # 设置游戏状态
            self.state = GameState.RUNNING
            self.running = True
            
            print("✅ Pygame初始化成功")
            print(f"✅ 游戏窗口创建成功: {self.width}x{self.height}")
            
            return True
            
        except Exception as e:
            print(f"❌ 游戏初始化失败: {e}")
            return False
    
    def handle_events(self) -> None:
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # 空格键暂停/恢复
                    if self.state == GameState.RUNNING:
                        self.state = GameState.PAUSED
                        print("游戏暂停")
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.RUNNING
                        print("游戏恢复")
    
    def update(self, delta_time: float) -> None:
        """
        更新游戏逻辑
        
        Args:
            delta_time: 距离上一帧的时间(秒)
        """
        if self.state != GameState.RUNNING:
            return
            
        # TODO: 在这里添加游戏逻辑更新
        # - 单位移动和AI
        # - 建筑生产
        # - 资源采集
        # - 战斗计算
        pass
    
    def render(self) -> None:
        """渲染游戏画面"""
        if not self.screen:
            return
            
        # 清空屏幕
        self.screen.fill(self.BLACK)
        
        if self.state == GameState.RUNNING:
            # TODO: 在这里添加游戏对象渲染
            # - 地图渲染
            # - 单位渲染
            # - 建筑渲染
            # - UI元素渲染
            
            # 临时：显示一个简单的状态指示
            font = pygame.font.Font(None, 36)
            text = font.render("MinSC Engine Running - Press ESC to quit, SPACE to pause", 
                             True, self.WHITE)
            text_rect = text.get_rect(center=(self.width // 2, 50))
            self.screen.blit(text, text_rect)
            
        elif self.state == GameState.PAUSED:
            # 暂停状态显示
            font = pygame.font.Font(None, 72)
            text = font.render("PAUSED", True, self.RED)
            text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(text, text_rect)
        
        # 更新显示
        pygame.display.flip()
    
    def run(self) -> None:
        """运行游戏主循环"""
        if not self.initialize():
            print("❌ 游戏初始化失败，退出")
            return
        
        print("🚀 开始游戏主循环...")
        
        last_time = pygame.time.get_ticks()
        
        while self.running:
            # 计算帧时间
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000.0  # 转换为秒
            last_time = current_time
            
            # 游戏循环三大步骤
            self.handle_events()
            self.update(delta_time)
            self.render()
            
            # 控制帧率
            if self.clock:
                self.clock.tick(self.fps)
        
        self.cleanup()
    
    def cleanup(self) -> None:
        """清理资源"""
        print("🔄 清理游戏资源...")
        pygame.quit()
        print("✅ 游戏正常退出")

if __name__ == "__main__":
    # 创建并运行游戏实例
    game = Game()
    game.run()