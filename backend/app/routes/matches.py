"""
比赛模块路由层
处理HTTP请求和响应
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from pydantic import ValidationError
from app.services.match_service import MatchService
from app.schemas import MatchCreate, MatchUpdate

# 创建蓝图
matches_bp = Blueprint('matches', __name__)

# 初始化服务
match_service = MatchService()


@matches_bp.route('', methods=['POST'])
@jwt_required()
def create_match():
    """创建比赛"""
    try:
        payload = MatchCreate(**(request.get_json() or {}))
        # 服务层当前使用 team1/team2/date/matchType 等键，这里保持原前端负载结构不变
        result = match_service.create_match(payload.model_dump(by_alias=True))
        return jsonify(result), 201
    except ValidationError as e:
        return jsonify({'status': 'error', 'message': '参数验证失败', 'details': e.errors()}), 400


@matches_bp.route('/<string:match_id>/complete', methods=['PUT'])
@jwt_required()
def complete_match(match_id: str):
    """标记比赛为已完赛"""
    result = match_service.complete_match(match_id)
    return jsonify(result), 200


@matches_bp.route('', methods=['GET'])
@jwt_required()
def get_matches():
    """获取所有比赛"""
    status = request.args.get('status')
    match_type = request.args.get('type')
    limit = request.args.get('limit', type=int)
    sort = request.args.get('sort')
    
    result = match_service.get_all_matches(status=status, match_type=match_type)
    
    # 简单的内存排序和切片，如果数据量大建议移至 Service 层 SQL 处理
    if result.get('status') == 'success' and isinstance(result.get('data'), list):
        matches = result['data']
        if sort == 'desc':
            matches.sort(key=lambda x: x.get('date') or '', reverse=True)
        if limit:
            matches = matches[:limit]
        result['data'] = matches
        
    return jsonify(result), 200


@matches_bp.route('/<string:match_id>', methods=['PUT'])
@jwt_required()
def update_match(match_id: str):
    """更新比赛信息"""
    try:
        payload = MatchUpdate(**(request.get_json() or {}))
        result = match_service.update_match(match_id, payload.model_dump(exclude_unset=True, by_alias=True))
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({'status': 'error', 'message': '参数验证失败', 'details': e.errors()}), 400


@matches_bp.route('/<string:match_id>', methods=['DELETE'])
@jwt_required()
def delete_match(match_id: str):
    """删除比赛"""
    result = match_service.delete_match(match_id)
    return jsonify(result), 200


@matches_bp.route('/match-records', methods=['GET'])
def get_match_records():
    """
    获取比赛记录，支持筛选类型、搜索关键字、状态筛选和分页
    """
    # 从 query parameters 获取参数
    match_type = request.args.get('type', '')
    status_filter = request.args.get('status', '')
    keyword = request.args.get('keyword', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))

    result = match_service.get_match_records(
        match_type=match_type,
        status_filter=status_filter,
        keyword=keyword,
        page=page,
        page_size=page_size
    )
    return jsonify(result), 200


@matches_bp.route('/<string:match_id>', methods=['GET'])
def get_match_detail(match_id: str):
    """获取单个比赛的详细信息"""
    result = match_service.get_match_detail(match_id)
    return jsonify(result), 200
