import os

class Config:
    """基本配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    # 数据库连接信息
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/football_management_system'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/football_management_system_test'

class ProductionConfig(Config):
    """生产环境配置"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://username:password@localhost/football_management_system'

# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}