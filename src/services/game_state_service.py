"""
游戏状态服务实现
"""
from typing import Dict
from ioc.services import IGameStateService, IEventBusService


class GameStateService:
    """游戏状态服务实现"""
    
    def __init__(self, event_bus: IEventBusService):
        self.event_bus = event_bus
        self._game_manager = None
    
    def set_game_manager(self, game_manager):
        """设置GameManager引用"""
        self._game_manager = game_manager
    
    def get_game_state(self):
        """获取当前游戏状态"""
        # 返回包装的游戏状态
        class GameStateWrapper:
            def __init__(self, game_manager):
                self.buildings = game_manager.buildings if game_manager else []
                self.units = game_manager.units if game_manager else []
                self.game_manager = game_manager
        
        return GameStateWrapper(self._game_manager)
    
    def get_player_resources(self, player_id: int) -> Dict[str, int]:
        """获取玩家资源"""
        # 简单实现，返回默认资源
        return {'minerals': 1000, 'gas': 500}
    
    def get_map_info(self):
        """获取地图信息"""
        class MapInfoWrapper:
            def __init__(self):
                self.width = 1024
                self.height = 768
        
        return MapInfoWrapper()