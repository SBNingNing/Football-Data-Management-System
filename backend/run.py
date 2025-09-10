"""
后端运行文件
启动足球管理系统后端服务
"""

import os
from app import create_app, db
from app.main import get_app_info, validate_app_configuration
from app.config import get_config


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
        
        # 验证应用配置
        is_valid, errors = validate_app_configuration(app)
        if not is_valid:
            logger.error(f"应用配置验证失败: {errors}")
            return
        
        # 打印应用信息
        app_info = get_app_info(app)
        logger.info(f"应用信息: {app_info['app_name']} v{app_info['app_version']}")
        logger.info(f"注册的蓝图: {app_info['registered_blueprints']}")
        
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
