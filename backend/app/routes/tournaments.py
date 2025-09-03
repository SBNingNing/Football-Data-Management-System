from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.tournament import Tournament
from app.models.competition import Competition
from app.models.season import Season
from app.models.team import Team
from app.models.player_team_history import PlayerTeamHistory
from datetime import datetime
import urllib.parse
import os
from sqlalchemy import text

tournaments_bp = Blueprint('tournaments', __name__)

@tournaments_bp.route('/<tournament_name>', methods=['GET'])
def get_tournament(tournament_name):
    """根据赛事名称获取赛事信息和统计数据"""
    print(f"[DEBUG] get_tournament called with tournament_name: {tournament_name}")
    try:
        # URL解码处理中文名称
        decoded_tournament_name = urllib.parse.unquote(tournament_name, encoding='utf-8').strip()
        print(f"前端传入赛事名称: '{tournament_name}', 解码后: '{decoded_tournament_name}'")

        # 检查数据库连接
        try:
            db.session.execute(text('SELECT 1'))
            print("[DEBUG] 数据库连接正常")
        except Exception as db_error:
            print(f"[ERROR] 数据库连接失败: {db_error}")
            return jsonify({'status': 'error', 'message': '数据库连接失败'}), 500

        # 获取所有赛事用于调试
        try:
            all_tournaments = Tournament.query.all()
            all_names = [t.name for t in all_tournaments]
            print(f"数据库中所有赛事名称: {all_names}")
            print(f"数据库中赛事总数: {len(all_tournaments)}")
        except Exception as query_error:
            print(f"[ERROR] 查询所有赛事失败: {query_error}")
            return jsonify({'status': 'error', 'message': '查询数据库失败'}), 500

        # 直接用SQL精确匹配
        tournament_records = Tournament.query.filter(
            Tournament.name == decoded_tournament_name
        ).all()
        print(f"[DEBUG] 精确匹配找到记录数: {len(tournament_records)}")

        # 如果精确匹配失败，尝试模糊匹配
        if not tournament_records:
            print(f"[DEBUG] 精确匹配失败，尝试模糊匹配")
            tournament_records = Tournament.query.filter(
                Tournament.name.like(f"%{decoded_tournament_name}%")
            ).all()
            print(f"[DEBUG] 模糊匹配找到记录数: {len(tournament_records)}")

        # 如果还是没找到，尝试其他匹配方式
        if not tournament_records:
            # 尝试忽略大小写匹配
            tournament_records = Tournament.query.filter(
                Tournament.name.ilike(f"%{decoded_tournament_name}%")
            ).all()
            print(f"[DEBUG] 忽略大小写匹配找到记录数: {len(tournament_records)}")

        if not tournament_records:
            return jsonify({
                'status': 'error', 
                'message': f'赛事"{decoded_tournament_name}"不存在',
                'available_tournaments': all_names,
                'debug_info': {
                    'original_name': tournament_name,
                    'decoded_name': decoded_tournament_name,
                    'total_tournaments': len(all_names)
                }
            }), 404
        
        tournament_info = {
            'tournamentName': decoded_tournament_name,
            'totalSeasons': len(tournament_records),
            'records': []
        }
        
        for record in tournament_records:
            try:
                print(f"[DEBUG] 处理赛事记录 ID: {record.id}, 名称: {record.name}")
                
                # 获取该赛事下的所有球队信息
                tournament_teams = Team.query.filter(Team.tournament_id == record.id).all()
                print(f"[DEBUG] 找到球队数: {len(tournament_teams)}")
                teams_data = []
                
                for team in tournament_teams:
                    # 获取该球队在该赛事中的所有球员
                    team_players = PlayerTeamHistory.query.filter(
                        PlayerTeamHistory.team_id == team.id,
                        PlayerTeamHistory.tournament_id == record.id
                    ).all()
                    
                    players_data = []
                    for player_history in team_players:
                        try:
                            player_dict = {
                                'player_id': player_history.player_id,
                                'player_name': player_history.player.name if hasattr(player_history, 'player') and player_history.player else f'球员{player_history.player_id}',
                                'player_number': player_history.player_number,
                                'goals': player_history.tournament_goals or 0,
                                'redCards': player_history.tournament_red_cards or 0,
                                'yellowCards': player_history.tournament_yellow_cards or 0,
                                'remarks': player_history.remarks or ''
                            }
                            players_data.append(player_dict)
                        except Exception as player_error:
                            print(f"[ERROR] 处理球员数据失败: {player_error}")
                            continue
                    
                    team_dict = {
                        'id': team.id,
                        'name': team.name or '',
                        'goals': team.tournament_goals or 0,
                        'goalsConceded': team.tournament_goals_conceded or 0,
                        'goalDifference': team.tournament_goal_difference or 0,
                        'points': team.tournament_points or 0,
                        'rank': team.tournament_rank or 0,
                        'redCards': team.tournament_red_cards or 0,
                        'yellowCards': team.tournament_yellow_cards or 0,
                        'groupId': team.group_id,
                        'players': players_data,
                        'playerCount': len(players_data)
                    }
                    teams_data.append(team_dict)
                
                # 计算赛事统计数据
                total_goals = sum(team.tournament_goals or 0 for team in tournament_teams)
                print(f"[DEBUG] 计算得出总进球数: {total_goals}")
                
                # 安全处理时间字段
                season_start_time = None
                season_end_time = None
                if record.season_start_time:
                    try:
                        season_start_time = record.season_start_time.isoformat()
                    except:
                        season_start_time = str(record.season_start_time)
                
                if record.season_end_time:
                    try:
                        season_end_time = record.season_end_time.isoformat()
                    except:
                        season_end_time = str(record.season_end_time)
                
                record_dict = {
                    'id': record.id,
                    'name': record.name,
                    'tournamentName': record.name,
                    'teams': teams_data,
                    'teamCount': len(teams_data),
                    'totalGoals': total_goals,
                    'totalTeams': len(teams_data),
                    'seasonStartTime': season_start_time,
                    'seasonEndTime': season_end_time,
                    'isGrouped': record.is_grouped or False,
                    'seasonName': record.season_name or record.name
                }
                
                tournament_info['records'].append(record_dict)
                
            except Exception as record_error:
                print(f"[ERROR] 处理赛事记录失败: {record_error}")
                continue
        
        print(f"[DEBUG] 最终返回的赛事信息包含 {len(tournament_info['records'])} 条记录")
        return jsonify({'status': 'success', 'data': tournament_info}), 200
        
    except Exception as e:
        print(f"[ERROR] 获取赛事信息失败: {str(e)}")
        import traceback
        print(f"[ERROR] 详细错误信息: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

@tournaments_bp.route('', methods=['GET'])
def get_tournaments():
    """获取所有赛事信息（公共接口）"""
    try:
        group_by_name = request.args.get('group_by_name', 'false').lower() == 'true'
        
        if group_by_name:
            tournaments = Tournament.query.all()
            
            if not tournaments:
                return jsonify({'status': 'success', 'data': []}), 200
            
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
                tournament_teams = Team.query.filter(Team.tournament_id == tournament.id).all()
                total_goals = sum(team.tournament_goals or 0 for team in tournament_teams)
                
                tournaments_grouped[tournament_name]['totalSeasons'] += 1
                tournaments_grouped[tournament_name]['totalTeams'] += len(tournament_teams)
                tournaments_grouped[tournament_name]['totalGoals'] += total_goals
                
                season_info = {
                    'tournament_id': tournament.id,
                    'season_name': tournament.season_name or '',
                    'is_grouped': tournament.is_grouped or False,
                    'team_count': len(tournament_teams),
                    'total_goals': total_goals
                }
                
                # 安全处理时间字段
                try:
                    if tournament.season_start_time:
                        season_info['season_start_time'] = tournament.season_start_time.isoformat()
                    else:
                        season_info['season_start_time'] = None
                        
                    if tournament.season_end_time:
                        season_info['season_end_time'] = tournament.season_end_time.isoformat()
                    else:
                        season_info['season_end_time'] = None
                except Exception as time_error:
                    season_info['season_start_time'] = None
                    season_info['season_end_time'] = None
                
                tournaments_grouped[tournament_name]['seasons'].append(season_info)
            
            result_data = list(tournaments_grouped.values())
            return jsonify({'status': 'success', 'data': result_data}), 200
        else:
            # 原有逻辑：返回所有赛事记录
            tournaments = Tournament.query.all()
            
            if not tournaments:
                return jsonify({'status': 'success', 'data': []}), 200
            
            tournaments_data = []
            
            for tournament in tournaments:
                try:
                    tournament_teams = Team.query.filter(Team.tournament_id == tournament.id).all()
                    teams_data = []
                    
                    for team in tournament_teams:
                        team_players = PlayerTeamHistory.query.filter(
                            PlayerTeamHistory.team_id == team.id,
                            PlayerTeamHistory.tournament_id == tournament.id
                        ).all()
                        
                        players_data = []
                        for player_history in team_players:
                            player_dict = {
                                'player_id': player_history.player_id,
                                'player_name': player_history.player.name if hasattr(player_history, 'player') and player_history.player else f'球员{player_history.player_id}',
                                'player_number': player_history.player_number,
                                'goals': player_history.tournament_goals or 0,
                                'redCards': player_history.tournament_red_cards or 0,
                                'yellowCards': player_history.tournament_yellow_cards or 0,
                                'remarks': player_history.remarks or ''
                            }
                            players_data.append(player_dict)
                        
                        teams_data.append({
                            'id': team.id,
                            'name': team.name or '',
                            'goals': team.tournament_goals or 0,
                            'goalsConceded': team.tournament_goals_conceded or 0,
                            'goalDifference': team.tournament_goal_difference or 0,
                            'points': team.tournament_points or 0,
                            'rank': team.tournament_rank or 0,
                            'redCards': team.tournament_red_cards or 0,
                            'yellowCards': team.tournament_yellow_cards or 0,
                            'groupId': team.group_id,
                            'players': players_data,
                            'playerCount': len(players_data)
                        })

                    total_goals = sum(team.tournament_goals or 0 for team in tournament_teams)
                    
                    tournament_dict = {
                        'id': tournament.id,
                        'name': tournament.name,
                        'tournamentName': tournament.name,
                        'teams': teams_data,
                        'teamCount': len(teams_data),
                        'totalGoals': total_goals,
                        'seasonStartTime': tournament.season_start_time.isoformat() if tournament.season_start_time else None,
                        'seasonEndTime': tournament.season_end_time.isoformat() if tournament.season_end_time else None,
                        'isGrouped': tournament.is_grouped or False,
                        'seasonName': tournament.season_name or ''
                    }
                    
                    tournaments_data.append(tournament_dict)
                    
                except Exception as tournament_error:
                    print(f"[ERROR] 处理赛事数据失败: {tournament_error}")
                    continue
            
            return jsonify({'status': 'success', 'data': tournaments_data}), 200
        
    except Exception as e:
        print(f"[ERROR] 获取赛事列表失败: {str(e)}")
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
        print(f"[ERROR] 创建赛事失败: {str(e)}")
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
        print(f"[ERROR] 更新赛事失败: {str(e)}")
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
        print(f"[ERROR] 删除赛事失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500

# 添加一个测试路由来确认蓝图工作正常
@tournaments_bp.route('/test', methods=['GET'])
def test_route():
    """测试路由是否工作"""
    return jsonify({'status': 'success', 'message': '赛事路由工作正常'}), 200

@tournaments_bp.route('/instances', methods=['POST'])
@jwt_required()
def create_tournament_instance():
    """创建新的赛事-赛季实例"""
    try:
        data = request.get_json()
        
        required_fields = ['competition_id', 'season_id']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'status': 'error', 'message': f'{field}不能为空'}), 400
        
        # 验证competition和season是否存在
        competition = Competition.query.get(data['competition_id'])
        if not competition:
            return jsonify({'status': 'error', 'message': '赛事不存在'}), 404
        
        season = Season.query.get(data['season_id'])
        if not season:
            return jsonify({'status': 'error', 'message': '赛季不存在'}), 404
        
        # 检查是否已经存在相同的组合
        existing_tournament = Tournament.query.filter_by(
            competition_id=data['competition_id'],
            season_id=data['season_id']
        ).first()
        
        if existing_tournament:
            return jsonify({
                'status': 'error', 
                'message': '该赛事和赛季的组合已存在'
            }), 400
        
        tournament = Tournament(
            competition_id=data['competition_id'],
            season_id=data['season_id'],
            is_grouped=data.get('is_grouped', False),
            group_count=data.get('group_count'),
            playoff_spots=data.get('playoff_spots')
        )
        
        db.session.add(tournament)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '赛事实例创建成功',
            'data': tournament.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] 创建赛事实例失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500

@tournaments_bp.route('/instances/<int:tournament_id>', methods=['PUT'])
@jwt_required()
def update_tournament_instance(tournament_id):
    """更新赛事实例"""
    try:
        tournament = Tournament.query.get_or_404(tournament_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': '请提供要更新的数据'}), 400
        
        if 'competition_id' in data:
            competition = Competition.query.get(data['competition_id'])
            if not competition:
                return jsonify({'status': 'error', 'message': '赛事不存在'}), 404
            tournament.competition_id = data['competition_id']
        
        if 'season_id' in data:
            season = Season.query.get(data['season_id'])
            if not season:
                return jsonify({'status': 'error', 'message': '赛季不存在'}), 404
            tournament.season_id = data['season_id']
        
        if 'is_grouped' in data:
            tournament.is_grouped = data['is_grouped']
        
        if 'group_count' in data:
            tournament.group_count = data['group_count']
        
        if 'playoff_spots' in data:
            tournament.playoff_spots = data['playoff_spots']
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '赛事实例更新成功',
            'data': tournament.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] 更新赛事实例失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500
