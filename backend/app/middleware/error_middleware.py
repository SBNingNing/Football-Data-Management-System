from flask import current_app
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def cors_headers(response):
    """CORS头部处理中间件"""
    try:
        cors_config = current_app.config['CORS_CONFIG']
        headers = {
            'Access-Control-Allow-Origin': ','.join(cors_config['ORIGINS']),
            'Access-Control-Allow-Methods': ','.join(cors_config['METHODS']),
            'Access-Control-Allow-Headers': ','.join(cors_config['HEADERS']),
            'Access-Control-Max-Age': '86400'
        }
        
        for key, value in headers.items():
            response.headers[key] = value
            
        logger.debug(f"CORS headers applied: {headers['Access-Control-Allow-Origin']}")
        
    except Exception as e:
        logger.error(f"CORS setup failed: {e}")
        # 默认CORS设置
        default_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
        for key, value in default_headers.items():
            response.headers[key] = value
    
    return response


def log_error(error, context=None):
    """统一错误日志记录"""
    msg = f"Error: {error}"
    if context:
        msg += f" | Context: {context}"
    logger.error(msg, exc_info=True)


def log_security_event(event_type, details, user_id=None):
    """记录安全相关事件"""
    msg = f"Security - {event_type}: {details}"
    if user_id is not None:
        msg += f" | User: {user_id}"
    logger.warning(msg)
