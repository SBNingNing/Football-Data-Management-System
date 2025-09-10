import os
from datetime import timedelta
import logging


class Config:
    """基础配置类"""
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-should-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'mysql+pymysql://root:123456@localhost/football_management_system'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-dev-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_EXPIRES_HOURS', 1)))
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
    
    # 服务器配置
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    SERVER_NAME = os.environ.get('SERVER_NAME', 'localhost:5000')
    APPLICATION_ROOT = os.environ.get('APPLICATION_ROOT', '/')
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME', 'http')
    
    # CORS配置 - 与__init__.py保持一致
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8080').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_HEADERS = ['Content-Type', 'Authorization']
    
    # 用户验证规则配置
    USER_VALIDATION = {
        'USERNAME_MIN_LENGTH': int(os.environ.get('USERNAME_MIN_LENGTH', 3)),
        'USERNAME_MAX_LENGTH': int(os.environ.get('USERNAME_MAX_LENGTH', 50)),
        'PASSWORD_MIN_LENGTH': int(os.environ.get('PASSWORD_MIN_LENGTH', 6)),
        'PASSWORD_MAX_LENGTH': int(os.environ.get('PASSWORD_MAX_LENGTH', 128)),
        'REQUIRE_PASSWORD_COMPLEXITY': os.environ.get('REQUIRE_PASSWORD_COMPLEXITY', 'False').lower() == 'true'
    }
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    # 使用backend目录下的logs文件夹记录后端运行状况
    BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_FILE = os.environ.get('LOG_FILE', os.path.join(BACKEND_ROOT, 'logs', 'app.log'))
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # 分页配置
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 20))
    MAX_ITEMS_PER_PAGE = int(os.environ.get('MAX_ITEMS_PER_PAGE', 100))
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    
    @classmethod
    def validate_config(cls):
        """验证配置的有效性"""
        errors = []
        
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-key-should-be-changed':
            errors.append("SECRET_KEY should be set to a secure value")
        
        if not cls.JWT_SECRET_KEY or cls.JWT_SECRET_KEY == 'jwt-dev-key-change-in-production':
            errors.append("JWT_SECRET_KEY should be set to a secure value")
        
        if cls.USER_VALIDATION['PASSWORD_MIN_LENGTH'] < 6:
            errors.append("PASSWORD_MIN_LENGTH should be at least 6")
        
        return errors

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    SQLALCHEMY_ECHO = True  # 打印SQL语句
    
    # 开发环境使用具体的前端地址，更安全
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:8080', 'http://127.0.0.1:3000']


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # 生产环境强制使用环境变量
    def __init__(self):
        super().__init__()
        # 验证必要的环境变量
        self._validate_production_config()
    
    def _validate_production_config(self):
        """验证生产环境必要配置"""
        required_vars = ['SECRET_KEY', 'JWT_SECRET_KEY', 'DATABASE_URI']
        missing_vars = []
        
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Production environment requires these environment variables: {', '.join(missing_vars)}")
    
    # 生产环境使用HTTPS
    PREFERRED_URL_SCHEME = 'https'
    
    # 生产环境限制CORS来源
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'https://yourdomain.com').split(',')


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    
    # 测试环境配置
    USER_VALIDATION = {
        'USERNAME_MIN_LENGTH': 2,  # 测试时允许更短的用户名
        'USERNAME_MAX_LENGTH': 50,
        'PASSWORD_MIN_LENGTH': 4,  # 测试时允许更短的密码
        'PASSWORD_MAX_LENGTH': 128,
        'REQUIRE_PASSWORD_COMPLEXITY': False
    }
    
    # 测试时禁用CSRF保护
    WTF_CSRF_ENABLED = False

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """获取配置类"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(config_name, config['default'])


def validate_all_configs():
    """验证所有配置类"""
    errors = {}
    for name, config_class in config.items():
        if name != 'default':
            try:
                errors[name] = config_class.validate_config()
            except Exception as e:
                errors[name] = [str(e)]
    return errors
