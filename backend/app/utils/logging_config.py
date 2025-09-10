import logging
import logging.handlers
import os
from flask import current_app


def setup_logging(app):
    """设置应用日志配置"""
    # 创建日志目录
    log_dir = os.path.dirname(app.config['LOG_FILE'])
    os.makedirs(log_dir, exist_ok=True)
    
    # 只在主进程第一次启动时清空日志文件
    # 重启进程时保留日志，这样可以看到完整的启动过程
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        try:
            with open(app.config['LOG_FILE'], 'w', encoding='utf-8') as f:
                f.write('')  # 清空文件内容
        except (PermissionError, OSError) as e:
            print(f"无法清空日志文件: {e}")
    
    # 配置文件处理器（追加模式，因为文件已经清空了）
    handler = logging.handlers.RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=app.config['LOG_MAX_BYTES'],
        backupCount=app.config['LOG_BACKUP_COUNT'],
        encoding='utf-8',
        mode='a'  # 追加模式
    )
    
    # 设置格式和级别
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    
    # 配置控制台处理器（同时显示在控制台）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s'
    ))
    console_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    
    # 清除现有处理器，避免重复
    app.logger.handlers.clear()
    
    # 添加处理器
    app.logger.addHandler(handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    
    # 配置根日志记录器，确保所有模块的日志都能记录到文件
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.addHandler(console_handler)
    root_logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    
    app.logger.info('Application startup - Logging configured successfully')


def get_logger(name):
    """获取日志记录器"""
    logger = logging.getLogger(name)
    
    try:
        if current_app:
            logger.setLevel(getattr(logging, current_app.config['LOG_LEVEL']))
    except RuntimeError:
        logger.setLevel(logging.INFO)
    
    return logger
