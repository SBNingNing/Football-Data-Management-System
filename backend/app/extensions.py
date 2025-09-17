"""extensions.py
集中初始化与管理可共享扩展实例 (db / jwt / cors / logging / future services)
后续若引入 cache(redis) / mail / limiter 等, 在此追加并在 init_app 中统一绑定。
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import logging

# 延迟创建的扩展实例
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS  # CORS 不是实例化形式, 直接引用工厂

logger = logging.getLogger(__name__)

def init_extensions(app):
    """初始化所有扩展到 app 上"""
    db.init_app(app)
    
    # 配置JWT错误处理器
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.error(f"JWT token已过期: {jwt_payload}")
        return {
            'status': 'error',
            'message': 'Token已过期，请重新登录'
        }, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        logger.error(f"JWT token无效: {error}")
        return {
            'status': 'error',
            'message': '无效的Token，请重新登录'
        }, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        logger.error(f"缺少JWT token: {error}")
        return {
            'status': 'error',
            'message': '缺少认证Token，请登录'
        }, 401
    
    jwt.init_app(app)
    # CORS 在 create_app 中根据配置进行更细粒度资源设置, 这里不直接调用
    return app

__all__ = ["db", "jwt", "cors", "init_extensions"]