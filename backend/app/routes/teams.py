"""
球队路由层
负责处理HTTP请求和响应
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.services.team_service import TeamService
from app.middleware.team_middleware import (
    validate_team_data,
    validate_team_id, 
    validate_team_name,
    validate_query_params,
    handle_team_errors,
    log_team_operation,
    TeamMiddleware
)
from app.utils.team_utils import TeamUtils

teams_bp = Blueprint('teams', __name__)


@teams_bp.route('/<team_name>/new-api', methods=['GET'])
@validate_team_name
@handle_team_errors
@log_team_operation('查询新API')
def get_team_new_api(team_name):
    """使用新架构根据球队名称获取球队统计信息和历史记录"""
    try:
        team_info, error = TeamService.get_team_by_name_new_api(team_name)
        
        if error:
            return jsonify(TeamMiddleware.format_error_response(error)), 404
        
        # 添加matchType信息
        for record in team_info.get('records', []):
            if 'tournament_id' in record:
                # 这里可以根据tournament_id获取tournament对象并确定matchType
                # 为了简化，我们使用工具函数的默认逻辑
                record['matchType'] = record.get('matchType', 'champions-cup')
        
        return jsonify(TeamMiddleware.format_team_response(team_info)), 200
        
    except Exception as e:
        return jsonify(TeamMiddleware.format_error_response(f'查询失败: {str(e)}')), 500


@teams_bp.route('/<team_name>', methods=['GET'])
@validate_team_name
@handle_team_errors
@log_team_operation('查询')
def get_team(team_name):
    """根据球队名称获取球队统计信息和历史记录"""
    try:
        team_info, error = TeamService.get_team_by_name(team_name)
        
        if error:
            return jsonify(TeamMiddleware.format_error_response(error)), 404
        
        # 为每条记录添加matchType
        for record in team_info.get('records', []):
            if not record.get('matchType'):
                # 如果没有matchType，根据tournament信息确定
                record['matchType'] = TeamUtils.determine_match_type(None)  # 可以根据需要改进
        
        return jsonify(TeamMiddleware.format_team_response(team_info)), 200
        
    except Exception as e:
        return jsonify(TeamMiddleware.format_error_response(f'获取失败: {str(e)}')), 500


@teams_bp.route('', methods=['GET'])
@validate_query_params
@handle_team_errors
@log_team_operation('列表查询')
def get_teams():
    """获取所有球队信息（公共接口）"""
    try:
        # 解析查询参数
        validated_params = TeamMiddleware.validate_query_params(request.args)
        
        teams_data, error = TeamService.get_all_teams(
            group_by_name=validated_params['group_by_name']
        )
        
        if error:
            return jsonify(TeamMiddleware.format_error_response(error)), 500
        
        # 为每个球队添加matchType（如果没有的话）
        for team in teams_data:
            if not team.get('matchType'):
                team['matchType'] = TeamUtils.determine_match_type(None)
        
        return jsonify(TeamMiddleware.format_team_response(teams_data)), 200
        
    except Exception as e:
        return jsonify(TeamMiddleware.format_error_response(f'获取失败: {str(e)}')), 500


@teams_bp.route('', methods=['POST'])
@jwt_required()
@validate_team_data
@handle_team_errors
@log_team_operation('创建')
def create_team():
    """创建球队和球员信息"""
    try:
        data = request.get_json()
        
        # 格式化球队名称
        data['teamName'] = TeamUtils.format_team_name(data['teamName'])
        
        # 验证球员数据
        players = data.get('players', [])
        is_valid, error_msg = TeamUtils.validate_player_data(players)
        if not is_valid:
            return jsonify(TeamMiddleware.format_error_response(error_msg)), 400
        
        team_dict, error = TeamService.create_team(data)
        
        if error:
            return jsonify(TeamMiddleware.format_error_response(error)), 400
        
        # 添加matchType
        if not team_dict.get('matchType'):
            team_dict['matchType'] = TeamUtils.determine_match_type(None)
        
        return jsonify(TeamMiddleware.format_team_response(
            team_dict,
            '球队创建成功'
        )), 201
        
    except Exception as e:
        return jsonify(TeamMiddleware.format_error_response(f'创建失败: {str(e)}')), 500


@teams_bp.route('/<int:team_id>', methods=['PUT'])
@jwt_required()
@validate_team_id
@validate_team_data
@handle_team_errors
@log_team_operation('更新')
def update_team(team_id):
    """更新球队信息"""
    try:
        data = request.get_json()
        
        # 格式化球队名称（如果提供了）
        if data.get('teamName'):
            data['teamName'] = TeamUtils.format_team_name(data['teamName'])
        
        # 验证球员数据（如果提供了）
        if 'players' in data:
            players = data['players']
            is_valid, error_msg = TeamUtils.validate_player_data(players)
            if not is_valid:
                return jsonify(TeamMiddleware.format_error_response(error_msg)), 400
        
        team_dict, error = TeamService.update_team(team_id, data)
        
        if error:
            if '不存在' in error:
                status_code = 404
            elif '已存在' in error or '目标赛事' in error:
                status_code = 400
            else:
                status_code = 500
            return jsonify(TeamMiddleware.format_error_response(error)), status_code
        
        # 添加matchType
        if not team_dict.get('matchType'):
            team_dict['matchType'] = TeamUtils.determine_match_type(None)
        
        return jsonify(TeamMiddleware.format_team_response(
            team_dict,
            '更新成功'
        )), 200
        
    except Exception as e:
        return jsonify(TeamMiddleware.format_error_response(f'更新失败: {str(e)}')), 500


@teams_bp.route('/<int:team_id>', methods=['DELETE'])
@jwt_required()
@validate_team_id
@handle_team_errors
@log_team_operation('删除')
def delete_team(team_id):
    """删除球队"""
    try:
        success, error = TeamService.delete_team(team_id)
        
        if error:
            status_code = 404 if '不存在' in error else 500
            return jsonify(TeamMiddleware.format_error_response(error)), status_code
        
        return jsonify(TeamMiddleware.format_team_response(
            None,
            '删除成功'
        )), 200
        
    except Exception as e:
        return jsonify(TeamMiddleware.format_error_response(f'删除失败: {str(e)}')), 500
