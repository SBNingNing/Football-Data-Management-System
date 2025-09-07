"""
球员验证中间件
"""
from flask import request, jsonify
from functools import wraps
from app.utils.logger import get_logger

logger = get_logger(__name__)


def validate_player_creation_data(f):
    """验证球员创建数据的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('studentId'):
            logger.error("创建球员失败：球员姓名和学号不能为空")
            return jsonify({'status': 'error', 'message': '球员姓名和学号不能为空'}), 400
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_player_id(f):
    """验证球员ID的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        player_id = kwargs.get('player_id')
        if not player_id:
            logger.error("操作失败：球员ID不能为空")
            return jsonify({'status': 'error', 'message': '球员ID不能为空'}), 400
        
        return f(*args, **kwargs)
    
    return decorated_function
