"""
赛事中间件层
负责赛事相关的验证、错误处理和请求预处理
"""
from functools import wraps
from typing import Any, Callable, Dict, Optional
from flask import request, jsonify
from sqlalchemy import text

from app.database import db
from app.utils.logger import get_logger

logger = get_logger(__name__)


def validate_tournament_name(f: Callable) -> Callable:
    """
    验证赛事名称参数装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        tournament_name = kwargs.get('tournament_name')
        if not tournament_name or not tournament_name.strip():
            return jsonify({
                'status': 'error',
                'message': '赛事名称不能为空'
            }), 400
        return f(*args, **kwargs)
    return decorated_function


def validate_tournament_create_data(f: Callable) -> Callable:
    """
    验证创建赛事数据装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({
                'status': 'error',
                'message': '赛事名称不能为空'
            }), 400
        
        if not data.get('season_name'):
            return jsonify({
                'status': 'error',
                'message': '赛季名称不能为空'
            }), 400
        
        return f(*args, **kwargs)
    return decorated_function


def validate_tournament_instance_data(f: Callable) -> Callable:
    """
    验证创建赛事实例数据装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        required_fields = ['competition_id', 'season_id']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({
                    'status': 'error',
                    'message': f'{field}不能为空'
                }), 400
        
        return f(*args, **kwargs)
    return decorated_function


def validate_tournament_update_data(f: Callable) -> Callable:
    """
    验证更新赛事数据装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': '请提供要更新的数据'
            }), 400
        
        return f(*args, **kwargs)
    return decorated_function


def check_database_connection(f: Callable) -> Callable:
    """
    检查数据库连接装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            db.session.execute(text('SELECT 1'))
            return f(*args, **kwargs)
        except Exception as db_error:
            logger.error(f"数据库连接失败: {db_error}")
            return jsonify({
                'status': 'error',
                'message': '数据库连接失败'
            }), 500
    return decorated_function


def handle_tournament_errors(f: Callable) -> Callable:
    """
    赛事操作错误处理装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as ve:
            logger.warning(f"赛事操作参数错误: {ve}")
            return jsonify({
                'status': 'error',
                'message': str(ve)
            }), 400
        except Exception as e:
            db.session.rollback()
            logger.error(f"赛事操作失败: {e}")
            return jsonify({
                'status': 'error',
                'message': f'操作失败: {str(e)}'
            }), 500
    return decorated_function


def log_tournament_operation(operation_type: str):
    """
    记录赛事操作日志装饰器工厂
    
    Args:
        operation_type: 操作类型
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 记录操作开始
            logger.info(f"开始执行赛事{operation_type}操作")
            
            try:
                result = f(*args, **kwargs)
                logger.info(f"赛事{operation_type}操作成功完成")
                return result
            except Exception as e:
                logger.error(f"赛事{operation_type}操作失败: {e}")
                raise
        return decorated_function
    return decorator


class TournamentMiddleware:
    """赛事中间件类"""
    
    @staticmethod
    def validate_query_params(request_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证查询参数
        
        Args:
            request_args: 请求参数
            
        Returns:
            Dict[str, Any]: 处理后的参数
        """
        validated_params = {}
        
        # 验证group_by_name参数
        group_by_name = request_args.get('group_by_name', 'false').lower()
        validated_params['group_by_name'] = group_by_name == 'true'
        
        return validated_params
    
    @staticmethod
    def format_tournament_response(data: Any, message: str = None) -> Dict[str, Any]:
        """
        格式化赛事响应数据
        
        Args:
            data: 响应数据
            message: 响应消息
            
        Returns:
            Dict[str, Any]: 格式化后的响应
        """
        response = {
            'status': 'success',
            'data': data
        }
        
        if message:
            response['message'] = message
        
        return response
    
    @staticmethod
    def format_error_response(message: str, available_tournaments: list = None) -> Dict[str, Any]:
        """
        格式化错误响应
        
        Args:
            message: 错误消息
            available_tournaments: 可用赛事列表
            
        Returns:
            Dict[str, Any]: 格式化后的错误响应
        """
        response = {
            'status': 'error',
            'message': message
        }
        
        if available_tournaments:
            response['available_tournaments'] = available_tournaments
            response['total_tournaments'] = len(available_tournaments)
        
        return response
