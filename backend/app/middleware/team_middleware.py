"""
球队中间件层
处理球队相关的验证、错误处理和请求预处理
"""
from functools import wraps
from flask import request, jsonify
from typing import Dict, Any
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def validate_team_data(f):
    """球队数据验证中间件"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        if not data:
            logger.warning("Empty team data provided")
            return jsonify({'status': 'error', 'message': '请提供球队数据'}), 400
        
        # 验证球队名称
        if not data.get('teamName'):
            logger.warning("Team name is required but not provided")
            return jsonify({'status': 'error', 'message': '球队名称不能为空'}), 400
        
        # 验证球队名称长度
        team_name = data['teamName'].strip()
        if len(team_name) < 2:
            return jsonify({'status': 'error', 'message': '球队名称至少需要2个字符'}), 400
        
        if len(team_name) > 50:
            return jsonify({'status': 'error', 'message': '球队名称不能超过50个字符'}), 400
        
        # 验证比赛类型
        match_type = data.get('matchType', 'champions-cup')
        valid_match_types = ['champions-cup', 'womens-cup', 'eight-a-side']
        if match_type not in valid_match_types:
            return jsonify({
                'status': 'error', 
                'message': f'无效的比赛类型。有效类型: {", ".join(valid_match_types)}'
            }), 400
        
        # 验证球员数据
        players = data.get('players', [])
        if isinstance(players, list):
            for i, player in enumerate(players):
                if not isinstance(player, dict):
                    return jsonify({
                        'status': 'error', 
                        'message': f'第{i+1}个球员数据格式错误'
                    }), 400
                
                if not player.get('name'):
                    return jsonify({
                        'status': 'error', 
                        'message': f'第{i+1}个球员姓名不能为空'
                    }), 400
                
                if not player.get('studentId'):
                    return jsonify({
                        'status': 'error', 
                        'message': f'第{i+1}个球员学号不能为空'
                    }), 400
                
                # 验证球员号码
                try:
                    number = int(player.get('number', 1))
                    if number < 1 or number > 99:
                        return jsonify({
                            'status': 'error', 
                            'message': f'第{i+1}个球员号码必须在1-99之间'
                        }), 400
                except (ValueError, TypeError):
                    return jsonify({
                        'status': 'error', 
                        'message': f'第{i+1}个球员号码格式错误'
                    }), 400
        
        return f(*args, **kwargs)
    return decorated_function


def validate_team_id(f):
    """球队ID验证中间件"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        team_id = kwargs.get('team_id')
        
        if not team_id or not isinstance(team_id, int) or team_id <= 0:
            logger.warning(f"Invalid team ID: {team_id}")
            return jsonify({'status': 'error', 'message': '无效的球队ID'}), 400
        
        return f(*args, **kwargs)
    return decorated_function


def validate_team_name(f):
    """球队名称验证中间件"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        team_name = kwargs.get('team_name')
        
        if not team_name or not isinstance(team_name, str):
            logger.warning(f"Invalid team name: {team_name}")
            return jsonify({'status': 'error', 'message': '无效的球队名称'}), 400
        
        # 验证球队名称长度和字符
        team_name = team_name.strip()
        if len(team_name) < 1:
            return jsonify({'status': 'error', 'message': '球队名称不能为空'}), 400
        
        if len(team_name) > 50:
            return jsonify({'status': 'error', 'message': '球队名称不能超过50个字符'}), 400
        
        return f(*args, **kwargs)
    return decorated_function


def validate_query_params(f):
    """查询参数验证中间件"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 验证group_by_name参数
        group_by_name = request.args.get('group_by_name', 'false')
        if group_by_name.lower() not in ['true', 'false']:
            return jsonify({
                'status': 'error', 
                'message': 'group_by_name参数只能是true或false'
            }), 400
        
        return f(*args, **kwargs)
    return decorated_function


def handle_team_errors(f):
    """球队操作错误处理中间件"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as ve:
            logger.warning(f"Validation error in team operation: {ve}")
            return jsonify({'status': 'error', 'message': str(ve)}), 400
        except Exception as e:
            logger.error(f"Unexpected error in team operation: {e}")
            return jsonify({'status': 'error', 'message': '服务器内部错误'}), 500
    return decorated_function


def log_team_operation(operation_type: str):
    """球队操作日志中间件"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 记录操作开始
            logger.info(f"Team {operation_type} operation started")
            
            try:
                result = f(*args, **kwargs)
                logger.info(f"Team {operation_type} operation completed successfully")
                return result
            except Exception as e:
                logger.error(f"Team {operation_type} operation failed: {e}")
                raise
                
        return decorated_function
    return decorator


class TeamMiddleware:
    """球队中间件类"""
    
    @staticmethod
    def format_team_response(data: Any, message: str = None) -> Dict[str, Any]:
        """
        格式化球队响应数据
        
        Args:
            data: 响应数据
            message: 响应消息
            
        Returns:
            Dict: 格式化的响应数据
        """
        response = {
            'status': 'success'
        }
        
        if message:
            response['message'] = message
        
        if data is not None:
            response['data'] = data
        
        return response
    
    @staticmethod
    def format_error_response(error_message: str, error_code: str = None) -> Dict[str, Any]:
        """
        格式化错误响应数据
        
        Args:
            error_message: 错误消息
            error_code: 错误代码
            
        Returns:
            Dict: 格式化的错误响应数据
        """
        response = {
            'status': 'error',
            'message': error_message
        }
        
        if error_code:
            response['error_code'] = error_code
        
        return response
    
    @staticmethod
    def validate_query_params(args: Dict[str, str]) -> Dict[str, Any]:
        """
        验证和解析查询参数
        
        Args:
            args: 请求参数
            
        Returns:
            Dict: 验证后的参数
        """
        validated_params = {
            'group_by_name': args.get('group_by_name', 'false').lower() == 'true'
        }
        
        return validated_params
