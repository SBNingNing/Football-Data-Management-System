"""
数据库实例的单一出口
为避免项目中出现多个 SQLAlchemy/JWT 实例导致的 "app not registered" 错误，
此模块仅从 app.extensions 重新导出已初始化的全局实例。
"""
from app.extensions import db, jwt  # noqa: F401

