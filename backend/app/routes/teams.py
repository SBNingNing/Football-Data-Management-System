"""
球队路由层
负责处理HTTP请求和响应
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from app.services.team_service import TeamService
from app.schemas import TeamCreate
from app.utils.team_utils import TeamUtils

teams_bp = Blueprint('teams', __name__)


@teams_bp.route('/<team_name>/new-api', methods=['GET'])
def get_team_new_api(team_name):
    """使用新架构根据球队名称获取球队统计信息和历史记录"""
    try:
        team_info, error = TeamService.get_team_by_name_new_api(team_name)
        
        if error:
            return jsonify({'error': error}), 404
        
        # 添加match_type信息
        for record in team_info.get('records', []):
            if 'tournament_id' in record:
                # 这里可以根据tournament_id获取tournament对象并确定match_type
                # 为了简化，我们使用工具函数的默认逻辑
                record['match_type'] = record.get('match_type', 'champions-cup')
        
        return jsonify(team_info), 200
        
    except Exception as e:
        return jsonify({'error': f'查询失败: {str(e)}'}), 500


@teams_bp.route('/<team_name>', methods=['GET'])
def get_team(team_name):
    """根据球队名称获取球队统计信息和历史记录"""
    try:
        team_info, error = TeamService.get_team_by_name(team_name)
        
        if error:
            return jsonify({'error': error}), 404
        
        # 为每条记录添加match_type
        for record in team_info.get('records', []):
            if not record.get('match_type'):
                # 如果没有match_type，根据tournament信息确定
                record['match_type'] = TeamUtils.determine_match_type(None)  # 可以根据需要改进
        
        return jsonify(team_info), 200
        
    except Exception as e:
        return jsonify({'error': f'获取失败: {str(e)}'}), 500


@teams_bp.route('', methods=['GET'])
def get_teams():
    """获取所有球队信息（公共接口）"""
    try:
        # 解析查询参数
        
        teams_data, error = TeamService.get_all_teams(
            group_by_name=request.args.get('group_by_name') == 'true'
        )
        
        if error:
            return jsonify({'error': error}), 500
        
        # 为每个球队添加match_type（如果没有的话）
        for team in teams_data:
            if not team.get('match_type'):
                if team.get('competition_name'):
                    team['match_type'] = team['competition_name']
                else:
                    team['match_type'] = TeamUtils.determine_match_type(None)
        
        return jsonify(teams_data), 200
        
    except Exception as e:
        return jsonify({'error': f'获取失败: {str(e)}'}), 500


@teams_bp.route('', methods=['POST'])
@jwt_required()
def create_team():
    """创建球队和球员信息"""
    try:
        # 使用 Pydantic Schema 验证输入
        payload = TeamCreate(**(request.get_json() or {}))
        data = payload.model_dump(by_alias=True)
        
        # 格式化球队名称
        data['teamName'] = TeamUtils.format_team_name(data['teamName'])
        
        # 验证球员数据 (保留原有逻辑，或迁移到 Schema)
        players = data.get('players', [])
        is_valid, error_msg = TeamUtils.validate_player_data(players)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        team_dict, error = TeamService.create_team(data)
        
        if error:
            return jsonify({'error': error}), 400
        
        # 添加match_type
        if not team_dict.get('match_type'):
            team_dict['match_type'] = TeamUtils.determine_match_type(None)
        
        message = '球队创建成功' if team_dict.get('is_new', True) else '球队更新成功'
        
        return jsonify({
            'success': True,
            'message': message,
            'data': team_dict
        }), 201

    except ValidationError as e:
        return jsonify({'error': '参数验证失败', 'details': e.errors()}), 400
        
    except Exception as e:
        return jsonify({'error': f'创建失败: {str(e)}'}), 500


@teams_bp.route('/<int:team_id>', methods=['PUT'])
@jwt_required()
def update_team(team_id):
    """更新球队信息 (部分字段可选)。"""
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
                return jsonify({'error': error_msg}), 400
        
        team_dict, error = TeamService.update_team(team_id, data)
        
        if error:
            if '不存在' in error:
                status_code = 404
            elif '已存在' in error or '目标赛事' in error:
                status_code = 400
            else:
                status_code = 500
            return jsonify({'error': error}), status_code
        
        # 添加match_type
        if not team_dict.get('match_type'):
            team_dict['match_type'] = TeamUtils.determine_match_type(None)
        
        return jsonify({
            'success': True,
            'message': '更新成功',
            'data': team_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'更新失败: {str(e)}'}), 500


# 按名称更新（最新参赛实例或指定 tournamentId / matchType 选择）
@teams_bp.route('/by-name/<team_name>', methods=['PUT'])
@jwt_required()
def update_team_by_name(team_name):
    """按名称更新球队最近参赛实例: 优先 tournamentId -> matchType -> 最新 participation。"""
    try:
        data = request.get_json() or {}
        from app.models.team_base import TeamBase
        from app.models.team_tournament_participation import TeamTournamentParticipation
        from app.models.tournament import Tournament

        base = TeamBase.query.filter_by(name=team_name).first()
        if not base:
            return jsonify({'error': '球队不存在'}), 404

        q = TeamTournamentParticipation.query.filter_by(team_base_id=base.id)
        target_participation = None

        # 指定 tournament_id
        if data.get('tournament_id'):
            target_participation = q.filter_by(tournament_id=data['tournament_id']).first()
            if not target_participation:
                return jsonify({'error': '指定赛事参赛记录不存在'}), 404
        else:
            # match_type 过滤
            if data.get('match_type'):
                canonical, _ = TeamUtils.normalize_match_type(data['match_type'])
                match_map = {
                    'champions-cup': 1,
                    'womens-cup': 2,
                    'eight-a-side': 3
                }
                tid = match_map.get(canonical)
                if tid:
                    target_participation = q.filter_by(tournament_id=tid).order_by(TeamTournamentParticipation.id.desc()).first()
            # 若仍未找到，取最新
            if not target_participation:
                target_participation = q.order_by(TeamTournamentParticipation.id.desc()).first()

        if not target_participation:
            return jsonify({'error': '未找到参赛记录'}), 404

        # 直接复用 update_team 逻辑: 构造部分更新数据
        team_dict, error = TeamService.update_team(target_participation.id, data)
        if error:
            status_code = 404 if '不存在' in error else 400
            return jsonify({'error': error}), status_code

        if not team_dict.get('match_type'):
            team_dict['match_type'] = TeamUtils.determine_match_type(None)

        return jsonify({
            'success': True,
            'message': '按名称更新成功',
            'data': team_dict
        }), 200
    except Exception as e:
        return jsonify({'error': f'更新失败: {str(e)}'}), 500


@teams_bp.route('/<int:team_id>', methods=['DELETE'])
@jwt_required()
def delete_team(team_id):
    """删除球队"""
    try:
        success, error = TeamService.delete_team(team_id)
        
        if error:
            status_code = 404 if '不存在' in error else 500
            return jsonify({'error': error}), status_code
        
        return jsonify({
            'success': True,
            'message': '删除成功'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'删除失败: {str(e)}'}), 500
