import logging
import logging.handlers
import os
from flask import current_app


def setup_logging(app):
    """设置应用日志配置"""
    if app.debug or app.testing:
        return
        
    # 创建日志目录
    log_dir = os.path.dirname(app.config['LOG_FILE'])
    os.makedirs(log_dir, exist_ok=True)
    
    # 配置文件处理器
    handler = logging.handlers.RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=app.config['LOG_MAX_BYTES'],
        backupCount=app.config['LOG_BACKUP_COUNT'],
        encoding='utf-8'
    )
    
    # 设置格式和级别
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    
    # 应用配置
    app.logger.addHandler(handler)
    app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    app.logger.info('Application startup')


def get_logger(name):
    """获取日志记录器"""
    logger = logging.getLogger(name)
    
    try:
        if current_app:
            logger.setLevel(getattr(logging, current_app.config['LOG_LEVEL']))
    except RuntimeError:
        logger.setLevel(logging.INFO)
    
    return logger
