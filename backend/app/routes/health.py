from flask import Blueprint, jsonify
from sqlalchemy import text
from app.database import db
from app.utils.logger import get_logger

health_bp = Blueprint('health', __name__)
logger = get_logger(__name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """基础健康检查: 应用/数据库状态"""
    db_status = 'up'
    try:
        db.session.execute(text('SELECT 1'))
    except Exception as e:
        logger.error(f'Database health check failed: {e}')
        db_status = 'down'
    return jsonify({
        'app': 'Football Management System',
        'version': '1.0.0',
        'db': db_status,
        'status': 'ok' if db_status == 'up' else 'degraded'
    })
