"""
战略层AI服务实现 (占位符)
"""
from typing import TYPE_CHECKING
from ioc.services import IStrategyService, StrategicAssessment, StrategicPlan

if TYPE_CHECKING:
    from ioc.services import IGameStateService, IBuildingManagerService, IUnitManagerService, ILoggingService


class StrategyService:
    """战略层AI服务实现 - 占位符"""
    
    def __init__(self,
                 game_state: 'IGameStateService',
                 building_manager: 'IBuildingManagerService', 
                 unit_manager: 'IUnitManagerService',
                 logging: 'ILoggingService'):
        self.game_state = game_state
        self.building_manager = building_manager
        self.unit_manager = unit_manager
        self.logging = logging
        
        self.logging.info("✅ 战略AI服务初始化完成 (占位符)")
    
    def evaluate_game_situation(self, player_id: int) -> StrategicAssessment:
        """评估整体游戏局势"""
        self.logging.debug(f"评估玩家{player_id}的战略局势")
        
        # 占位符实现
        assessment = StrategicAssessment()
        assessment.player_id = player_id
        assessment.economic_status = "developing"
        assessment.military_strength = "weak"
        assessment.tech_level = "basic"
        assessment.threats = []
        assessment.opportunities = ["expand_economy", "build_army"]
        
        return assessment
    
    def recommend_strategy(self, player_id: int) -> StrategicPlan:
        """推荐战略方案"""
        assessment = self.evaluate_game_situation(player_id)
        
        # 占位符实现
        plan = StrategicPlan()
        plan.player_id = player_id
        plan.primary_goal = "economic_expansion"
        plan.secondary_goals = ["military_buildup", "tech_advancement"]
        plan.resource_allocation = {
            "economy": 0.6,
            "military": 0.3,
            "research": 0.1
        }
        plan.timeline = "long_term"
        
        self.logging.info(f"为玩家{player_id}生成战略计划: {plan.primary_goal}")
        return plan
    
    def adjust_long_term_goals(self, assessment: StrategicAssessment) -> None:
        """调整长期目标"""
        self.logging.debug(f"根据评估调整玩家{assessment.player_id}的长期目标")
        # 占位符实现 - 暂时不做任何调整
        pass