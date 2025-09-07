"""
历史查询模块工具类 - 兼容性保留版本
提供球员和球队历史数据处理的通用工具函数
注意：此文件为向后兼容保留，新代码请使用 player_history_utils.py 和 team_history_utils.py
"""

from app.utils.player_history_utils import PlayerHistoryUtils
from app.utils.team_history_utils import TeamHistoryUtils

# 为了保持向后兼容性，保留原有的HistoryUtils类
class HistoryUtils:
    """历史查询工具类 - 兼容性包装器"""

    # 球员相关方法 - 委托给PlayerHistoryUtils
    @staticmethod
    def validate_player_id(player_id: str) -> bool:
        return PlayerHistoryUtils.validate_player_id(player_id)

    @staticmethod
    def validate_season_id(season_id):
        return PlayerHistoryUtils.validate_season_id(season_id)
    
    @staticmethod
    def format_player_basic_info(player):
        return PlayerHistoryUtils.format_player_basic_info(player)
    
    # 球队相关方法 - 委托给TeamHistoryUtils  
    @staticmethod
    def validate_team_base_id(team_base_id):
        return TeamHistoryUtils.validate_team_base_id(team_base_id)
    
    @staticmethod
    def format_team_basic_info(team_base):
        return TeamHistoryUtils.format_team_basic_info(team_base)
    
    # 通用方法 - 保持原有实现
    @staticmethod
    def safe_date_format(date_obj):
        return PlayerHistoryUtils.safe_date_format(date_obj)
    
    @staticmethod
    def calculate_average_safely(total: float, count: int, decimal_places: int = 2) -> float:
        return PlayerHistoryUtils.calculate_average_safely(total, count, decimal_places)
    
    @staticmethod
    def get_empty_career_summary():
        return PlayerHistoryUtils.get_empty_career_summary()
    
    @staticmethod
    def get_empty_season_totals():
        return PlayerHistoryUtils.get_empty_season_totals()
    
    # 日志方法
    @staticmethod
    def log_history_operation(operation: str, entity_type: str, entity_id: str, details: str = ""):
        if entity_type == 'player':
            PlayerHistoryUtils.log_player_history_operation(operation, entity_id, details)
        elif entity_type == 'team':
            TeamHistoryUtils.log_team_history_operation(operation, entity_id, details)
