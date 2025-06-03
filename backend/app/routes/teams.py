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

@teams_bp.route('', methods=['POST'])
@jwt_required()
def create_team():
    """创建球队和球员信息"""
    data = request.get_json()
    
    if not data or not data.get('teamName'):
        return jsonify({'status': 'error', 'message': '球队名称不能为空'}), 400
    
    # 检查球队名称是否已存在
    existing_team = Team.query.filter_by(name=data['teamName']).first()
    if existing_team:
        return jsonify({'status': 'error', 'message': '球队名称已存在'}), 400
    
    try:
        # 根据matchType确定赛事ID
        match_type_to_tournament = {
            'champions-cup': 1,  # 冠军杯
            'womens-cup': 2,     # 巾帼杯
            'eight-a-side': 3    # 八人制比赛
        }
        tournament_id = match_type_to_tournament.get(data.get('matchType', 'champions-cup'), 1)
        
        # 创建球队
        new_team = Team(
            name=data['teamName'],
            tournament_id=tournament_id,
            group_id=data.get('groupId')
        )
        db.session.add(new_team)
        db.session.flush()
        
        # 创建球员和球员-队伍历史记录
        players_data = data.get('players', [])
        for player_data in players_data:
            if player_data.get('name') and player_data.get('studentId'):
                player_id = player_data['studentId']
                
                # 检查球员是否已存在
                existing_player = Player.query.get(player_id)
                if not existing_player:
                    new_player = Player(
                        id=player_id,
                        name=player_data['name']
                    )
                    db.session.add(new_player)
                else:
                    # 更新球员姓名
                    existing_player.name = player_data['name']
                
                # 创建球员-队伍历史记录
                player_history = PlayerTeamHistory(
                    player_id=player_id,
                    player_number=int(player_data.get('number', 1)),
                    team_id=new_team.id,
                    tournament_id=tournament_id
                )
                db.session.add(player_history)
        
        db.session.commit()
        
        # 返回创建成功的球队信息
        team_dict = new_team.to_dict()
        team_dict['teamName'] = team_dict['name']
        
        # 获取球员信息
        team_players = []
        for history in PlayerTeamHistory.query.filter_by(team_id=new_team.id, tournament_id=tournament_id).all():
            team_players.append({
                'name': history.player.name,
                'number': str(history.player_number),
                'studentId': history.player_id,
                'id': history.player_id
            })
        
        team_dict['players'] = team_players
        team_dict['matchType'] = data.get('matchType', 'champions-cup')
        
        return jsonify({
            'status': 'success', 
            'message': '球队创建成功',
            'data': team_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500

@teams_bp.route('/<int:team_id>', methods=['PUT'])
@jwt_required()
def update_team(team_id):
    """更新球队信息"""
    data = request.get_json()
    
    try:
        team = Team.query.get(team_id)
        if not team:
            return jsonify({'status': 'error', 'message': '球队不存在'}), 404
        
        # 更新球队信息
        if data.get('teamName'):
            team.name = data['teamName']
        
        # 删除原有的球员-队伍历史记录
        PlayerTeamHistory.query.filter_by(team_id=team_id, tournament_id=team.tournament_id).delete()
        
        # 添加新的球员和历史记录
        players_data = data.get('players', [])
        for player_data in players_data:
            if player_data.get('name') and player_data.get('studentId'):
                player_id = player_data['studentId']
                
                # 检查球员是否已存在
                existing_player = Player.query.get(player_id)
                if not existing_player:
                    new_player = Player(
                        id=player_id,
                        name=player_data['name']
                    )
                    db.session.add(new_player)
                else:
                    # 更新球员姓名
                    existing_player.name = player_data['name']
                
                # 创建新的球员-队伍历史记录
                player_history = PlayerTeamHistory(
                    player_id=player_id,
                    player_number=int(player_data.get('number', 1)),
                    team_id=team_id,
                    tournament_id=team.tournament_id
                )
                db.session.add(player_history)
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': '更新成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500

@teams_bp.route('/<int:team_id>', methods=['DELETE'])
@jwt_required()
def delete_team(team_id):
    """删除球队"""
    try:
        team = Team.query.get(team_id)
        if not team:
            return jsonify({'status': 'error', 'message': '球队不存在'}), 404
        
        # 删除关联的球员-队伍历史记录
        PlayerTeamHistory.query.filter_by(team_id=team_id).delete()
        
        # 删除球队
        db.session.delete(team)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': '删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500
