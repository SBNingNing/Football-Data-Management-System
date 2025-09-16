from functools import wraps
from flask import request, jsonify
from app.utils.validation_config import ValidationConfig
from app.utils.logger import get_logger

logger = get_logger(__name__)


def validate_json(required_fields=None):
    """JSON数据验证中间件装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                logger.warning(f"Non-JSON request for {request.endpoint}")
                return jsonify({'error': '请求必须是JSON格式'}), 400
                
            data = request.get_json()
            if not data:
                logger.warning(f"Empty request body for {request.endpoint}")
                return jsonify({'error': '请求体不能为空'}), 400
                
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    logger.warning(f"Missing fields: {missing_fields} for {request.endpoint}")
                    return jsonify({'error': f'缺少必要字段: {", ".join(missing_fields)}'}), 400
                    
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_user_data(f):
    """用户数据验证中间件"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        # 统一验证逻辑
        validations = [
            ('username', ValidationConfig.validate_username),
            ('email', ValidationConfig.validate_email),
            ('password', ValidationConfig.validate_password)
        ]
        
        for field, validator in validations:
            if field in data:
                is_valid, error_msg = validator(data[field])
                if not is_valid:
                    logger.warning(f"{field.capitalize()} validation failed: {error_msg}")
                    return jsonify({'error': error_msg}), 400
                
        return f(*args, **kwargs)
    return decorated_function
