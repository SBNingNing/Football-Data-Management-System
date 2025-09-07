"""
球员历史数据服务类 - 重构版
专门处理球员跨赛季查询和统计分析
采用四层架构：服务层专注业务逻辑，工具函数移至utils层
"""

from app.models import Player, PlayerTeamHistory, Tournament, Season, Competition, TeamBase
from app.utils.player_history_utils import PlayerHistoryUtils
from app.database import db
from sqlalchemy import desc, func
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Optional, Any


class PlayerHistoryService:
    """球员历史数据服务类"""
    
    @staticmethod
    def get_player_complete_history(player_id: str) -> Dict[str, Any]:
        """获取球员完整的跨赛季历史记录"""
        # 查找球员
        player = Player.query.get(player_id)
        if not player:
            raise ValueError('未找到球员')
        
        # 获取球员所有历史记录，按时间排序
        histories = PlayerTeamHistory.query.filter_by(
            player_id=player_id
        ).join(Tournament).join(Season).order_by(desc(Season.start_date)).all()
        
        if not histories:
            return {
                'player_info': PlayerHistoryUtils.format_player_basic_info(player),
                'seasons': [],
                'career_summary': PlayerHistoryUtils.get_empty_career_summary()
            }
        
        # 按赛季分组数据
        seasons_data = PlayerHistoryUtils.group_histories_by_season(histories)
        
        # 转换为列表格式，按赛季倒序
        seasons_list = []
        for season_name in sorted(seasons_data.keys(), reverse=True):
            season_histories = seasons_data[season_name]
            season_summary = PlayerHistoryUtils.format_season_summary({
                'season_name': season_name,
                'histories': season_histories
            })
            
            # 构建团队记录
            team_records = []
            for history in season_histories:
                team_record = PlayerHistoryUtils.build_team_change_record(history)
                team_records.append(team_record)
            
            seasons_list.append({
                'season_name': season_name,
                'teams': team_records,
                'season_summary': season_summary
            })
        
        # 计算职业生涯汇总
        career_summary = PlayerHistoryUtils.calculate_career_statistics(histories)
        
        return {
            'player_info': PlayerHistoryUtils.format_player_basic_info(player),
            'seasons': seasons_list,
            'career_summary': career_summary
        }
    
    @staticmethod
    def get_player_season_performance(player_id: str, season_id: int) -> Dict[str, Any]:
        """获取球员在指定赛季的表现"""
        # 查找球员
        player = Player.query.get(player_id)
        if not player:
            raise ValueError('未找到球员')
        
        # 查找赛季
        season = Season.query.get(season_id)
        if not season:
            raise ValueError('未找到赛季')
        
        # 获取该赛季的所有赛事
        tournaments = Tournament.query.filter_by(season_id=season_id).all()
        tournament_ids = [t.id for t in tournaments]
        
        # 获取球员在该赛季的所有记录
        histories = PlayerTeamHistory.query.filter(
            PlayerTeamHistory.player_id == player_id,
            PlayerTeamHistory.tournament_id.in_(tournament_ids)
        ).all()
        
        if not histories:
            return {
                'player_info': PlayerHistoryUtils.format_player_basic_info(player),
                'season_info': {
                    'id': season.id,
                    'name': season.name,
                    'start_date': PlayerHistoryUtils.safe_date_format(season.start_date),
                    'end_date': PlayerHistoryUtils.safe_date_format(season.end_date)
                },
                'performance': [],
                'season_totals': PlayerHistoryUtils.get_empty_season_totals()
            }
        
        # 计算赛季统计
        season_totals = {
            'total_goals': sum(h.tournament_goals or 0 for h in histories),
            'total_yellow_cards': sum(h.tournament_yellow_cards or 0 for h in histories),
            'total_red_cards': sum(h.tournament_red_cards or 0 for h in histories),
            'tournaments_participated': len(set(h.tournament_id for h in histories)),
            'teams_played_for': len(PlayerHistoryUtils.extract_unique_teams(histories))
        }
        
        # 构建表现记录
        performance_data = []
        for history in histories:
            performance_record = PlayerHistoryUtils.build_team_change_record(history)
            performance_data.append(performance_record)
        
        return {
            'player_info': PlayerHistoryUtils.format_player_basic_info(player),
            'season_info': {
                'id': season.id,
                'name': season.name,
                'start_date': PlayerHistoryUtils.safe_date_format(season.start_date),
                'end_date': PlayerHistoryUtils.safe_date_format(season.end_date)
            },
            'performance': performance_data,
            'season_totals': season_totals
        }
    
    @staticmethod
    def compare_players_across_seasons(player_ids: List[str], season_ids: List[int] = None) -> Dict[str, Any]:
        """跨赛季球员对比"""
        comparison_data = []
        
        for player_id in player_ids:
            player = Player.query.get(player_id)
            if not player:
                continue
            
            # 构建查询条件
            query = PlayerTeamHistory.query.filter_by(player_id=player_id)
            
            if season_ids:
                # 如果指定了赛季，只查询这些赛季的数据
                tournaments = Tournament.query.filter(Tournament.season_id.in_(season_ids)).all()
                tournament_ids = [t.id for t in tournaments]
                query = query.filter(PlayerTeamHistory.tournament_id.in_(tournament_ids))
            
            histories = query.all()
            
            # 计算球员统计
            player_stats = PlayerHistoryUtils.calculate_career_statistics(histories)
            player_stats['player_info'] = PlayerHistoryUtils.format_player_basic_info(player)
            
            comparison_data.append(player_stats)
        
        return {
            'comparison': comparison_data,
            'comparison_metadata': PlayerHistoryUtils.format_comparison_metadata(
                len(comparison_data), season_ids
            )
        }
    
    @staticmethod
    def get_player_team_changes(player_id: str) -> Dict[str, Any]:
        """获取球员转队历史"""
        player = Player.query.get(player_id)
        if not player:
            raise ValueError('未找到球员')
        
        # 获取球员所有历史记录，按时间排序
        histories = PlayerTeamHistory.query.filter_by(
            player_id=player_id
        ).join(Tournament).join(Season).order_by(Season.start_date, Tournament.id).all()
        
        if not histories:
            return {
                'player_info': PlayerHistoryUtils.format_player_basic_info(player),
                'team_changes': [],
                'summary': {'total_teams': 0, 'total_transfers': 0}
            }
        
        # 分析转队历史
        team_changes = []
        seen_teams = set()
        
        for history in histories:
            team_name = PlayerHistoryUtils._get_team_name(history)
            if team_name and team_name not in seen_teams:
                team_record = PlayerHistoryUtils.build_team_change_record(history)
                team_changes.append(team_record)
                seen_teams.add(team_name)
        
        return {
            'player_info': PlayerHistoryUtils.format_player_basic_info(player),
            'team_changes': team_changes,
            'summary': {
                'total_teams': len(seen_teams),
                'total_transfers': max(0, len(seen_teams) - 1)  # 转队次数 = 球队数 - 1
            }
        }
