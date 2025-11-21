"""
球队历史服务类
处理球队跨赛季历史查询的业务逻辑
"""

from app.models import TeamBase, TeamTournamentParticipation, Tournament, Season, PlayerTeamHistory
from app.utils.team_history_utils import TeamHistoryUtils
from app.database import db
from sqlalchemy import desc, func
from collections import defaultdict


class TeamHistoryService:
    """球队历史查询服务"""
    
    @staticmethod
    def get_team_complete_history(team_base_id):
        """获取球队完整的跨赛季历史记录"""
        # 查找球队基础信息
        team_base = TeamBase.query.get(team_base_id)
        if not team_base:
            raise ValueError('未找到球队')
        
        # 获取球队所有参赛记录，按时间排序
        participations = TeamTournamentParticipation.query.filter_by(
            team_base_id=team_base_id
        ).join(Tournament).join(Season).order_by(desc(Season.start_time)).all()
        
        if not participations:
            return {
                'team_info': {
                    'id': team_base.id,
                    'name': team_base.name
                },
                'seasons': [],
                'career_summary': TeamHistoryUtils.get_empty_career_summary()
            }
        
        # 按赛季分组数据
        seasons_data = defaultdict(lambda: {
            'season_info': {},
            'tournaments': [],
            'season_totals': {
                'tournaments_count': 0,
                'total_players': 0,
                'total_goals': 0,
                'total_yellow_cards': 0,
                'total_red_cards': 0
            }
        })
        
        # 预加载所有相关的球员历史记录，避免 N+1 查询
        participation_ids = [p.id for p in participations]
        all_player_stats = []
        if participation_ids:
            all_player_stats = PlayerTeamHistory.query.filter(
                PlayerTeamHistory.team_id.in_(participation_ids)
            ).all()
        
        # 将球员记录按 team_id (即 participation.id) 分组
        player_stats_map = defaultdict(list)
        for ps in all_player_stats:
            player_stats_map[ps.team_id].append(ps)

        # 处理每条参赛记录
        for participation in participations:
            if not participation.tournament or not participation.tournament.season:
                continue
                
            season = participation.tournament.season
            tournament = participation.tournament
            season_key = season.name
            
            # 填充赛季信息
            if not seasons_data[season_key]['season_info']:
                seasons_data[season_key]['season_info'] = {
                    'id': season.season_id,
                    'name': season.name,
                    'start_date': season.start_time.isoformat() if season.start_time else None,
                    'end_date': season.end_time.isoformat() if season.end_time else None,
                }
            
            # 获取该赛事中的球员统计 (从内存中获取)
            players_stats = player_stats_map.get(participation.id, [])
            
            # 重新使用球员统计数据进行累加，以确保数据准确性（解决数据库中 participation 统计可能为 0 的问题）
            # 同时保持了 N+1 优化的成果（数据已预加载）
            p_goals = sum(p.tournament_goals for p in players_stats if p.tournament_goals)
            p_yellow = sum(p.tournament_yellow_cards for p in players_stats if p.tournament_yellow_cards)
            p_red = sum(p.tournament_red_cards for p in players_stats if p.tournament_red_cards)
            
            tournament_stats = {
                'players_count': len(players_stats),
                'total_goals': p_goals,
                'total_goals_conceded': participation.tournament_goals_conceded if participation.tournament_goals_conceded is not None else 0, # 失球数通常只在球队记录中有
                'total_goal_difference': participation.tournament_goal_difference if participation.tournament_goal_difference is not None else (p_goals - (participation.tournament_goals_conceded or 0)),
                'total_points': participation.tournament_points if participation.tournament_points is not None else 0,
                'total_yellow_cards': p_yellow,
                'total_red_cards': p_red
            }
            
            # 序列化球员列表
            players_list = []
            for p in players_stats:
                players_list.append({
                    'playerId': p.player_id, 
                    'name': p.player.name if p.player else '未知球员',
                    'number': p.player_number,
                    'goals': p.tournament_goals,
                    'yellowCards': p.tournament_yellow_cards,
                    'redCards': p.tournament_red_cards
                })

            # 添加赛事记录
            tournament_record = {
                'tournament_id': tournament.id,
                'tournament_name': tournament.name,
                'competition_name': tournament.competition.name if tournament.competition else None,
                'team_id': participation.id,
                'team_name': participation.team_base.name if participation.team_base else None,
                'final_ranking': participation.tournament_rank,
                'remarks': None,
                'stats': tournament_stats,
                'players': players_list # 添加球员列表
            }
            
            seasons_data[season_key]['tournaments'].append(tournament_record)
            
            # 累加赛季统计
            seasons_data[season_key]['season_totals']['tournaments_count'] += 1
            seasons_data[season_key]['season_totals']['total_players'] += tournament_stats['players_count']
            seasons_data[season_key]['season_totals']['total_goals'] += tournament_stats['total_goals']
            seasons_data[season_key]['season_totals']['total_yellow_cards'] += tournament_stats['total_yellow_cards']
            seasons_data[season_key]['season_totals']['total_red_cards'] += tournament_stats['total_red_cards']
        
        # 转换为列表格式
        seasons_list = []
        for season_key in sorted(seasons_data.keys(), reverse=True):  # 按赛季倒序
            season_data = seasons_data[season_key]
            seasons_list.append({
                'season_info': season_data['season_info'],
                'tournaments': season_data['tournaments'],
                'season_totals': season_data['season_totals']
            })
        
        # 计算职业生涯汇总 (基于已计算的 seasons_list，避免再次查询或使用不准确的 participation 数据)
        career_summary = {
            'total_tournaments': 0,
            'total_seasons': len(seasons_list),
            'total_players_used': 0, # 难以精确去重，暂且累加或忽略
            'total_goals_scored': 0,
            'total_goals_conceded': 0,
            'total_goal_difference': 0,
            'total_points': 0,
            'total_yellow_cards': 0,
            'total_red_cards': 0,
            'best_ranking': None,
            'average_ranking': 0,
            'average_goals_per_tournament': 0,
            'disciplinary_record': {'yellow_card_rate': 0, 'red_card_rate': 0}
        }
        
        all_rankings = []
        
        for season in seasons_list:
            for t in season['tournaments']:
                career_summary['total_tournaments'] += 1
                career_summary['total_goals_scored'] += t['stats']['total_goals']
                career_summary['total_goals_conceded'] += t['stats']['total_goals_conceded']
                career_summary['total_goal_difference'] += t['stats']['total_goal_difference']
                career_summary['total_points'] += t['stats']['total_points']
                career_summary['total_yellow_cards'] += t['stats']['total_yellow_cards']
                career_summary['total_red_cards'] += t['stats']['total_red_cards']
                
                if t['final_ranking']:
                    all_rankings.append(t['final_ranking'])
        
        if all_rankings:
            career_summary['best_ranking'] = min(all_rankings)
            career_summary['average_ranking'] = sum(all_rankings) / len(all_rankings)
            
        if career_summary['total_tournaments'] > 0:
            career_summary['average_goals_per_tournament'] = career_summary['total_goals_scored'] / career_summary['total_tournaments']
            career_summary['disciplinary_record']['yellow_card_rate'] = career_summary['total_yellow_cards'] / career_summary['total_tournaments']
            career_summary['disciplinary_record']['red_card_rate'] = career_summary['total_red_cards'] / career_summary['total_tournaments']

        # 尝试计算去重后的球员总数
        unique_player_ids = set()
        for ps in all_player_stats:
            unique_player_ids.add(ps.player_id)
        career_summary['total_players_used'] = len(unique_player_ids)
        
        return {
            'team_info': {
                'id': team_base.id,
                'name': team_base.name
            },
            'seasons': seasons_list,
            'career_summary': career_summary
        }
    
    @staticmethod
    def get_team_season_performance(team_base_id, season_id):
        """获取球队在指定赛季的表现"""
        # 查找球队
        team_base = TeamBase.query.get(team_base_id)
        if not team_base:
            raise ValueError('未找到球队')
        
        # 查找赛季
        season = Season.query.get(season_id)
        if not season:
            raise ValueError('未找到赛季')
        
        # 获取该赛季的所有赛事
        tournaments = Tournament.query.filter_by(season_id=season_id).all()
        tournament_ids = [t.id for t in tournaments]
        
        # 获取球队在该赛季的所有参赛记录
        participations = TeamTournamentParticipation.query.filter(
            TeamTournamentParticipation.team_base_id == team_base_id,
            TeamTournamentParticipation.tournament_id.in_(tournament_ids)
        ).all()
        
        if not participations:
            return {
                'team_info': {'id': team_base.id, 'name': team_base.name},
                'season_info': {'id': season.season_id, 'name': season.name},
                'performance': [],
                'season_totals': TeamHistoryUtils.get_empty_season_totals()
            }
        
        # 组织数据
        performance_data = []
        season_totals = {
            'tournaments_participated': 0,
            'total_players': 0,
            'total_goals': 0,
            'total_yellow_cards': 0,
            'total_red_cards': 0,
            'average_ranking': 0
        }
        
        total_ranking = 0
        ranking_count = 0
        
        for participation in participations:
            tournament = participation.tournament
            
            # 获取该赛事中的球员统计
            players_stats = PlayerTeamHistory.query.filter_by(
                team_id=participation.id,
                tournament_id=tournament.id
            ).all()
            
            tournament_stats = {
                'players_count': len(players_stats),
                'total_goals': sum(p.tournament_goals for p in players_stats),
                'total_yellow_cards': sum(p.tournament_yellow_cards for p in players_stats),
                'total_red_cards': sum(p.tournament_red_cards for p in players_stats)
            }
            
            performance_record = {
                'tournament_id': tournament.id,
                'tournament_name': tournament.name,
                'competition_name': tournament.competition.name if tournament.competition else None,
                'team_id': participation.id,
                'team_name': participation.team_base.name if participation.team_base else None,
                'final_ranking': participation.tournament_rank,
                'remarks': None,  # 模型中没有remarks字段
                'stats': tournament_stats
            }
            
            performance_data.append(performance_record)
            
            # 累计统计
            season_totals['tournaments_participated'] += 1
            season_totals['total_players'] += tournament_stats['players_count']
            season_totals['total_goals'] += tournament_stats['total_goals']
            season_totals['total_yellow_cards'] += tournament_stats['total_yellow_cards']
            season_totals['total_red_cards'] += tournament_stats['total_red_cards']
            
            if participation.tournament_rank:
                total_ranking += participation.tournament_rank
                ranking_count += 1
        
        if ranking_count > 0:
            season_totals['average_ranking'] = round(total_ranking / ranking_count, 2)
        
        return {
            'team_info': {'id': team_base.id, 'name': team_base.name},
            'season_info': {
                'id': season.season_id,
                'name': season.name,
                'start_date': season.start_time.isoformat() if season.start_time else None,
                'end_date': season.end_time.isoformat() if season.end_time else None
            },
            'performance': performance_data,
            'season_totals': season_totals
        }
    
    @staticmethod
    def compare_teams_across_seasons(team_base_ids, season_ids=None):
        """跨赛季球队对比"""
        comparison_data = []
        
        for team_base_id in team_base_ids:
            team_base = TeamBase.query.get(team_base_id)
            if not team_base:
                continue
            
            # 构建查询条件
            query = TeamTournamentParticipation.query.filter_by(team_base_id=team_base_id)
            
            if season_ids:
                # 如果指定了赛季，只查询这些赛季的数据
                tournaments = Tournament.query.filter(Tournament.season_id.in_(season_ids)).all()
                tournament_ids = [t.id for t in tournaments]
                query = query.filter(TeamTournamentParticipation.tournament_id.in_(tournament_ids))
            
            participations = query.all()
            
            # 计算球队统计
            team_stats = TeamHistoryUtils.calculate_career_summary(participations)
            team_stats['team_info'] = {
                'id': team_base.id,
                'name': team_base.name
            }
            
            comparison_data.append(team_stats)
        
        return {
            'comparison': comparison_data,
            'comparison_metadata': {
                'total_teams': len(comparison_data),
                'season_filter': season_ids,
                'comparison_date': func.now()
            }
        }
    
    @staticmethod
    def get_team_tournament_history(team_base_id):
        """获取球队参赛历史"""
        team_base = TeamBase.query.get(team_base_id)
        if not team_base:
            raise ValueError('未找到球队')
        
        # 获取球队所有参赛记录，按时间排序
        participations = TeamTournamentParticipation.query.filter_by(
            team_base_id=team_base_id
        ).join(Tournament).join(Season).order_by(Season.start_time, Tournament.id).all()
        
        if not participations:
            return {
                'team_info': {'id': team_base.id, 'name': team_base.name},
                'tournament_history': [],
                'summary': {'total_tournaments': 0, 'total_seasons': 0, 'best_ranking': None}
            }
        
        # 分析参赛历史
        tournament_history = []
        seasons_participated = set()
        rankings = []
        
        for participation in participations:
            if not participation.tournament or not participation.tournament.season:
                continue
            
            tournament_record = {
                'season_name': participation.tournament.season.name,
                'tournament_name': participation.tournament.name,
                'competition_name': participation.tournament.competition.name if participation.tournament.competition else None,
                'team_name': participation.team_base.name if participation.team_base else None,
                'final_ranking': participation.tournament_rank,
                'remarks': None  # 模型中没有remarks字段
            }
            
            tournament_history.append(tournament_record)
            seasons_participated.add(participation.tournament.season.name)
            
            if participation.tournament_rank:
                rankings.append(participation.tournament_rank)
        
        best_ranking = min(rankings) if rankings else None
        
        return {
            'team_info': {'id': team_base.id, 'name': team_base.name},
            'tournament_history': tournament_history,
            'summary': {
                'total_tournaments': len(tournament_history),
                'total_seasons': len(seasons_participated),
                'best_ranking': best_ranking
            }
        }
