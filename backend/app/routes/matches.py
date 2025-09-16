"""
比赛模块路由层
处理HTTP请求和响应
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.match_service import MatchService
from app.schemas import MatchCreate, MatchUpdate
from app.middleware.match_middleware import (
    validate_create_match, validate_update_match, validate_get_match,
    validate_delete_match, validate_search_matches, MatchMiddleware
)

# 创建蓝图
matches_bp = Blueprint('matches', __name__)

# 初始化服务
match_service = MatchService()


@matches_bp.route('', methods=['POST'])
@jwt_required()
@validate_create_match
def create_match():
    """创建比赛"""
    payload = MatchCreate(**(request.get_json() or {}))
    # 服务层当前使用 team1/team2/date/matchType 等键，这里保持原前端负载结构不变
    result = match_service.create_match(payload.model_dump(by_alias=True))
    return jsonify(result), 201


@matches_bp.route('/<string:match_id>/complete', methods=['PUT'])
@jwt_required()
@validate_get_match
def complete_match(match_id: str):
    """标记比赛为已完赛"""
    result = match_service.complete_match(match_id)
    return jsonify(result), 200


@matches_bp.route('', methods=['GET'])
@jwt_required()
@MatchMiddleware.handle_match_errors
@MatchMiddleware.log_match_request
def get_matches():
    """获取所有比赛"""
    result = match_service.get_all_matches()
    return jsonify(result), 200


@matches_bp.route('/<string:match_id>', methods=['PUT'])
@jwt_required()
@validate_update_match
def update_match(match_id: str):
    """更新比赛信息"""
    payload = MatchUpdate(**(request.get_json() or {}))
    result = match_service.update_match(match_id, payload.model_dump(exclude_unset=True, by_alias=True))
    return jsonify(result), 200


@matches_bp.route('/<string:match_id>', methods=['DELETE'])
@jwt_required()
@validate_delete_match
def delete_match(match_id: str):
    """删除比赛"""
    result = match_service.delete_match(match_id)
    return jsonify(result), 200


@matches_bp.route('/match-records', methods=['GET'])
@jwt_required()
@validate_search_matches
def get_match_records(match_type: str = '', status_filter: str = '', 
                     keyword: str = '', page: int = 1, page_size: int = 10):
    """
    获取比赛记录，支持筛选类型、搜索关键字、状态筛选和分页
    参数:
      - type: 比赛类型 (championsCup, womensCup, eightASide)
      - status: 比赛状态 (待开始, 进行中, 已完赛)
      - keyword: 搜索关键字（比赛名称/球队/地点）
      - page: 页码（从1开始）
      - pageSize: 每页数量
    """
    result = match_service.get_match_records(
        match_type=match_type,
        status_filter=status_filter,
        keyword=keyword,
        page=page,
        page_size=page_size
    )
    return jsonify(result), 200


@matches_bp.route('/<string:match_id>', methods=['GET'])
@jwt_required()
@validate_get_match
def get_match_detail(match_id: str):
    """获取单个比赛的详细信息"""
    result = match_service.get_match_detail(match_id)
    return jsonify(result), 200
