"""
球员历史模块路由层
处理HTTP请求和响应
"""

from flask import Blueprint, request, jsonify
from app.services.player_history_service import PlayerHistoryService
from app.middleware.player_history_middleware import (
    validate_player_history, validate_season_performance,
    validate_player_comparison, validate_team_changes
)

# 创建蓝图（前缀在 create_app 中统一指定）
player_history_bp = Blueprint('player_history', __name__)

# 初始化服务
player_history_service = PlayerHistoryService()


@player_history_bp.route('/<player_id>/complete', methods=['GET'])
@validate_player_history
def get_player_complete_history(player_id: str):
    """获取球员完整的跨赛季历史记录"""
    result = player_history_service.get_player_complete_history(player_id)
    return result, 200


@player_history_bp.route('/<player_id>/season/<int:season_id>', methods=['GET'])
@validate_season_performance
def get_player_season_performance(player_id: str, season_id: int):
    """获取球员在指定赛季的表现"""
    result = player_history_service.get_player_season_performance(player_id, season_id)
    return result, 200


@player_history_bp.route('/compare', methods=['POST'])
@validate_player_comparison
def compare_players_across_seasons():
    """跨赛季球员对比"""
    data = request.get_json()
    player_ids = data.get('player_ids', [])
    season_ids = data.get('season_ids', [])  # 可选：指定赛季范围
    
    result = player_history_service.compare_players_across_seasons(player_ids, season_ids)
    return result, 200


@player_history_bp.route('/team-changes/<player_id>', methods=['GET'])
@validate_team_changes
def get_player_team_changes(player_id: str):
    """获取球员转队历史"""
    result = player_history_service.get_player_team_changes(player_id)
    return result, 200
