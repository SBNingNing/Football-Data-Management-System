from flask import Blueprint, jsonify
from app.models.match import Match
from app.models.team import Team
from app.models.tournament import Tournament
from app.models.event import Event
from app.models.player_team_history import PlayerTeamHistory
from app.models.player import Player
from app import db
from sqlalchemy import func, and_, case, or_

stats_bp = Blueprint('stats', __name__, url_prefix='/api')

@stats_bp.route('/test', methods=['GET'])
def test_stats():
    """测试stats路由是否正常工作"""
    return jsonify({
        'status': 'success',
        'message': 'Stats route is working!'
    })

@stats_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取比赛统计数据"""
    print("Stats route called")  # 添加调试信息
    try:
        # 修复case函数的参数格式
        stats_query = db.session.query(
            func.count(Match.id).label('total'),
            func.sum(case((Match.status == 'F', 1), else_=0)).label('completed'),
            func.sum(case((Match.status.in_(['S', 'P']), 1), else_=0)).label('upcoming')
        ).first()
        
        # 检查查询结果是否为空
        if not stats_query:
            total_matches = completed_matches = upcoming_matches = 0
        else:
            total_matches = int(stats_query.total or 0)
            completed_matches = int(stats_query.completed or 0)
            upcoming_matches = int(stats_query.upcoming or 0)
        
        # 数据验证：确保数据逻辑正确
        if total_matches < completed_matches + upcoming_matches:
            # 如果有其他状态的比赛，重新计算即将进行的比赛数
            upcoming_matches = total_matches - completed_matches
        
        stats_data = {
            'totalMatches': total_matches,
            'completedMatches': completed_matches,
            'upcomingMatches': max(0, upcoming_matches)  # 确保不为负数
        }
        
        print(f"Stats data: {stats_data}")  # 调试信息
        
        return jsonify({
            'status': 'success',
            'data': stats_data
        })
        
    except Exception as e:
        # 记录详细错误信息用于调试
        print(f"Stats error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        # 如果复杂查询失败，使用简单查询作为后备
        try:
            total_matches = Match.query.count()
            completed_matches = Match.query.filter_by(status='F').count()
            upcoming_matches = max(0, total_matches - completed_matches)
            
            stats_data = {
                'totalMatches': total_matches,
                'completedMatches': completed_matches,
                'upcomingMatches': upcoming_matches
            }
            
            print(f"Fallback stats data: {stats_data}")  # 调试信息
            
            return jsonify({
                'status': 'success',
                'data': stats_data
            })
        except Exception as fallback_error:
            print(f"Fallback query error: {str(fallback_error)}")
            return jsonify({
                'status': 'error',
                'message': f'获取统计数据失败: {str(e)}'
            }), 500

@stats_bp.route('/rankings', methods=['GET'])
def get_rankings():
    """获取排行榜数据"""
    try:
        # 获取所有赛事
        tournaments = Tournament.query.all()
        rankings = {}
        
        for tournament in tournaments:
            tournament_key = get_tournament_key(tournament.name)
            
            # 射手榜 - 个人（从player_team_history表获取）
            player_goals = db.session.query(
                PlayerTeamHistory.player_id,
                Player.name.label('player_name'),
                Team.name.label('team_name'),
                PlayerTeamHistory.tournament_goals.label('goals')
            ).join(
                Player, PlayerTeamHistory.player_id == Player.id
            ).join(
                Team, PlayerTeamHistory.team_id == Team.id
            ).filter(
                and_(PlayerTeamHistory.tournament_id == tournament.id,
                     PlayerTeamHistory.tournament_goals > 0)
            ).order_by(PlayerTeamHistory.tournament_goals.desc()).limit(5).all()
            
            # 射手榜 - 团队（从team表获取）
            team_goals = db.session.query(
                Team.name.label('team_name'),
                Team.tournament_goals.label('goals')
            ).filter(
                and_(Team.tournament_id == tournament.id,
                     Team.tournament_goals > 0)
            ).order_by(Team.tournament_goals.desc()).limit(5).all()
            
            # 红黄牌榜 - 个人（从player_team_history表获取）
            player_cards = db.session.query(
                PlayerTeamHistory.player_id,
                Player.name.label('player_name'),
                Team.name.label('team_name'),
                PlayerTeamHistory.tournament_yellow_cards.label('yellow_cards'),
                PlayerTeamHistory.tournament_red_cards.label('red_cards')
            ).join(
                Player, PlayerTeamHistory.player_id == Player.id
            ).join(
                Team, PlayerTeamHistory.team_id == Team.id
            ).filter(
                and_(PlayerTeamHistory.tournament_id == tournament.id,
                     or_(PlayerTeamHistory.tournament_yellow_cards > 0,
                         PlayerTeamHistory.tournament_red_cards > 0))
            ).order_by(
                PlayerTeamHistory.tournament_red_cards.desc(),
                PlayerTeamHistory.tournament_yellow_cards.desc()
            ).limit(5).all()
            
            # 红黄牌榜 - 团队（从team表获取）
            team_cards = db.session.query(
                Team.name.label('team_name'),
                Team.tournament_yellow_cards.label('yellow_cards'),
                Team.tournament_red_cards.label('red_cards')
            ).filter(
                and_(Team.tournament_id == tournament.id,
                     or_(Team.tournament_yellow_cards > 0,
                         Team.tournament_red_cards > 0))
            ).order_by(
                Team.tournament_red_cards.desc(),
                Team.tournament_yellow_cards.desc()
            ).limit(5).all()
            
            # 积分榜（使用team表中的积分数据）
            team_points = calculate_team_points(tournament.id)
            
            rankings[tournament_key] = {
                'topScorers': {
                    'players': [
                        {
                            'id': player.player_id,
                            'name': player.player_name,
                            'team': player.team_name,
                            'goals': int(player.goals or 0)
                        } for player in player_goals
                    ],
                    'teams': [
                        {
                            'team': team.team_name,
                            'goals': int(team.goals or 0)
                        } for team in team_goals
                    ]
                },
                'cards': {
                    'players': [
                        {
                            'id': player.player_id,
                            'name': player.player_name,
                            'team': player.team_name,
                            'yellowCards': int(player.yellow_cards or 0),
                            'redCards': int(player.red_cards or 0)
                        } for player in player_cards
                    ],
                    'teams': [
                        {
                            'team': team.team_name,
                            'yellowCards': int(team.yellow_cards or 0),
                            'redCards': int(team.red_cards or 0)
                        } for team in team_cards
                    ]
                },
                'points': team_points
            }
        
        return jsonify({
            'status': 'success',
            'data': rankings
        })
        
    except Exception as e:
        print(f"Rankings error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': f'获取排行数据失败: {str(e)}'
        }), 500

@stats_bp.route('/group-rankings', methods=['GET'])
def get_group_rankings():
    """获取分组排名数据"""
    try:
        # 获取八人制比赛的分组排名
        eightASide_tournament = Tournament.query.filter(Tournament.name.contains('八人制')).first()
        
        if not eightASide_tournament:
            return jsonify({
                'status': 'success',
                'data': {'eightASide': {'groups': []}}
            })
        
        # 这里需要根据实际的分组逻辑来实现
        # 暂时返回示例数据
        groups_data = {
            'eightASide': {
                'groups': [
                    {
                        'name': 'A组',
                        'teams': []
                    },
                    {
                        'name': 'B组', 
                        'teams': []
                    }
                ]
            }
        }
        
        return jsonify({
            'status': 'success',
            'data': groups_data
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取分组排名失败: {str(e)}'
        }), 500

@stats_bp.route('/playoff-bracket', methods=['GET'])
def get_playoff_bracket():
    """获取淘汰赛对阵图"""
    try:
        # 暂时返回示例数据
        bracket_data = {
            'championsCup': [],
            'womensCup': [],
            'eightASide': []
        }
        
        return jsonify({
            'status': 'success',
            'data': bracket_data
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取淘汰赛对阵失败: {str(e)}'
        }), 500

def get_tournament_key(tournament_name):
    """根据赛事名称获取键名"""
    if '冠军杯' in tournament_name:
        return 'championsCup'
    elif '巾帼杯' in tournament_name:
        return 'womensCup'
    elif '八人制' in tournament_name:
        return 'eightASide'
    else:
        return 'other'

def calculate_team_points(tournament_id):
    """计算球队积分（使用team表中的积分数据）"""
    try:
        # 直接从team表获取积分数据
        team_points = db.session.query(
            Team.name.label('team_name'),
            Team.tournament_points.label('points'),
            Team.tournament_goals.label('goals_for'),
            Team.tournament_goals_conceded.label('goals_against'),
            Team.tournament_goal_difference.label('goal_difference'),
            Team.tournament_rank.label('rank')
        ).filter(
            Team.tournament_id == tournament_id
        ).order_by(
            Team.tournament_points.desc(),
            Team.tournament_goal_difference.desc(),
            Team.tournament_goals.desc()
        ).limit(10).all()
        
        # 计算比赛场次（通过match表）
        results = []
        for team_data in team_points:
            # 查询该队的比赛场次
            matches_played = Match.query.filter(
                and_(
                    Match.tournament_id == tournament_id,
                    or_(Match.home_team_id == Team.query.filter_by(name=team_data.team_name, tournament_id=tournament_id).first().id,
                        Match.away_team_id == Team.query.filter_by(name=team_data.team_name, tournament_id=tournament_id).first().id),
                    Match.status == 'F'  # 只统计已完成的比赛
                )
            ).count()
            
            results.append({
                'team': team_data.team_name,
                'matchesPlayed': matches_played,
                'points': int(team_data.points or 0),
                'goalsFor': int(team_data.goals_for or 0),
                'goalsAgainst': int(team_data.goals_against or 0),
                'goalDifference': int(team_data.goal_difference or 0),
                'rank': team_data.rank
            })
        
        return results
        
    except Exception as e:
        print(f"Calculate team points error: {str(e)}")
        return []
