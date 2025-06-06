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
        
        team_name = team.name  # 保存球队名称用于日志
        print(f"开始删除球队: {team_name} (ID: {team_id})")
        
        # 使用事务来确保数据一致性
        try:
            # 1. 删除所有相关的事件记录
            try:
                from app.models.event import Event
                events_to_delete = Event.query.filter_by(team_id=team_id).all()
                for event in events_to_delete:
                    db.session.delete(event)
                print(f"准备删除 {len(events_to_delete)} 条事件记录")
            except ImportError:
                print("Event模型不存在，跳过事件记录删除")
            except Exception as event_error:
                print(f"删除事件记录时出错: {str(event_error)}")
            
            # 2. 删除所有相关的比赛记录
            try:
                from app.models.match import Match
                # 先查找所有相关比赛
                home_matches = Match.query.filter_by(home_team_id=team_id).all()
                away_matches = Match.query.filter_by(away_team_id=team_id).all()
                
                # 逐个删除比赛记录
                for match in home_matches + away_matches:
                    db.session.delete(match)
                
                print(f"准备删除 {len(home_matches)} 场主场比赛和 {len(away_matches)} 场客场比赛")
                
            except ImportError:
                print("Match模型不存在，跳过比赛记录删除")
            except Exception as match_error:
                print(f"删除比赛记录时出错: {str(match_error)}")
                # 如果ORM删除失败，尝试使用原生SQL
                try:
                    print("尝试使用原生SQL删除比赛记录...")
                    db.session.execute(
                        "DELETE FROM `match` WHERE `主队ID` = :team_id OR `客队ID` = :team_id",
                        {"team_id": team_id}
                    )
                    print("使用原生SQL删除比赛记录成功")
                except Exception as sql_error:
                    print(f"原生SQL删除也失败: {str(sql_error)}")
                    raise sql_error
            
            # 3. 删除球员-队伍历史记录
            try:
                histories_to_delete = PlayerTeamHistory.query.filter_by(team_id=team_id).all()
                for history in histories_to_delete:
                    db.session.delete(history)
                print(f"准备删除 {len(histories_to_delete)} 条球员历史记录")
            except Exception as history_error:
                print(f"删除球员历史记录时出错: {str(history_error)}")
                raise history_error
            
            # 4. 删除球队本身
            db.session.delete(team)
            print(f"准备删除球队: {team_name}")
            
            # 5. 提交所有删除操作
            db.session.commit()
            print(f"成功删除球队: {team_name} (ID: {team_id})")
            
            return jsonify({
                'status': 'success', 
                'message': f'球队 {team_name} 删除成功'
            }), 200
            
        except Exception as delete_error:
            print(f"删除过程中发生错误: {str(delete_error)}")
            db.session.rollback()
            
            # 提供更详细的错误信息
            error_message = str(delete_error)
            if "foreign key constraint" in error_message.lower():
                return jsonify({
                    'status': 'error', 
                    'message': '删除失败：该球队存在关联数据，请先删除相关比赛或事件记录'
                }), 500
            elif "cannot be null" in error_message.lower():
                return jsonify({
                    'status': 'error', 
                    'message': '删除失败：数据库约束错误，请联系管理员'
                }), 500
            else:
                return jsonify({
                    'status': 'error', 
                    'message': f'删除失败: {error_message}'
                }), 500
        
    except Exception as e:
        db.session.rollback()
        print(f"删除球队时发生未预期的错误: {str(e)}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")
        return jsonify({
            'status': 'error', 
            'message': f'删除失败: {str(e)}'
        }), 500
