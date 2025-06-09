from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.team import Team
from app.models.player import Player
from app.models.player_team_history import PlayerTeamHistory

teams_bp = Blueprint('teams', __name__)

def determine_match_type(tournament):
    """根据赛事名称确定matchType"""
    if tournament:
        tournament_name = tournament.name.lower()
        if '冠军杯' in tournament_name or 'champions' in tournament_name:
            return 'champions-cup'
        elif '巾帼杯' in tournament_name or 'womens' in tournament_name:
            return 'womens-cup'
        elif '八人制' in tournament_name or 'eight' in tournament_name:
            return 'eight-a-side'
        else:
            return 'champions-cup'
    else:
        return 'champions-cup'

@teams_bp.route('/<team_name>', methods=['GET'])
def get_team(team_name):
    """根据球队名称获取球队统计信息和历史记录"""
    try:
        # 查询该球队名称的所有记录
        team_records = Team.query.filter_by(name=team_name).all()
        if not team_records:
            return jsonify({'status': 'error', 'message': '球队不存在'}), 404
        
        # 统计总数据
        total_goals = sum(record.tournament_goals for record in team_records)
        total_goals_conceded = sum(record.tournament_goals_conceded for record in team_records)
        total_goal_difference = sum(record.tournament_goal_difference for record in team_records)
        total_red_cards = sum(record.tournament_red_cards for record in team_records)
        total_yellow_cards = sum(record.tournament_yellow_cards for record in team_records)
        total_points = sum(record.tournament_points for record in team_records)
        
        # 计算历史最好排名（最小的非零排名）
        valid_ranks = [record.tournament_rank for record in team_records if record.tournament_rank and record.tournament_rank > 0]
        best_rank = min(valid_ranks) if valid_ranks else None
        
        # 构建返回数据
        team_info = {
            'teamName': team_name,
            'totalGoals': total_goals,
            'totalGoalsConceded': total_goals_conceded,
            'totalGoalDifference': total_goal_difference,
            'totalRedCards': total_red_cards,
            'totalYellowCards': total_yellow_cards,
            'totalPoints': total_points,
            'bestRank': best_rank,
            'records': []
        }
        
        # 添加每条记录的详细信息
        for record in team_records:
            record_dict = record.to_dict()
            record_dict['teamName'] = record_dict['name']
            
            # 根据赛事名称确定matchType
            record_dict['matchType'] = determine_match_type(record.tournament)
            
            # 获取该记录对应的球员信息（从PlayerTeamHistory中获取）
            team_players = []
            player_histories = PlayerTeamHistory.query.filter_by(
                team_id=record.id, 
                tournament_id=record.tournament_id
            ).all()
            
            for history in player_histories:
                team_players.append({
                    'name': history.player.name,
                    'playerId': history.player_id,
                    'studentId': history.player_id,
                    'id': history.player_id,
                    'number': str(history.player_number),
                    'goals': history.tournament_goals,
                    'redCards': history.tournament_red_cards,
                    'yellowCards': history.tournament_yellow_cards
                })
            
            record_dict['players'] = team_players
            
            # 添加详细统计信息
            record_dict.update({
                'rank': record.tournament_rank,
                'goals': record.tournament_goals,
                'goalsConceded': record.tournament_goals_conceded,
                'goalDifference': record.tournament_goal_difference,
                'redCards': record.tournament_red_cards,
                'yellowCards': record.tournament_yellow_cards,
                'points': record.tournament_points,
                'tournamentId': record.tournament_id,
                'tournamentName': record.tournament.name if record.tournament else None
            })
            
            team_info['records'].append(record_dict)
        
        return jsonify({'status': 'success', 'data': team_info}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

@teams_bp.route('', methods=['GET'])
def get_teams():
    """获取所有球队信息（公共接口）"""
    try:
        # 检查是否需要按球队名称分组
        group_by_name = request.args.get('group_by_name', 'false').lower() == 'true'
        
        if group_by_name:
            # 按球队名称分组返回统计信息
            teams = Team.query.all()
            teams_grouped = {}
            
            for team in teams:
                team_name = team.name
                if team_name not in teams_grouped:
                    teams_grouped[team_name] = {
                        'teamName': team_name,
                        'totalGoals': 0,
                        'totalGoalsConceded': 0,
                        'totalGoalDifference': 0,
                        'totalRedCards': 0,
                        'totalYellowCards': 0,
                        'totalPoints': 0,
                        'bestRank': None,
                        'tournaments': []
                    }
                
                # 累加统计数据
                teams_grouped[team_name]['totalGoals'] += team.tournament_goals
                teams_grouped[team_name]['totalGoalsConceded'] += team.tournament_goals_conceded
                teams_grouped[team_name]['totalGoalDifference'] += team.tournament_goal_difference
                teams_grouped[team_name]['totalRedCards'] += team.tournament_red_cards
                teams_grouped[team_name]['totalYellowCards'] += team.tournament_yellow_cards
                teams_grouped[team_name]['totalPoints'] += team.tournament_points
                
                # 更新最好排名
                if team.tournament_rank and team.tournament_rank > 0:
                    current_best = teams_grouped[team_name]['bestRank']
                    if current_best is None or team.tournament_rank < current_best:
                        teams_grouped[team_name]['bestRank'] = team.tournament_rank
                
                # 添加赛事信息
                teams_grouped[team_name]['tournaments'].append({
                    'tournament_id': team.tournament_id,
                    'matchType': determine_match_type(team.tournament),
                    'tournament_name': team.tournament.name if team.tournament else None
                })
            
            return jsonify({'status': 'success', 'data': list(teams_grouped.values())}), 200
        else:
            # 原有逻辑：返回所有球队记录
            teams = Team.query.all()
            teams_data = []
            
            for team in teams:
                team_dict = team.to_dict()
                team_dict['teamName'] = team_dict['name']
                
                # 获取球队在当前赛事中的球员信息（从PlayerTeamHistory中获取）
                team_players = []
                player_histories = PlayerTeamHistory.query.filter_by(
                    team_id=team.id, 
                    tournament_id=team.tournament_id
                ).all()
                
                for history in player_histories:
                    team_players.append({
                        'name': history.player.name,
                        'playerId': history.player_id,
                        'studentId': history.player_id,
                        'id': history.player_id,
                        'number': str(history.player_number),
                        'goals': history.tournament_goals,
                        'redCards': history.tournament_red_cards,
                        'yellowCards': history.tournament_yellow_cards
                    })
                
                team_dict['players'] = team_players
                
                # 根据赛事名称确定matchType
                team_dict['matchType'] = determine_match_type(team.tournament)
                
                # 添加详细统计信息
                team_dict.update({
                    'rank': team.tournament_rank,
                    'goals': team.tournament_goals,
                    'goalsConceded': team.tournament_goals_conceded,
                    'goalDifference': team.tournament_goal_difference,
                    'redCards': team.tournament_red_cards,
                    'yellowCards': team.tournament_yellow_cards,
                    'points': team.tournament_points,
                    'tournamentId': team.tournament_id,
                    'tournamentName': team.tournament.name if team.tournament else None
                })
                
                teams_data.append(team_dict)
            
            return jsonify({'status': 'success', 'data': teams_data}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

@teams_bp.route('', methods=['POST'])
@jwt_required()
def create_team():
    """创建球队和球员信息"""
    data = request.get_json()
    
    if not data or not data.get('teamName'):
        return jsonify({'status': 'error', 'message': '球队名称不能为空'}), 400
    
    # 根据matchType确定赛事ID
    match_type_to_tournament = {
        'champions-cup': 1,  # 冠军杯
        'womens-cup': 2,     # 巾帼杯
        'eight-a-side': 3    # 八人制比赛
    }
    tournament_id = match_type_to_tournament.get(data.get('matchType', 'champions-cup'), 1)
    
    # 检查在同一赛事中球队名称是否已存在
    existing_team = Team.query.filter_by(name=data['teamName'], tournament_id=tournament_id).first()
    if existing_team:
        return jsonify({'status': 'error', 'message': '该赛事中球队名称已存在'}), 400
    
    try:
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
        
        # 获取球员信息（保持与其他接口一致的格式）
        team_players = []
        for history in PlayerTeamHistory.query.filter_by(team_id=new_team.id, tournament_id=tournament_id).all():
            team_players.append({
                'name': history.player.name,
                'playerId': history.player_id,
                'studentId': history.player_id,
                'id': history.player_id,
                'number': str(history.player_number),
                'goals': history.tournament_goals,
                'redCards': history.tournament_red_cards,
                'yellowCards': history.tournament_yellow_cards
            })
        
        team_dict['players'] = team_players
        team_dict['matchType'] = determine_match_type(new_team.tournament)
        
        # 添加详细统计信息
        team_dict.update({
            'rank': new_team.tournament_rank,
            'goals': new_team.tournament_goals,
            'goalsConceded': new_team.tournament_goals_conceded,
            'goalDifference': new_team.tournament_goal_difference,
            'redCards': new_team.tournament_red_cards,
            'yellowCards': new_team.tournament_yellow_cards,
            'points': new_team.tournament_points,
            'tournamentId': new_team.tournament_id,
            'tournamentName': new_team.tournament.name if new_team.tournament else None
        })
        
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
        
        # 保存原有的tournament_id
        old_tournament_id = team.tournament_id
        
        # 更新球队信息
        if data.get('teamName'):
            team.name = data['teamName']
        
        # 如果修改了比赛类型，需要更新tournament_id
        if data.get('matchType'):
            match_type_to_tournament = {
                'champions-cup': 1,
                'womens-cup': 2,
                'eight-a-side': 3
            }
            new_tournament_id = match_type_to_tournament.get(data['matchType'], 1)
            
            # 检查新赛事中是否已有同名球队
            if new_tournament_id != old_tournament_id:
                existing_team = Team.query.filter_by(
                    name=team.name, 
                    tournament_id=new_tournament_id
                ).filter(Team.id != team_id).first()
                
                if existing_team:
                    return jsonify({'status': 'error', 'message': '目标赛事中已存在同名球队'}), 400
                
                team.tournament_id = new_tournament_id
        
        # 删除原有的球员-队伍历史记录（使用原tournament_id或新tournament_id）
        PlayerTeamHistory.query.filter_by(team_id=team_id, tournament_id=old_tournament_id).delete()
        if team.tournament_id != old_tournament_id:
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
        
        # 返回更新后的球队信息
        team_dict = team.to_dict()
        team_dict['teamName'] = team_dict['name']
        
        # 获取更新后的球员信息
        team_players = []
        for history in PlayerTeamHistory.query.filter_by(team_id=team_id, tournament_id=team.tournament_id).all():
            team_players.append({
                'name': history.player.name,
                'playerId': history.player_id,
                'studentId': history.player_id,
                'id': history.player_id,
                'number': str(history.player_number),
                'goals': history.tournament_goals,
                'redCards': history.tournament_red_cards,
                'yellowCards': history.tournament_yellow_cards
            })
        
        team_dict['players'] = team_players
        team_dict['matchType'] = determine_match_type(team.tournament)
        
        # 添加详细统计信息
        team_dict.update({
            'rank': team.tournament_rank,
            'goals': team.tournament_goals,
            'goalsConceded': team.tournament_goals_conceded,
            'goalDifference': team.tournament_goal_difference,
            'redCards': team.tournament_red_cards,
            'yellowCards': team.tournament_yellow_cards,
            'points': team.tournament_points,
            'tournamentId': team.tournament_id,
            'tournamentName': team.tournament.name if team.tournament else None
        })
        
        return jsonify({
            'status': 'success', 
            'message': '更新成功',
            'data': team_dict
        }), 200
        
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

        db.session.delete(team)
        db.session.commit()
        return jsonify({'status': 'success', 'message': '删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500
