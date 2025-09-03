import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-should-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'mysql+pymysql://root:123456@localhost/football_management_system'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-dev-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # 添加URL构建相关配置
    SERVER_NAME = os.environ.get('SERVER_NAME', 'localhost:5000')
    APPLICATION_ROOT = os.environ.get('APPLICATION_ROOT', '/')
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME', 'http')

class DevelopmentConfig(Config):
    DEBUG = True
    # 移除或注释掉任何 FLASK_ENV 相关的配置
