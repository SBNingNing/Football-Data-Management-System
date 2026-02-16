"""
赛季路由层 - 处理HTTP请求和响应
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from app.services.season_service import SeasonService
from app.schemas import SeasonCreate, SeasonUpdate, SeasonOut
from app.utils.logger import get_logger

logger = get_logger(__name__)

seasons_bp = Blueprint('seasons', __name__)


@seasons_bp.route('', methods=['GET'])
def get_seasons():
    """获取所有赛季信息"""
    try:
        seasons = SeasonService.get_all_seasons()
        # 统一使用 SeasonOut 序列化（保持字段名不变）
        seasons_out = [SeasonOut(**s).model_dump(by_alias=True) for s in seasons]
        return jsonify({'status': 'success', 'data': seasons_out}), 200
        
    except Exception as e:
        logger.error(f"获取赛季列表失败: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'获取失败: {str(e)}'
        }), 500


@seasons_bp.route('/<int:season_id>', methods=['GET'])
def get_season(season_id):
    """根据ID获取单个赛季信息"""
    try:
        season = SeasonService.get_season_by_id(season_id)
        season_out = SeasonOut(**season).model_dump(by_alias=True)
        return jsonify({'status': 'success', 'data': season_out}), 200
        
    except Exception as e:
        logger.error(f"获取赛季信息失败: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'获取失败: {str(e)}'
        }), 500


@seasons_bp.route('', methods=['POST'])
@jwt_required()
def create_season():
    """创建新赛季"""
    try:
        payload = SeasonCreate(**(request.get_json() or {}))
        season_data, message = SeasonService.create_season(payload.model_dump(by_alias=True))
        season_out = SeasonOut(**season_data).model_dump(by_alias=True)
        return jsonify({'status': 'success', 'message': message, 'data': season_out}), 201
        
    except IntegrityError:
        return jsonify({
            'status': 'error', 
            'message': '赛季名称已存在'
        }), 400
    except ValidationError as e:
        return jsonify({
            'status': 'error', 
            'message': '参数验证失败',
            'details': e.errors()
        }), 400
    except ValueError as e:
        return jsonify({
            'status': 'error', 
            'message': str(e)
        }), 400
    except Exception as e:
        import traceback
        logger.error(f"创建赛季失败: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'status': 'error', 
            'message': f'创建失败: {str(e)}'
        }), 500


@seasons_bp.route('/<int:season_id>', methods=['PUT'])
@jwt_required()
def update_season(season_id):
    """更新赛季信息"""
    try:
        payload = SeasonUpdate(**(request.get_json() or {}))
        season_data, message = SeasonService.update_season(season_id, payload.model_dump(exclude_unset=True, by_alias=True))
        season_out = SeasonOut(**season_data).model_dump(by_alias=True)
        return jsonify({'status': 'success', 'message': message, 'data': season_out}), 200
        
    except IntegrityError:
        return jsonify({
            'status': 'error', 
            'message': '赛季名称已存在'
        }), 400
    except ValidationError as e:
        return jsonify({
            'status': 'error', 
            'message': '参数验证失败',
            'details': e.errors()
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
def delete_season(season_id):
    """删除赛季"""
    try:
        logger.info(f"请求删除赛季 ID: {season_id}")
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
