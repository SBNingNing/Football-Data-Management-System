"""
后端运行文件
启动足球管理系统后端服务
"""

import os
from app import create_app
from app.extensions import db
from app.config import get_config
from app.utils.app_diagnostics import get_app_info, validate_app_configuration


def main():
    """主启动函数"""
    # 获取运行环境
    env = os.environ.get('FLASK_ENV', 'development')
    
    # 获取配置类
    config_class = get_config(env)
    
    # 创建应用
    app = create_app(config_class)
    
    # 现在使用应用的logger，确保日志记录到文件
    logger = app.logger
    
    try:
        logger.info(f"启动环境: {env}")

        # 运行配置验证（非阻断式，记录问题以便运维）
        ok, config_errors = validate_app_configuration(app)
        if not ok:
            for err in config_errors:
                logger.warning(f"配置校验告警: {err}")
        info = get_app_info(app)
        logger.info(f"App: {info['app_name']} v{info['app_version']} | Blueprints: {len(info['registered_blueprints'])}")
        logger.debug(f"已注册蓝图: {info['registered_blueprints']}")
        
        # 创建数据库表
        # 创建数据库表
        with app.app_context():
            try:
                db.create_all()
                logger.info("数据库表创建成功")
            except Exception as e:
                logger.error(f"数据库创建失败: {e}")
                return
        
        # 启动服务器
        host = app.config.get('HOST', '0.0.0.0')
        port = app.config.get('PORT', 5000)
        debug = app.config.get('DEBUG', False)
        
        logger.info(f"启动服务器: http://{host}:{port}")
        app.run(debug=debug, host=host, port=port)
        
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise


if __name__ == '__main__':
    main()
