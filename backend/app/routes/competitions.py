from flask import Blueprint, request, jsonify
from app.services.competition_service import CompetitionService
from app.middleware.auth_middleware import auth_required
from app.middleware.validation_middleware import validate_json
from app.middleware.competition_middleware import validate_competition_data, validate_competition_id
from app.utils.competition_utils import CompetitionUtils

competitions_bp = Blueprint('competitions', __name__)

@competitions_bp.route('', methods=['GET'])
def get_competitions():
    """获取所有赛事信息"""
    try:
        # 获取查询参数
        sort_by = request.args.get('sort_by', 'name')
        search_term = request.args.get('search', '')
        
        competitions, error = CompetitionService.get_all_competitions()
        
        if error:
            return jsonify(CompetitionUtils.format_error_response(error)), 500
        
        # 应用过滤和排序
        if search_term:
            competitions = CompetitionUtils.filter_competitions(competitions, search_term)
        
        competitions = CompetitionUtils.sort_competitions(competitions, sort_by)
        
        # 添加统计信息
        statistics = CompetitionUtils.get_competition_statistics(competitions)
        
        response_data = {
            'competitions': competitions,
            'statistics': statistics
        }
        
        return jsonify(CompetitionUtils.format_competition_response(
            response_data, 
            f'成功获取{len(competitions)}个赛事信息'
        )), 200
        
    except Exception as e:
        return jsonify(CompetitionUtils.format_error_response(f'获取赛事列表失败: {str(e)}')), 500

@competitions_bp.route('/<int:competition_id>', methods=['GET'])
@validate_competition_id
def get_competition(competition_id):
    """根据ID获取单个赛事信息"""
    try:
        competition, error = CompetitionService.get_competition_by_id(competition_id)
        
        if error:
            status_code = 404 if '不存在' in error else 500
            return jsonify(CompetitionUtils.format_error_response(error)), status_code
        
        # 使用工具函数构建完整的竞赛数据
        enhanced_competition = CompetitionUtils.build_competition_dict(type('obj', (object,), competition)())
        enhanced_competition.update(competition)  # 合并原始数据
        
        return jsonify(CompetitionUtils.format_competition_response(
            enhanced_competition,
            '成功获取赛事信息'
        )), 200
        
    except Exception as e:
        return jsonify(CompetitionUtils.format_error_response(f'获取赛事信息失败: {str(e)}')), 500

@competitions_bp.route('', methods=['POST'])
@auth_required
@validate_json(['name'])
@validate_competition_data
def create_competition():
    """创建新赛事"""
    try:
        data = request.get_json()
        
        # 使用工具函数格式化名称
        formatted_name = CompetitionUtils.format_competition_name(data['name'])
        
        competition, error = CompetitionService.create_competition(formatted_name)
        
        if error:
            status_code = 400 if '已存在' in error or '不能为空' in error else 500
            return jsonify(CompetitionUtils.format_error_response(error)), status_code
        
        return jsonify(CompetitionUtils.format_competition_response(
            competition,
            '赛事创建成功'
        )), 201
        
    except Exception as e:
        return jsonify(CompetitionUtils.format_error_response(f'创建赛事失败: {str(e)}')), 500

@competitions_bp.route('/<int:competition_id>', methods=['PUT'])
@auth_required
@validate_competition_id
@validate_json()
@validate_competition_data
def update_competition(competition_id):
    """更新赛事信息"""
    try:
        data = request.get_json()
        
        # 格式化名称（如果提供了）
        if 'name' in data and data['name']:
            data['name'] = CompetitionUtils.format_competition_name(data['name'])
        
        competition, error = CompetitionService.update_competition(competition_id, data)
        
        if error:
            if '不存在' in error:
                status_code = 404
            elif '已存在' in error or '请提供' in error:
                status_code = 400
            else:
                status_code = 500
            return jsonify(CompetitionUtils.format_error_response(error)), status_code
        
        return jsonify(CompetitionUtils.format_competition_response(
            competition,
            '赛事更新成功'
        )), 200
        
    except Exception as e:
        return jsonify(CompetitionUtils.format_error_response(f'更新赛事失败: {str(e)}')), 500

@competitions_bp.route('/<int:competition_id>', methods=['DELETE'])
@auth_required
@validate_competition_id
def delete_competition(competition_id):
    """删除赛事"""
    try:
        result, error = CompetitionService.delete_competition(competition_id)
        
        if error:
            if '不存在' in error:
                status_code = 404
            elif '无法删除' in error:
                status_code = 400
            else:
                status_code = 500
            return jsonify(CompetitionUtils.format_error_response(error)), status_code
        
        return jsonify(CompetitionUtils.format_competition_response(
            None,
            '赛事删除成功'
        )), 200
        
    except Exception as e:
        return jsonify(CompetitionUtils.format_error_response(f'删除赛事失败: {str(e)}')), 500
