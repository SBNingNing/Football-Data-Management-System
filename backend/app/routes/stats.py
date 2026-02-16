"""
统计路由层 - 处理HTTP请求和响应
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.services.stats_facade import StatsFacade
from app.middleware.stats_middleware import (
    log_stats_operation,
    handle_stats_errors,
    cache_stats_result
)
from app.utils.logger import get_logger
from app.utils.response import success_response, error_response

logger = get_logger(__name__)

# 统一前缀交由 create_app 注册时指定，以保持所有蓝图一致性
stats_bp = Blueprint('stats', __name__)


@stats_bp.route('', methods=['GET'])
@handle_stats_errors
@log_stats_operation('查询')
@cache_stats_result(300)  # 缓存5分钟
def get_stats():
    """获取比赛统计数据"""
    try:
        stats_data = StatsFacade.overview()
        return success_response(stats_data, message="统计数据获取成功")
    except Exception as e:
        logger.error(f"获取统计数据失败: {str(e)}")
        return error_response('STATS_ERROR', '获取统计数据失败', 500)


@stats_bp.route('/rankings', methods=['GET'])
@handle_stats_errors
@log_stats_operation('排行榜查询')
# @cache_stats_result(600)  # 暂时禁用缓存以便调试，或者需要根据参数生成缓存key
def get_rankings():
    """获取排行榜数据"""
    try:
        season_id = request.args.get('season_id', type=int)
        rankings = StatsFacade.all_rankings(season_id)
        return success_response(rankings, message="排行榜获取成功")
    except Exception as e:
        logger.error(f"获取排行榜失败: {str(e)}")
        return error_response('RANKINGS_ERROR', '获取排行榜失败', 500)


@stats_bp.route('/tournaments/<int:tournament_id>/stats', methods=['GET'])
@handle_stats_errors
@log_stats_operation('赛事统计查询')
def get_tournament_stats(tournament_id):
    """获取特定赛事的统计数据"""
    try:
        stats_data = StatsFacade.tournament_detail_stats(tournament_id)
        return success_response(stats_data, message="赛事统计获取成功")
    except Exception as e:
        logger.error(f"获取赛事统计失败: {str(e)}")
        return error_response('TOURNAMENT_STATS_ERROR', '获取赛事统计失败', 500)


@stats_bp.route('/tournaments/<int:tournament_id>/rankings/<string:ranking_type>', methods=['GET'])
@handle_stats_errors
@log_stats_operation('特定排行榜查询')
def get_tournament_ranking(tournament_id, ranking_type):
    """获取特定赛事的特定类型排行榜"""
    try:
        if ranking_type == 'points':
            ranking_data = StatsFacade.tournament_points_ranking(tournament_id)
        elif ranking_type == 'participation':
            ranking_data = StatsFacade.tournament_team_rankings(tournament_id)
        else:
            # 可扩展更多类型
            ranking_data = []

        return success_response({
            'tournament_id': tournament_id,
            'ranking_type': ranking_type,
            'rankings': ranking_data
        }, message="赛事排行榜获取成功")
    except Exception as e:
        logger.error(f"获取特定排行榜失败: {str(e)}")
        return error_response('TOURNAMENT_RANKING_ERROR', '获取排行榜失败', 500)
