"""
赛季路由层 - 处理HTTP请求和响应
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from app.services.season_service import SeasonService
from app.middleware.season_middleware import (
    validate_season_creation_data,
    validate_season_update_data,
    validate_season_id,
    log_season_operation,
    preprocess_season_data
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

seasons_bp = Blueprint('seasons', __name__)


@seasons_bp.route('', methods=['GET'])
def get_seasons():
    """获取所有赛季信息"""
    try:
        seasons = SeasonService.get_all_seasons()
        
        return jsonify({
            'status': 'success',
            'data': seasons
        }), 200
        
    except Exception as e:
        logger.error(f"获取赛季列表失败: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'获取失败: {str(e)}'
        }), 500


@seasons_bp.route('/<int:season_id>', methods=['GET'])
@validate_season_id
def get_season(season_id):
    """根据ID获取单个赛季信息"""
    try:
        season = SeasonService.get_season_by_id(season_id)
        
        return jsonify({
            'status': 'success',
            'data': season
        }), 200
        
    except Exception as e:
        logger.error(f"获取赛季信息失败: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'获取失败: {str(e)}'
        }), 500


@seasons_bp.route('', methods=['POST'])
@jwt_required()
@validate_season_creation_data
@preprocess_season_data
@log_season_operation('创建')
def create_season():
    """创建新赛季"""
    try:
        from flask import request
        data = request.get_json()
        
        season_data, message = SeasonService.create_season(data)
        
        return jsonify({
            'status': 'success',
            'message': message,
            'data': season_data
        }), 201
        
    except IntegrityError:
        return jsonify({
            'status': 'error', 
            'message': '赛季名称已存在'
        }), 400
    except ValueError as e:
        return jsonify({
            'status': 'error', 
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"创建赛季失败: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'创建失败: {str(e)}'
        }), 500


@seasons_bp.route('/<int:season_id>', methods=['PUT'])
@jwt_required()
@validate_season_id
@validate_season_update_data
@preprocess_season_data
@log_season_operation('更新')
def update_season(season_id):
    """更新赛季信息"""
    try:
        from flask import request
        data = request.get_json()
        
        season_data, message = SeasonService.update_season(season_id, data)
        
        return jsonify({
            'status': 'success',
            'message': message,
            'data': season_data
        }), 200
        
    except IntegrityError:
        return jsonify({
            'status': 'error', 
            'message': '赛季名称已存在'
        }), 400
    except ValueError as e:
        return jsonify({
            'status': 'error', 
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"更新赛季失败: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'更新失败: {str(e)}'
        }), 500


@seasons_bp.route('/<int:season_id>', methods=['DELETE'])
@jwt_required()
@validate_season_id
@log_season_operation('删除')
def delete_season(season_id):
    """删除赛季"""
    try:
        message = SeasonService.delete_season(season_id)
        
        return jsonify({
            'status': 'success',
            'message': message
        }), 200
        
    except ValueError as e:
        return jsonify({
            'status': 'error', 
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"删除赛季失败: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'删除失败: {str(e)}'
        }), 500
