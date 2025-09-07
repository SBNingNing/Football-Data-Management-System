from functools import wraps
from flask import request, jsonify
from app.utils.logging_config import get_logger
from app.utils.validation_config import ValidationConfig

logger = get_logger(__name__)


def validate_competition_data(f):
    """竞赛数据验证中间件"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        if not data:
            logger.warning("Empty competition data provided")
            return jsonify({'status': 'error', 'message': '请提供竞赛数据'}), 400
        
        # 验证竞赛名称
        if 'name' in data:
            is_valid, error_msg = ValidationConfig.validate_competition_name(data['name'])
            if not is_valid:
                logger.warning(f"Competition name validation failed: {error_msg}")
                return jsonify({'status': 'error', 'message': error_msg}), 400
        
        return f(*args, **kwargs)
    return decorated_function


def validate_competition_id(f):
    """竞赛ID验证中间件"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        competition_id = kwargs.get('competition_id')
        
        if not competition_id or not isinstance(competition_id, int) or competition_id <= 0:
            logger.warning(f"Invalid competition ID: {competition_id}")
            return jsonify({'status': 'error', 'message': '无效的赛事ID'}), 400
        
        return f(*args, **kwargs)
    return decorated_function
