"""
球队历史模块中间件
提供验证、错误处理和请求预处理功能
"""

from functools import wraps
from flask import request, jsonify
from typing import Callable, List, Dict, Any
from datetime import datetime
from app.utils.team_history_utils import TeamHistoryUtils
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TeamHistoryMiddleware:
    """球队历史中间件类"""
    
    @staticmethod
    def validate_team_base_id(f: Callable) -> Callable:
        """
        验证球队基础ID的装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            team_base_id = kwargs.get('team_base_id') or request.view_args.get('team_base_id')
            
            if not TeamHistoryUtils.validate_team_base_id(team_base_id):
                logger.warning(f"球队ID验证失败: team_base_id={team_base_id}")
                return jsonify({
                    'error': '球队ID不能为空或格式无效'
                }), 400
            
            kwargs['team_base_id'] = str(team_base_id).strip()
            return f(*args, **kwargs)
        
        return decorated_function
    
    @staticmethod
    def validate_season_id(f: Callable) -> Callable:
        """
        验证赛季ID的装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            season_id = kwargs.get('season_id') or request.view_args.get('season_id')
            
            if not TeamHistoryUtils.validate_season_id(season_id):
                logger.warning(f"赛季ID验证失败: season_id={season_id}")
                return jsonify({
                    'error': '赛季ID不能为空或格式无效'
                }), 400
            
            kwargs['season_id'] = int(season_id)
            return f(*args, **kwargs)
        
        return decorated_function
    
    @staticmethod
    def validate_comparison_data(f: Callable) -> Callable:
        """
        验证球队对比数据的装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': '请求体不能为空'}), 400
                
                errors = TeamHistoryUtils.validate_comparison_data(data)
                if errors:
                    logger.warning(f"球队对比数据验证失败: {errors}")
                    return jsonify({
                        'error': '数据验证失败',
                        'details': errors
                    }), 400
                
                # 验证球队数量限制
                team_base_ids = data.get('team_base_ids', [])
                if len(team_base_ids) > 10:
                    return jsonify({
                        'error': '一次最多只能对比10支球队'
                    }), 400
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"球队对比数据验证异常: {e}")
                return jsonify({
                    'error': '数据验证过程中发生错误'
                }), 500
        
        return decorated_function
    
    @staticmethod
    def handle_team_history_errors(f: Callable) -> Callable:
        """
        统一的球队历史错误处理装饰器
        
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
                logger.warning(f"球队历史查询参数错误: {e}")
                return jsonify({
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 404
            except Exception as e:
                logger.error(f"球队历史查询异常: {e}")
                return jsonify({
                    'error': '服务器内部错误',
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        return decorated_function
    
    @staticmethod
    def log_team_history_request(f: Callable) -> Callable:
        """
        记录球队历史请求日志的装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 记录请求开始
            start_time = datetime.now()
            team_base_id = kwargs.get('team_base_id', 'unknown')
            season_id = kwargs.get('season_id', 'all')
            
            logger.info(f"球队历史请求开始: team_base_id={team_base_id}, season_id={season_id}")
            
            try:
                result = f(*args, **kwargs)
                # 记录请求成功
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.info(f"球队历史请求成功: team_base_id={team_base_id}, 耗时={duration:.2f}秒")
                return result
            except Exception as e:
                # 记录请求失败
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.error(f"球队历史请求失败: team_base_id={team_base_id}, 耗时={duration:.2f}秒, 错误={e}")
                raise
        
        return decorated_function
    
    @staticmethod
    def validate_request_limits(f: Callable) -> Callable:
        """
        验证请求限制的装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 验证是否为POST请求的大批量对比
            if request.method == 'POST':
                try:
                    data = request.get_json()
                    if data:
                        team_base_ids = data.get('team_base_ids', [])
                        season_ids = data.get('season_ids', [])
                        
                        # 限制球队数量
                        if len(team_base_ids) > 10:
                            return jsonify({
                                'error': '一次最多只能对比10支球队'
                            }), 400
                        
                        # 限制赛季数量
                        if len(season_ids) > 20:
                            return jsonify({
                                'error': '一次最多只能查询20个赛季的数据'
                            }), 400
                        
                except Exception:
                    pass  # 如果解析失败，让后续处理
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    @staticmethod
    def validate_response_format(f: Callable) -> Callable:
        """
        验证响应格式的装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            
            # 确保响应包含时间戳
            if isinstance(result, tuple) and len(result) == 2:
                response_data, status_code = result
                if isinstance(response_data, dict) and 'timestamp' not in response_data:
                    response_data['timestamp'] = datetime.now().isoformat()
                return jsonify(response_data), status_code
            
            return result
        
        return decorated_function


# 组合装饰器 - 常用验证组合
def validate_team_history(f: Callable) -> Callable:
    """
    球队历史验证组合装饰器
    包含: 球队ID验证 + 错误处理 + 请求日志
    """
    return TeamHistoryMiddleware.log_team_history_request(
        TeamHistoryMiddleware.handle_team_history_errors(
            TeamHistoryMiddleware.validate_team_base_id(f)
        )
    )


def validate_team_season_performance(f: Callable) -> Callable:
    """
    球队赛季表现验证组合装饰器
    包含: 球队ID验证 + 赛季ID验证 + 错误处理 + 请求日志
    """
    return TeamHistoryMiddleware.log_team_history_request(
        TeamHistoryMiddleware.handle_team_history_errors(
            TeamHistoryMiddleware.validate_season_id(
                TeamHistoryMiddleware.validate_team_base_id(f)
            )
        )
    )


def validate_team_comparison(f: Callable) -> Callable:
    """
    球队对比验证组合装饰器
    包含: 对比数据验证 + 请求限制 + 错误处理 + 请求日志
    """
    return TeamHistoryMiddleware.log_team_history_request(
        TeamHistoryMiddleware.handle_team_history_errors(
            TeamHistoryMiddleware.validate_request_limits(
                TeamHistoryMiddleware.validate_comparison_data(f)
            )
        )
    )


def validate_tournament_history(f: Callable) -> Callable:
    """
    球队参赛历史验证组合装饰器
    包含: 球队ID验证 + 错误处理 + 请求日志 + 响应格式验证
    """
    return TeamHistoryMiddleware.validate_response_format(
        TeamHistoryMiddleware.log_team_history_request(
            TeamHistoryMiddleware.handle_team_history_errors(
                TeamHistoryMiddleware.validate_team_base_id(f)
            )
        )
    )
