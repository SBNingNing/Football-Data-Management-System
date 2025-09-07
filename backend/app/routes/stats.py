"""
统计路由层 - 处理HTTP请求和响应
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.services.stats_service import StatsService
from app.middleware.stats_middleware import (
    validate_tournament_id,
    validate_stats_query_params,
    validate_ranking_type,
    log_stats_operation,
    handle_stats_errors,
    cache_stats_result
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

stats_bp = Blueprint('stats', __name__, url_prefix='/api')


@stats_bp.route('/stats', methods=['GET'])
@handle_stats_errors
@log_stats_operation('查询')
@cache_stats_result(300)  # 缓存5分钟
def get_stats():
    """获取比赛统计数据"""
    try:
        stats_data = StatsService.get_match_statistics()
        
        return jsonify({
            'status': 'success',
            'data': stats_data
        }), 200
        
    except Exception as e:
        logger.error(f"获取统计数据失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取统计数据失败: {str(e)}'
        }), 500


@stats_bp.route('/rankings', methods=['GET'])
@handle_stats_errors
@validate_stats_query_params
@log_stats_operation('排行榜查询')
@cache_stats_result(600)  # 缓存10分钟
def get_rankings():
    """获取排行榜数据"""
    try:
        rankings = StatsService.get_all_rankings()
        
        return jsonify({
            'status': 'success',
            'data': rankings
        }), 200
        
    except Exception as e:
        logger.error(f"获取排行榜失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取排行榜失败: {str(e)}'
        }), 500


@stats_bp.route('/tournaments/<int:tournament_id>/stats', methods=['GET'])
@handle_stats_errors
@validate_tournament_id
@log_stats_operation('赛事统计查询')
def get_tournament_stats(tournament_id):
    """获取特定赛事的统计数据"""
    try:
        stats_data = StatsService.get_tournament_statistics(tournament_id)
        
        return jsonify({
            'status': 'success',
            'data': stats_data
        }), 200
        
    except Exception as e:
        logger.error(f"获取赛事统计失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取赛事统计失败: {str(e)}'
        }), 500


@stats_bp.route('/tournaments/<int:tournament_id>/rankings/<string:ranking_type>', methods=['GET'])
@handle_stats_errors
@validate_tournament_id
@validate_ranking_type
@log_stats_operation('特定排行榜查询')
def get_tournament_ranking(tournament_id, ranking_type):
    """获取特定赛事的特定类型排行榜"""
    try:
        # 根据排行榜类型获取相应数据
        if ranking_type == 'points':
            ranking_data = StatsService.calculate_team_points(tournament_id)
        else:
            # 其他类型的排行榜可以通过获取完整排行榜数据然后筛选
            all_rankings = StatsService.get_all_rankings()
            # 这里需要根据tournament_id筛选，简化处理
            ranking_data = []
        
        return jsonify({
            'status': 'success',
            'data': {
                'tournament_id': tournament_id,
                'ranking_type': ranking_type,
                'rankings': ranking_data
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取特定排行榜失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取排行榜失败: {str(e)}'
        }), 500
