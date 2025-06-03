from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.team import Team
from app.models.player import Player
from app.models.player_team_history import PlayerTeamHistory

teams_bp = Blueprint('teams', __name__)

@teams_bp.route('', methods=['GET'])
def get_teams():
    """获取所有球队信息（公共接口）"""
    try:
        teams = Team.query.all()
        teams_data = []
        
        for team in teams:
            team_dict = team.to_dict()
            team_dict['teamName'] = team_dict['name']
            
            # 获取球队在当前赛事中的球员
            team_players = []
            for history in team.player_histories:
                team_players.append({
                    'name': history.player.name,
                    'number': str(history.player_number),
                    'studentId': history.player_id,
                    'id': history.player_id
                })
            
            team_dict['players'] = team_players
            
            # 根据tournament_id确定matchType
            tournament_to_match_type = {1: 'champions-cup', 2: 'womens-cup', 3: 'eight-a-side'}
            team_dict['matchType'] = tournament_to_match_type.get(team.tournament_id, 'champions-cup')
            
            teams_data.append(team_dict)
        
        return jsonify({'status': 'success', 'data': teams_data}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

@teams_bp.route('/<int:team_id>', methods=['GET'])
def get_team(team_id):
    """获取单个球队信息"""
    try:
        team = Team.query.get(team_id)
        if not team:
            return jsonify({'status': 'error', 'message': '球队不存在'}), 404
        
        team_dict = team.to_dict()
        team_dict['teamName'] = team_dict['name']
        
        # 获取球员信息
        team_players = []
        for history in team.player_histories:
            team_players.append({
                'name': history.player.name,
                'number': str(history.player_number),
                'studentId': history.player_id,
                'id': history.player_id
            })
        
        team_dict['players'] = team_players
        
        # 根据tournament_id确定matchType
        tournament_to_match_type = {1: 'champions-cup', 2: 'womens-cup', 3: 'eight-a-side'}
        team_dict['matchType'] = tournament_to_match_type.get(team.tournament_id, 'champions-cup')
        
        return jsonify({'status': 'success', 'data': team_dict}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500
