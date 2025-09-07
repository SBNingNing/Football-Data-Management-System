"""
应用工具函数
提供应用信息获取和配置验证功能
"""

import os
from app.config import get_config, validate_all_configs
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_app_info(app):
    """获取应用信息"""
    return {
        'app_name': app.config.get('APP_NAME', 'Unknown'),
        'app_version': app.config.get('APP_VERSION', 'Unknown'),
        'debug_mode': app.config.get('DEBUG', False),
        'environment': app.config.get('ENV', 'Unknown'),
        'database_uri': app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured'),
        'registered_blueprints': list(app.blueprints.keys())
    }


def validate_app_configuration(app):
    """验证应用配置的完整性"""
    errors = []
    
    # 检查必要配置项
    required_configs = ['SECRET_KEY', 'SQLALCHEMY_DATABASE_URI', 'JWT_SECRET_KEY']
    for config_key in required_configs:
        if not app.config.get(config_key):
            errors.append(f"缺少必要配置: {config_key}")
    
    # 检查蓝图注册
    expected_blueprints = [
        'auth', 'matches', 'events', 'teams', 'tournaments', 
        'competitions', 'seasons', 'player_history', 'team_history', 'players', 'stats'
    ]
    registered_blueprints = list(app.blueprints.keys())
    missing_blueprints = [bp for bp in expected_blueprints if bp not in registered_blueprints]
    
    if missing_blueprints:
        errors.append(f"缺少蓝图注册: {', '.join(missing_blueprints)}")
    
    return len(errors) == 0, errors