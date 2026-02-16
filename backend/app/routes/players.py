"""
球员路由层 - 专注于HTTP请求处理和响应
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError
from app.services.player_service import PlayerService
from app.utils.logger import get_logger
from app.utils.response import success_response, error_response
from app.schemas.player import PlayerCreate, PlayerUpdate

players_bp = Blueprint('players', __name__)
logger = get_logger(__name__)


@players_bp.route('', methods=['GET'])
def get_players():
    """获取所有球员信息（公共接口）"""
    try:
        players_data = PlayerService.get_all_players()
        return success_response(players_data, message='获取球员信息成功', meta={'total': len(players_data)})
    except Exception as e:
        logger.error(f"获取球员列表失败: {str(e)}", exc_info=True)
        return error_response('PLAYER_LIST_ERROR', '获取球员信息失败', 500, detail=str(e))


@players_bp.route('/<string:player_id>', methods=['GET'])
def get_player(player_id):
    """获取单个球员信息"""
    try:
        player_data = PlayerService.get_player_by_id(player_id)
        if not player_data:
            return error_response('PLAYER_NOT_FOUND', '球员不存在', 404)
        return success_response(player_data, message='获取球员信息成功')
    except Exception as e:
        logger.error(f"获取球员 {player_id} 信息失败: {str(e)}", exc_info=True)
        return error_response('PLAYER_DETAIL_ERROR', '获取失败', 500, detail=str(e))


@players_bp.route('', methods=['POST'])
@jwt_required()
def create_player():
    """创建球员信息"""
    try:
        payload = request.get_json() or {}
        model = PlayerCreate(**payload)
        new_player = PlayerService.create_player({
            'name': model.name,
            'studentId': model.student_id
        })
        return success_response(new_player.to_dict(), message='球员创建成功', status_code=201)
    except ValueError as e:
        return error_response('PLAYER_CREATE_CONFLICT', str(e), 400)
    except ValidationError as e:
        return error_response('VALIDATION_ERROR', '参数验证失败', 400, detail=e.errors())
    except Exception as e:
        logger.error(f"创建球员失败: {str(e)}", exc_info=True)
        return error_response('PLAYER_CREATE_ERROR', '创建失败', 500, detail=str(e))


@players_bp.route('/<string:player_id>', methods=['PUT'])
@jwt_required()
def update_player(player_id):
    """更新球员信息"""
    try:
        payload = request.get_json() or {}
        from pydantic import ValidationError  # type: ignore
        model = PlayerUpdate(**payload)
        PlayerService.update_player(player_id, model.model_dump(exclude_unset=True, by_alias=True))
        return success_response(message='更新成功')
    except ValueError as e:
        return error_response('PLAYER_NOT_FOUND', str(e), 404)
    except ValidationError as e:
        return error_response('VALIDATION_ERROR', '参数验证失败', 400, detail=e.errors())
    except Exception as e:
        logger.error(f"更新球员 {player_id} 失败: {str(e)}", exc_info=True)
        return error_response('PLAYER_UPDATE_ERROR', '更新失败', 500, detail=str(e))


@players_bp.route('/<string:player_id>', methods=['DELETE'])
@jwt_required()
def delete_player(player_id):
    """删除球员"""
    try:
        PlayerService.delete_player(player_id)
        return success_response(message='删除成功')
    except ValueError as e:
        return error_response('PLAYER_NOT_FOUND', str(e), 404)
    except Exception as e:
        logger.error(f"删除球员 {player_id} 失败: {str(e)}", exc_info=True)
        return error_response('PLAYER_DELETE_ERROR', '删除失败', 500, detail=str(e))
