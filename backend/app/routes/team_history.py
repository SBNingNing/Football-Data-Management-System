"""
球队历史路由模块
路由层仅处理HTTP请求响应，业务逻辑交由服务层和中间件层处理
"""

from flask import Blueprint, jsonify, request
from app.services.team_history_service import TeamHistoryService
from app.middleware.team_history_middleware import (
    validate_team_history,
    validate_team_season_performance,
    validate_team_comparison,
    validate_tournament_history
)
from app.schemas import (
    TH_TeamComparisonIn,
    TH_TeamCompleteHistoryOut,
    TH_TeamSeasonPerformanceOut,
    TH_TeamTournamentHistoryOut,
)

# 创建蓝图（前缀在 create_app 中统一指定）
team_history_bp = Blueprint('team_history', __name__)


@team_history_bp.route('/<team_base_id>/complete', methods=['GET'])
@validate_team_history
def get_team_complete_history(team_base_id: str):
    """获取球队完整的跨赛季历史记录"""
    result = TeamHistoryService.get_team_complete_history(team_base_id)
    # 通过 Schema 构造做轻量校验，保持原有响应结构
    out = TH_TeamCompleteHistoryOut(**result)
    return jsonify({
        "status": "success",
        "data": out.model_dump(by_alias=True)
    }), 200


@team_history_bp.route('/<team_base_id>/season/<int:season_id>', methods=['GET'])
@validate_team_season_performance
def get_team_season_performance(team_base_id: str, season_id: int):
    """获取球队在指定赛季的表现"""
    result = TeamHistoryService.get_team_season_performance(team_base_id, season_id)
    out = TH_TeamSeasonPerformanceOut(**result)
    return jsonify({
        "status": "success",
        "data": out.model_dump(by_alias=True)
    }), 200


@team_history_bp.route('/compare', methods=['POST'])
@validate_team_comparison
def compare_teams_across_seasons():
    """跨赛季球队对比"""
    payload = TH_TeamComparisonIn(**(request.get_json() or {}))
    team_base_ids = payload.team_base_ids
    season_ids = payload.season_ids or []
    
    result = TeamHistoryService.compare_teams_across_seasons(team_base_ids, season_ids)
    return jsonify({
        "status": "success",
        "data": result
    }), 200


@team_history_bp.route('/tournament-history/<team_base_id>', methods=['GET'])
@validate_tournament_history
def get_team_tournament_history(team_base_id: str):
    """获取球队参赛历史"""
    result = TeamHistoryService.get_team_tournament_history(team_base_id)
    out = TH_TeamTournamentHistoryOut(**result)
    return jsonify({
        "status": "success",
        "data": out.model_dump(by_alias=True)
    }), 200
