from flask import current_app
from app.utils.logger import get_logger

logger = get_logger(__name__)

def security_headers(response):
    """安全头部处理中间件，添加X-Content-Type-Options等安全头部"""
    try:
        # 添加X-Content-Type-Options头部，防止MIME类型嗅探
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # 添加其他推荐的安全头部
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # 如果配置了HSTS，添加Strict-Transport-Security头部
        if current_app.config.get('ENABLE_HSTS', False):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
        logger.debug("安全头部已添加: X-Content-Type-Options=nosniff")
        
    except Exception as e:
        logger.error(f"安全头部设置失败: {e}")
        # 即使失败也尝试添加基本的安全头部
        try:
            response.headers['X-Content-Type-Options'] = 'nosniff'
        except:
            pass
    
    return response