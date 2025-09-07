from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.utils.logging_config import get_logger
from app.middleware.error_middleware import log_security_event

logger = get_logger(__name__)


def auth_required(f):
    """认证中间件装饰器"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        if not user_id:
            log_security_event("AUTH_FAILED", "Invalid token")
            return jsonify({'error': '认证失败'}), 401
        
        logger.debug(f"User {user_id} authenticated for {f.__name__}")
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """管理员权限中间件装饰器"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        from app.models.user import User
        
        user_id = get_jwt_identity()
        if not user_id or user_id == 'guest':
            log_security_event("ADMIN_ACCESS_DENIED", f"Guest attempted {f.__name__}")
            return jsonify({'error': '需要管理员权限'}), 403
            
        user = User.query.get(user_id)
        if not user or user.身份_角色 != 'admin':
            log_security_event("ADMIN_ACCESS_DENIED", f"User {user_id} attempted {f.__name__}", user_id)
            return jsonify({'error': '需要管理员权限'}), 403
        
        logger.info(f"Admin {user_id} accessed {f.__name__}")
        return f(*args, **kwargs)
    return decorated_function


def guest_allowed(f):
    """允许游客访问的中间件装饰器"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        logger.debug(f"User/Guest {user_id} accessed {f.__name__}")
        return f(*args, **kwargs)
    return decorated_function
