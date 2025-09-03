from flask import Blueprint, request, jsonify
from app.services import TeamHistoryService
from app.models import TeamBase, TeamTournamentParticipation, Tournament, Season, Competition
from app import db
from sqlalchemy import desc, func

team_history_bp = Blueprint('team_history', __name__)

@team_history_bp.route('/api/team-history/<team_base_id>/complete', methods=['GET'])
def get_team_complete_history(team_base_id):
    """获取球队完整的跨赛季历史记录"""
    try:
        result = TeamHistoryService.get_team_complete_history(team_base_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@team_history_bp.route('/api/team-history/<team_base_id>/season/<int:season_id>', methods=['GET'])
def get_team_season_performance(team_base_id, season_id):
    """获取球队在指定赛季的表现"""
    try:
        result = TeamHistoryService.get_team_season_performance(team_base_id, season_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@team_history_bp.route('/api/team-history/compare', methods=['POST'])
def compare_teams_across_seasons():
    """跨赛季球队对比"""
    try:
        data = request.get_json()
        team_base_ids = data.get('team_base_ids', [])
        season_ids = data.get('season_ids', [])  # 可选：指定赛季范围
        
        if not team_base_ids:
            return jsonify({'error': '请提供要比较的球队ID'}), 400
        
        result = TeamHistoryService.compare_teams_across_seasons(team_base_ids, season_ids)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@team_history_bp.route('/api/team-history/tournament-history/<team_base_id>', methods=['GET'])
def get_team_tournament_history(team_base_id):
    """获取球队参赛历史"""
    try:
        result = TeamHistoryService.get_team_tournament_history(team_base_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 保留原有的API路由以保持向后兼容性
def get_team_history(team_name):
    """获取指定球队的历史参赛记录"""
    try:
        # 查找基础球队信息
        team_base = TeamBase.query.filter_by(name=team_name).first()
        if not team_base:
            return jsonify({'error': '未找到球队'}), 404
        
        # 获取所有参赛记录，按时间倒序
        participations = TeamTournamentParticipation.query.filter_by(
            team_base_id=team_base.id
        ).join(Tournament).join(Season).order_by(desc(Season.start_date)).all()
        
        # 构建响应数据
        history_data = {
            'team_info': team_base.to_dict(),
            'participations': [
                {
                    'tournament_id': p.tournament_id,
                    'tournament_name': p.tournament.name,
                    'season_name': p.tournament.season.name,
                    'competition_name': p.tournament.competition.name,
                    'rank': p.rank,
                    'points': p.points,
                    'goals': p.goals,
                    'goals_conceded': p.goals_conceded,
                    'goal_difference': p.goal_difference,
                    'wins': p.wins,
                    'draws': p.draws,
                    'losses': p.losses,
                    'matches_played': p.matches_played
                }
                for p in participations
            ],
            'summary': team_base.get_historical_stats()
        }
        
        return jsonify(history_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@team_history_bp.route('/api/team-history/comparison', methods=['POST'])
def compare_teams():
    """比较多支球队的历史表现"""
    try:
        data = request.get_json()
        team_names = data.get('team_names', [])
        
        if not team_names:
            return jsonify({'error': '请提供要比较的球队名称'}), 400
        
        comparison_data = []
        
        for team_name in team_names:
            team_base = TeamBase.query.filter_by(name=team_name).first()
            if team_base:
                stats = team_base.get_historical_stats()
                comparison_data.append({
                    'team_name': team_name,
                    'stats': stats
                })
        
        return jsonify({
            'comparison': comparison_data,
            'timestamp': func.now()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@team_history_bp.route('/api/team-history/season/<int:season_id>', methods=['GET'])
def get_season_teams(season_id):
    """获取指定赛季的所有参赛球队"""
    try:
        # 获取赛季信息
        season = Season.query.get(season_id)
        if not season:
            return jsonify({'error': '未找到赛季'}), 404
        
        # 获取该赛季的所有赛事
        tournaments = Tournament.query.filter_by(season_id=season_id).all()
        
        season_data = {
            'season_info': {
                'id': season.id,
                'name': season.name,
                'start_date': season.start_date.isoformat() if season.start_date else None,
                'end_date': season.end_date.isoformat() if season.end_date else None
            },
            'tournaments': []
        }
        
        for tournament in tournaments:
            # 获取该赛事的参赛球队
            participations = TeamTournamentParticipation.query.filter_by(
                tournament_id=tournament.id
            ).join(TeamBase).order_by(TeamTournamentParticipation.rank.asc()).all()
            
            tournament_data = {
                'tournament_id': tournament.id,
                'tournament_name': tournament.name,
                'competition_name': tournament.competition.name if tournament.competition else None,
                'teams': [
                    {
                        'team_name': p.team_base.name,
                        'rank': p.rank,
                        'points': p.points,
                        'goals': p.goals,
                        'goals_conceded': p.goals_conceded,
                        'goal_difference': p.goal_difference,
                        'wins': p.wins,
                        'draws': p.draws,
                        'losses': p.losses,
                        'matches_played': p.matches_played
                    }
                    for p in participations
                ]
            }
            season_data['tournaments'].append(tournament_data)
        
        return jsonify(season_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@team_history_bp.route('/api/team-base', methods=['GET'])
def list_team_bases():
    """获取所有基础球队列表"""
    try:
        team_bases = TeamBase.query.all()
        
        teams_data = [
            {
                'id': team.id,
                'name': team.name,
                'created_at': team.created_at.isoformat() if team.created_at else None,
                'participation_count': len(team.participations),
                'total_goals': team.total_goals,
                'total_points': team.total_points,
                'win_rate': team.win_rate,
                'best_rank': team.best_rank
            }
            for team in team_bases
        ]
        
        return jsonify({
            'teams': teams_data,
            'total_count': len(teams_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@team_history_bp.route('/api/team-base/<int:team_base_id>/tournaments', methods=['GET'])
def get_team_tournaments(team_base_id):
    """获取指定基础球队的所有参赛赛事"""
    try:
        team_base = TeamBase.query.get(team_base_id)
        if not team_base:
            return jsonify({'error': '未找到球队'}), 404
        
        participations = TeamTournamentParticipation.query.filter_by(
            team_base_id=team_base_id
        ).join(Tournament).join(Season).order_by(desc(Season.start_date)).all()
        
        tournaments_data = [
            {
                'participation_id': p.id,
                'tournament_id': p.tournament_id,
                'tournament_name': p.tournament.name,
                'season_name': p.tournament.season.name,
                'competition_name': p.tournament.competition.name if p.tournament.competition else None,
                'start_date': p.tournament.season.start_date.isoformat() if p.tournament.season.start_date else None,
                'end_date': p.tournament.season.end_date.isoformat() if p.tournament.season.end_date else None,
                'performance': {
                    'rank': p.rank,
                    'points': p.points,
                    'goals': p.goals,
                    'goals_conceded': p.goals_conceded,
                    'goal_difference': p.goal_difference,
                    'wins': p.wins,
                    'draws': p.draws,
                    'losses': p.losses,
                    'matches_played': p.matches_played
                }
            }
            for p in participations
        ]
        
        return jsonify({
            'team_info': team_base.to_dict(),
            'tournaments': tournaments_data,
            'summary': team_base.get_historical_stats()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
