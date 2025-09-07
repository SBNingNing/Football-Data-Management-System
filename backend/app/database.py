"""
数据库配置文件
用于避免循环导入问题
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# 创建数据库实例
db = SQLAlchemy()
jwt = JWTManager()
