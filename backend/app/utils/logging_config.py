import logging
import logging.handlers
import os
from pathlib import Path


def setup_logging(app):
    """设置应用日志配置（文件 + 控制台）。

    约束：
    - 仅根 logger 绑定处理器，避免重复；模块内使用 get_logger(__name__) 输出，向上冒泡。
    - 开发模式避免对项目目录内日志文件写入导致的热重载循环（默认将日志写到临时目录；若手动设置了项目内路径，则不清空）。
    """
    # 目录与文件准备
    log_path = Path(app.config['LOG_FILE']).expanduser()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # 仅在非重载主进程、且日志文件不位于项目目录内时清空
    try:
        in_reloader = bool(os.environ.get('WERKZEUG_RUN_MAIN'))
        project_root = Path(app.root_path).resolve()
        resolved = log_path.resolve()
        is_inside_project = project_root == resolved or project_root in resolved.parents
        if not in_reloader and not is_inside_project:
            log_path.write_text('', encoding='utf-8')
    except Exception as e:
        print(f"无法清空日志文件: {e}")

    # 文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        str(log_path),
        maxBytes=app.config['LOG_MAX_BYTES'],
        backupCount=app.config['LOG_BACKUP_COUNT'],
        encoding='utf-8',
        mode='a'
    )
    file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
    file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
    console_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))

    # 根 logger 统一处理
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # app.logger 仅设置级别，开启冒泡，不直接加处理器
    app.logger.handlers.clear()
    app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    app.logger.propagate = True

    app.logger.info('Application startup - Logging configured successfully')
    try:
        app.logger.info(f"Logging to: {log_path} | Level: {app.config['LOG_LEVEL']}")
    except Exception:
        pass
