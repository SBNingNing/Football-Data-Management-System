from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.tournament import Tournament
from app.models.team import Team
from app.models.player_team_history import PlayerTeamHistory
from datetime import datetime

tournaments_bp = Blueprint('tournaments', __name__)

@tournaments_bp.route('/<tournament_name>', methods=['GET'])
def get_tournament(tournament_name):
    """根据赛事名称获取赛事信息和统计数据"""
    try:
        # 查询该赛事名称的所有记录
        tournament_records = Tournament.query.filter_by(name=tournament_name).all()
        if not tournament_records:
            return jsonify({'status': 'error', 'message': '赛事不存在'}), 404
        
        # 如果有多个同名赛事（不同赛季），返回所有记录
        tournament_info = {
            'tournamentName': tournament_name,
            'totalSeasons': len(tournament_records),
            'records': []
        }
        
        # 添加每条记录的详细信息
        for record in tournament_records:
            record_dict = record.to_dict()
            record_dict['tournamentName'] = record_dict['name']
            
            # 获取该赛事下的所有球队信息
            tournament_teams = Team.query.filter_by(tournament_id=record.id).all()
            teams_data = []
            
            for team in tournament_teams:
                # 获取该球队在该赛事中的所有球员
                team_players = PlayerTeamHistory.query.filter_by(
                    team_id=team.id, 
                    tournament_id=record.id
                ).all()
                
                players_data = []
                for player_history in team_players:
                    player_dict = {
                        'player_id': player_history.player_id,
                        'player_name': player_history.player.name if player_history.player else None,
                        'player_number': player_history.player_number,
                        'goals': player_history.tournament_goals or 0,
                        'redCards': player_history.tournament_red_cards or 0,
                        'yellowCards': player_history.tournament_yellow_cards or 0,
                        'remarks': player_history.remarks or ''
                    }
                    players_data.append(player_dict)
                
                team_dict = {
                    'id': team.id,
                    'name': team.name,
                    'goals': team.tournament_goals,
                    'goalsConceded': team.tournament_goals_conceded,
                    'goalDifference': team.tournament_goal_difference,
                    'points': team.tournament_points,
                    'rank': team.tournament_rank,
                    'redCards': team.tournament_red_cards,
                    'yellowCards': team.tournament_yellow_cards,
                    'groupId': team.group_id,
                    'players': players_data,
                    'playerCount': len(players_data)
                }
                teams_data.append(team_dict)
            
            record_dict['teams'] = teams_data
            record_dict['teamCount'] = len(teams_data)
            
            # 计算赛事统计数据
            total_goals = sum(team.tournament_goals or 0 for team in tournament_teams)
            total_teams = len(teams_data)
            
            record_dict.update({
                'totalGoals': total_goals,
                'totalTeams': total_teams,
                'seasonStartTime': record_dict['season_start_time'],
                'seasonEndTime': record_dict['season_end_time'],
                'isGrouped': record_dict['is_grouped'],
                'seasonName': record_dict['season_name']
            })
            
            tournament_info['records'].append(record_dict)
        
        return jsonify({'status': 'success', 'data': tournament_info}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

@tournaments_bp.route('', methods=['GET'])
def get_tournaments():
    """获取所有赛事信息（公共接口）"""
    try:
        # 检查是否需要按赛事名称分组
        group_by_name = request.args.get('group_by_name', 'false').lower() == 'true'
        
        if group_by_name:
            # 按赛事名称分组返回统计信息
            tournaments = Tournament.query.all()
            tournaments_grouped = {}
            
            for tournament in tournaments:
                tournament_name = tournament.name
                if tournament_name not in tournaments_grouped:
                    tournaments_grouped[tournament_name] = {
                        'tournamentName': tournament_name,
                        'totalSeasons': 0,
                        'totalTeams': 0,
                        'totalGoals': 0,
                        'seasons': []
                    }
                
                # 获取该赛事下的球队信息
                tournament_teams = Team.query.filter_by(tournament_id=tournament.id).all()
                total_goals = sum(team.tournament_goals or 0 for team in tournament_teams)
                
                # 累加统计数据
                tournaments_grouped[tournament_name]['totalSeasons'] += 1
                tournaments_grouped[tournament_name]['totalTeams'] += len(tournament_teams)
                tournaments_grouped[tournament_name]['totalGoals'] += total_goals
                
                # 添加赛季信息
                tournaments_grouped[tournament_name]['seasons'].append({
                    'tournament_id': tournament.id,
                    'season_name': tournament.season_name,
                    'is_grouped': tournament.is_grouped,
                    'team_count': len(tournament_teams),
                    'total_goals': total_goals,
                    'season_start_time': tournament.season_start_time.isoformat() if tournament.season_start_time else None,
                    'season_end_time': tournament.season_end_time.isoformat() if tournament.season_end_time else None
                })
            
            return jsonify({'status': 'success', 'data': list(tournaments_grouped.values())}), 200
        else:
            # 原有逻辑：返回所有赛事记录
            tournaments = Tournament.query.all()
            tournaments_data = []
            
            for tournament in tournaments:
                tournament_dict = tournament.to_dict()
                tournament_dict['tournamentName'] = tournament_dict['name']
                
                # 获取该赛事下的球队信息
                tournament_teams = Team.query.filter_by(tournament_id=tournament.id).all()
                teams_data = []
                
                for team in tournament_teams:
                    # 获取该球队在该赛事中的所有球员
                    team_players = PlayerTeamHistory.query.filter_by(
                        team_id=team.id, 
                        tournament_id=tournament.id
                    ).all()
                    
                    players_data = []
                    for player_history in team_players:
                        player_dict = {
                            'player_id': player_history.player_id,
                            'player_name': player_history.player.name if player_history.player else None,
                            'player_number': player_history.player_number,
                            'goals': player_history.tournament_goals or 0,
                            'redCards': player_history.tournament_red_cards or 0,
                            'yellowCards': player_history.tournament_yellow_cards or 0,
                            'remarks': player_history.remarks or ''
                        }
                        players_data.append(player_dict)
                    
                    teams_data.append({
                        'id': team.id,
                        'name': team.name,
                        'goals': team.tournament_goals,
                        'goalsConceded': team.tournament_goals_conceded,
                        'goalDifference': team.tournament_goal_difference,
                        'points': team.tournament_points,
                        'rank': team.tournament_rank,
                        'redCards': team.tournament_red_cards,
                        'yellowCards': team.tournament_yellow_cards,
                        'groupId': team.group_id,
                        'players': players_data,
                        'playerCount': len(players_data)
                    })

                tournament_dict['teams'] = teams_data
                tournament_dict['teamCount'] = len(teams_data)
                
                # 计算赛事统计数据
                total_goals = sum(team.tournament_goals or 0 for team in tournament_teams)
                tournament_dict['totalGoals'] = total_goals
                
                # 添加详细信息
                tournament_dict.update({
                    'seasonStartTime': tournament_dict['season_start_time'],
                    'seasonEndTime': tournament_dict['season_end_time'],
                    'isGrouped': tournament_dict['is_grouped'],
                    'seasonName': tournament_dict['season_name']
                })
                
                tournaments_data.append(tournament_dict)
            
            return jsonify({'status': 'success', 'data': tournaments_data}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

@tournaments_bp.route('', methods=['POST'])
@jwt_required()
def create_tournament():
    """创建赛事"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'status': 'error', 'message': '赛事名称不能为空'}), 400
    
    if not data.get('season_name'):
        return jsonify({'status': 'error', 'message': '赛季名称不能为空'}), 400
    
    try:
        # 解析时间
        season_start_time = datetime.fromisoformat(data['season_start_time'].replace('Z', '+00:00')) if data.get('season_start_time') else datetime.now()
        season_end_time = datetime.fromisoformat(data['season_end_time'].replace('Z', '+00:00')) if data.get('season_end_time') else datetime.now()
        
        # 创建赛事
        new_tournament = Tournament(
            name=data['name'],
            season_name=data['season_name'],
            is_grouped=data.get('is_grouped', False),
            season_start_time=season_start_time,
            season_end_time=season_end_time
        )
        db.session.add(new_tournament)
        db.session.commit()
        
        # 返回创建成功的赛事信息
        tournament_dict = new_tournament.to_dict()
        tournament_dict['tournamentName'] = tournament_dict['name']
        tournament_dict.update({
            'teams': [],
            'teamCount': 0,
            'totalGoals': 0,
            'seasonStartTime': tournament_dict['season_start_time'],
            'seasonEndTime': tournament_dict['season_end_time'],
            'isGrouped': tournament_dict['is_grouped'],
            'seasonName': tournament_dict['season_name']
        })
        
        return jsonify({
            'status': 'success', 
            'message': '赛事创建成功',
            'data': tournament_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500

@tournaments_bp.route('/<int:tournament_id>', methods=['PUT'])
@jwt_required()
def update_tournament(tournament_id):
    """更新赛事信息"""
    data = request.get_json()
    
    try:
        tournament = Tournament.query.get(tournament_id)
        if not tournament:
            return jsonify({'status': 'error', 'message': '赛事不存在'}), 404
        
        # 更新赛事信息
        if data.get('name'):
            tournament.name = data['name']
        if data.get('season_name'):
            tournament.season_name = data['season_name']
        if 'is_grouped' in data:
            tournament.is_grouped = data['is_grouped']
        if data.get('season_start_time'):
            tournament.season_start_time = datetime.fromisoformat(data['season_start_time'].replace('Z', '+00:00'))
        if data.get('season_end_time'):
            tournament.season_end_time = datetime.fromisoformat(data['season_end_time'].replace('Z', '+00:00'))
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': '更新成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500

@tournaments_bp.route('/<int:tournament_id>', methods=['DELETE'])
@jwt_required()
def delete_tournament(tournament_id):
    """删除赛事"""
    try:
        tournament = Tournament.query.get(tournament_id)
        if not tournament:
            return jsonify({'status': 'error', 'message': '赛事不存在'}), 404
        
        # 检查是否有关联的球队
        associated_teams = Team.query.filter_by(tournament_id=tournament_id).count()
        if associated_teams > 0:
            return jsonify({'status': 'error', 'message': f'无法删除，该赛事下还有 {associated_teams} 支球队'}), 400
        
        # 删除赛事
        db.session.delete(tournament)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': '删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500
