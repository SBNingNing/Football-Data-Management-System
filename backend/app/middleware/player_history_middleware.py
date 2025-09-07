"""
球员历史模块中间件
提供验证、错误处理和请求预处理功能
"""

from functools import wraps
from flask import request, jsonify
from typing import Callable, List, Dict, Any
from datetime import datetime
from app.utils.player_history_utils import PlayerHistoryUtils
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PlayerHistoryMiddleware:
    """球员历史中间件类"""

    @staticmethod
    def validate_player_id(f: Callable) -> Callable:
        """
        验证球员ID装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            player_id = kwargs.get('player_id') or request.view_args.get('player_id')
            
            if not PlayerHistoryUtils.validate_player_id(player_id):
                logger.warning(f"球员ID验证失败: player_id={player_id}")
                return jsonify({
                    'error': '球员ID不能为空或格式无效'
                }), 400
            
            kwargs['player_id'] = player_id.strip()
            return f(*args, **kwargs)
        
        return decorated_function

    @staticmethod
    def validate_season_id(f: Callable) -> Callable:
        """
        验证赛季ID装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            season_id = kwargs.get('season_id') or request.view_args.get('season_id')
            
            if not PlayerHistoryUtils.validate_season_id(season_id):
                logger.warning(f"赛季ID验证失败: season_id={season_id}")
                return jsonify({
                    'error': '赛季ID不能为空或格式无效'
                }), 400
            
            try:
                kwargs['season_id'] = int(season_id)
            except (ValueError, TypeError):
                return jsonify({
                    'error': '赛季ID必须是有效的数字'
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function

    @staticmethod
    def validate_comparison_data(f: Callable) -> Callable:
        """
        验证球员对比数据装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            
            if not data:
                logger.warning("球员对比数据验证失败: 请求体为空")
                return jsonify({
                    'error': '请求数据不能为空'
                }), 400
            
            player_ids = data.get('player_ids', [])
            if not player_ids or not isinstance(player_ids, list):
                logger.warning(f"球员对比数据验证失败: player_ids={player_ids}")
                return jsonify({
                    'error': '请提供要比较的球员ID列表'
                }), 400
            
            # 验证每个球员ID
            for player_id in player_ids:
                if not PlayerHistoryUtils.validate_player_id(player_id):
                    logger.warning(f"球员ID验证失败: {player_id}")
                    return jsonify({
                        'error': f'球员ID格式无效: {player_id}'
                    }), 400
            
            # 验证赛季ID（可选）
            season_ids = data.get('season_ids', [])
            if season_ids and isinstance(season_ids, list):
                for season_id in season_ids:
                    if not PlayerHistoryUtils.validate_season_id(season_id):
                        logger.warning(f"赛季ID验证失败: {season_id}")
                        return jsonify({
                            'error': f'赛季ID格式无效: {season_id}'
                        }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function

    @staticmethod
    def handle_history_errors(f: Callable) -> Callable:
        """
        球员历史操作错误处理装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except ValueError as e:
                logger.error(f"球员历史操作参数错误: {str(e)}")
                return jsonify({
                    'error': str(e)
                }), 404
            except Exception as e:
                logger.error(f"球员历史操作内部错误: {str(e)}", exc_info=True)
                return jsonify({
                    'error': f'服务器内部错误: {str(e)}'
                }), 500
        
        return decorated_function

    @staticmethod
    def log_history_request(f: Callable) -> Callable:
        """
        记录球员历史请求日志装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            endpoint = request.endpoint
            method = request.method
            player_id = kwargs.get('player_id', 'N/A')
            season_id = kwargs.get('season_id', 'N/A')
            
            logger.info(f"球员历史请求 - {method} {endpoint}: player_id={player_id}, season_id={season_id}")
            
            result = f(*args, **kwargs)
            
            # 记录响应状态
            if hasattr(result, '__len__') and len(result) > 1:
                status_code = result[1]
                logger.info(f"球员历史响应 - {method} {endpoint}: status={status_code}")
            
            return result
        
        return decorated_function

    @staticmethod
    def validate_request_limits(f: Callable) -> Callable:
        """
        验证请求限制装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 检查球员对比数量限制
            data = request.get_json()
            if data and 'player_ids' in data:
                player_ids = data.get('player_ids', [])
                if len(player_ids) > 20:  # 限制最多比较20个球员
                    logger.warning(f"球员对比数量超限: {len(player_ids)}")
                    return jsonify({
                        'error': '最多只能同时比较20个球员'
                    }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function

    @staticmethod
    def validate_response_format(f: Callable) -> Callable:
        """
        验证响应格式装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            
            # 确保返回的是标准的JSON响应格式
            if isinstance(result, tuple) and len(result) == 2:
                response_data, status_code = result
                if isinstance(response_data, dict):
                    # 添加时间戳
                    response_data['timestamp'] = datetime.now().isoformat()
                    return jsonify(response_data), status_code
            
            return result
        
        return decorated_function


# 组合装饰器 - 常用组合
def validate_player_history(f: Callable) -> Callable:
    """球员历史验证组合装饰器"""
    return PlayerHistoryMiddleware.validate_response_format(
        PlayerHistoryMiddleware.handle_history_errors(
            PlayerHistoryMiddleware.log_history_request(
                PlayerHistoryMiddleware.validate_player_id(f)
            )
        )
    )


def validate_season_performance(f: Callable) -> Callable:
    """赛季表现验证组合装饰器"""
    return PlayerHistoryMiddleware.validate_response_format(
        PlayerHistoryMiddleware.handle_history_errors(
            PlayerHistoryMiddleware.log_history_request(
                PlayerHistoryMiddleware.validate_season_id(
                    PlayerHistoryMiddleware.validate_player_id(f)
                )
            )
        )
    )


def validate_player_comparison(f: Callable) -> Callable:
    """球员对比验证组合装饰器"""
    return PlayerHistoryMiddleware.validate_response_format(
        PlayerHistoryMiddleware.handle_history_errors(
            PlayerHistoryMiddleware.log_history_request(
                PlayerHistoryMiddleware.validate_request_limits(
                    PlayerHistoryMiddleware.validate_comparison_data(f)
                )
            )
        )
    )


def validate_team_changes(f: Callable) -> Callable:
    """转队历史验证组合装饰器"""
    return PlayerHistoryMiddleware.validate_response_format(
        PlayerHistoryMiddleware.handle_history_errors(
            PlayerHistoryMiddleware.log_history_request(
                PlayerHistoryMiddleware.validate_player_id(f)
            )
        )
    )
