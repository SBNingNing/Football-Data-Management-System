"""
事件相关的工具函数
"""
from app.models.tournament import Tournament
from typing import Optional
from app.utils.tournament_utils import TournamentUtils


def determine_match_type(tournament: Optional[Tournament]) -> str:
    """根据赛事名称确定matchType"""
    return TournamentUtils.determine_match_type(tournament)


def validate_event_type(event_type: str) -> bool:
    """验证事件类型是否有效"""
    valid_event_types = ['进球', '乌龙球', '红牌', '黄牌']
    return event_type in valid_event_types


def validate_event_time(event_time: any) -> tuple[bool, int]:
    """验证事件时间是否有效
    
    Returns:
        tuple: (是否有效, 转换后的时间值)
    """
    try:
        event_time_int = int(event_time)
        if event_time_int < 0 or event_time_int > 120:  # 允许加时赛
            return False, 0
        return True, event_time_int
    except (ValueError, TypeError):
        return False, 0


def get_valid_event_types() -> list[str]:
    """获取有效的事件类型列表"""
    return ['进球', '乌龙球', '红牌', '黄牌']
