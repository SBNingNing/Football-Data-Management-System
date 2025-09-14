"""球队工具集: 比赛类型归一化 / 名称与统计辅助。"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class TeamUtils:
    """球队工具函数集合。"""

    # 比赛类型英文规范列表
    VALID_MATCH_TYPES = ['champions-cup', 'womens-cup', 'eight-a-side']
    # 中英文 & 变体别名映射到规范英文
    MATCH_TYPE_ALIAS_MAP = {
        # 冠军/校园杯
        '冠军杯': 'champions-cup', '校园杯': 'champions-cup',
        # 巾帼 / 女子 杯
        '巾帼杯': 'womens-cup', '女子杯': 'womens-cup', '女足杯': 'womens-cup',
        # 八人制
        '八人制': 'eight-a-side', '八人赛': 'eight-a-side', '8人制': 'eight-a-side',
    }

    @staticmethod
    def normalize_match_type(raw: str) -> tuple[str | None, str | None]:
        """比赛类型别名 -> 规范英文; 返回 (canonical, error)。"""
        if not raw:
            return 'champions-cup', None  # 默认
        raw = str(raw).strip()
        canonical = TeamUtils.MATCH_TYPE_ALIAS_MAP.get(raw, raw)
        if canonical not in TeamUtils.VALID_MATCH_TYPES:
            valid_cn = '冠军杯/校园杯, 巾帼杯/女子杯/女足杯, 八人制/八人赛/8人制'
            valid_en = ', '.join(TeamUtils.VALID_MATCH_TYPES)
            return None, f'无效的比赛类型({raw})。有效英文: {valid_en} | 中文: {valid_cn}'
        return canonical, None
    
    @staticmethod
    def determine_match_type(tournament) -> str:
        """从赛事名称推断 matchType。"""
        if tournament:
            tournament_name = tournament.name.lower()
            if '冠军杯' in tournament_name or '校园杯' in tournament_name or 'champions' in tournament_name:
                return 'champions-cup'
            elif '巾帼杯' in tournament_name or '女子杯' in tournament_name or '女足杯' in tournament_name or 'womens' in tournament_name:
                return 'womens-cup'
            elif '八人制' in tournament_name or 'eight' in tournament_name:
                return 'eight-a-side'
            else:
                return 'champions-cup'
        else:
            return 'champions-cup'
    
    @staticmethod
    def get_tournament_id_by_match_type(match_type: str) -> int:
        """比赛类型 -> 固定 tournamentId 映射。"""
        match_type_to_tournament = {
            'champions-cup': 1,  # 冠军杯
            'womens-cup': 2,     # 巾帼杯
            'eight-a-side': 3    # 八人制比赛
        }
        return match_type_to_tournament.get(match_type, 1)
    
    @staticmethod
    def format_team_name(name: str) -> str:
        """格式化球队名称。"""
        if not name:
            return ""
        
        # 去除首尾空格和多余的空格
        formatted_name = name.strip()
        formatted_name = re.sub(r'\s+', ' ', formatted_name)
        return formatted_name
    
    @staticmethod
    def validate_team_name(name: str) -> tuple[bool, str]:
        """验证球队名称。"""
        if not name or not name.strip():
            return False, "球队名称不能为空"
        
        name = name.strip()
        
        if len(name) < 2:
            return False, "球队名称至少需要2个字符"
        
        if len(name) > 50:
            return False, "球队名称不能超过50个字符"
        
        # 字符检查 - 允许中文、英文、数字、空格、常用标点
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9\s\-_()（）]+$', name):
            return False, "球队名称只能包含中文、英文、数字、空格和常用标点符号"
        
        return True, ""
    
    @staticmethod
    def calculate_win_rate(wins: int, total_matches: int) -> float:
        """胜率。"""
        if total_matches == 0:
            return 0.0
        return round(wins / total_matches, 3)
    
    @staticmethod
    def calculate_goal_difference(goals: int, goals_conceded: int) -> int:
        """净胜球。"""
        return goals - goals_conceded
    
    @staticmethod
    def format_player_data(player_history) -> Dict[str, Any]:
        """球员历史 -> 字典。"""
        if not player_history or not player_history.player:
            return {}
        
        return {
            'name': player_history.player.name,
            'playerId': player_history.player_id,
            'studentId': player_history.player_id,
            'id': player_history.player_id,
            'number': str(player_history.player_number),
            'goals': player_history.tournament_goals or 0,
            'redCards': player_history.tournament_red_cards or 0,
            'yellowCards': player_history.tournament_yellow_cards or 0
        }
    
    @staticmethod
    def build_team_dict_from_model(team) -> Dict[str, Any]:
        """模型 -> 标准化字典。"""
        if not team:
            return {}
        
        team_dict = team.to_dict() if hasattr(team, 'to_dict') else {}
        
        # 标准化字段名
        standardized_dict = {
            'id': team.id if hasattr(team, 'id') else None,
            'teamName': team.name if hasattr(team, 'name') else '',
            'name': team.name if hasattr(team, 'name') else '',
            'tournamentId': team.tournament_id if hasattr(team, 'tournament_id') else None,
            'tournamentName': team.tournament.name if hasattr(team, 'tournament') and team.tournament else None,
            'matchType': TeamUtils.determine_match_type(team.tournament if hasattr(team, 'tournament') else None),
            'groupId': team.group_id if hasattr(team, 'group_id') else None,
            'rank': team.tournament_rank if hasattr(team, 'tournament_rank') else None,
            'goals': team.tournament_goals if hasattr(team, 'tournament_goals') else 0,
            'goalsConceded': team.tournament_goals_conceded if hasattr(team, 'tournament_goals_conceded') else 0,
            'goalDifference': team.tournament_goal_difference if hasattr(team, 'tournament_goal_difference') else 0,
            'redCards': team.tournament_red_cards if hasattr(team, 'tournament_red_cards') else 0,
            'yellowCards': team.tournament_yellow_cards if hasattr(team, 'tournament_yellow_cards') else 0,
            'points': team.tournament_points if hasattr(team, 'tournament_points') else 0,
            'matchesPlayed': team.matches_played if hasattr(team, 'matches_played') else 0,
            'wins': team.wins if hasattr(team, 'wins') else 0,
            'draws': team.draws if hasattr(team, 'draws') else 0,
            'losses': team.losses if hasattr(team, 'losses') else 0,
            'createdAt': team.created_at.isoformat() if hasattr(team, 'created_at') and team.created_at else None
        }
        
        return standardized_dict
    
    @staticmethod
    def sort_teams_by_criteria(teams: List[Dict[str, Any]], 
                              sort_by: str = 'points') -> List[Dict[str, Any]]:
        """简单列表排序。"""
        if not teams:
            return []
        
        try:
            if sort_by == 'points':
                return sorted(teams, key=lambda x: x.get('points', 0), reverse=True)
            elif sort_by == 'goals':
                return sorted(teams, key=lambda x: x.get('goals', 0), reverse=True)
            elif sort_by == 'rank':
                # 排名越小越好（正序）
                return sorted(teams, key=lambda x: x.get('rank', 999))
            elif sort_by == 'name':
                return sorted(teams, key=lambda x: x.get('teamName', ''))
            else:
                logger.warning(f"Unknown sort criteria: {sort_by}, using default 'points'")
                return sorted(teams, key=lambda x: x.get('points', 0), reverse=True)
        except Exception as e:
            logger.error(f"Error sorting teams: {e}")
            return teams
    
    @staticmethod
    def filter_teams_by_tournament(teams: List[Dict[str, Any]], 
                                 tournament_id: int) -> List[Dict[str, Any]]:
        """过滤: 赛事ID。"""
        if not teams:
            return []
        return [team for team in teams if team.get('tournamentId') == tournament_id]
    
    @staticmethod
    def filter_teams_by_match_type(teams: List[Dict[str, Any]], 
                                  match_type: str) -> List[Dict[str, Any]]:
        """过滤: 比赛类型。"""
        if not teams:
            return []
        return [team for team in teams if team.get('matchType') == match_type]
    
    @staticmethod
    def get_team_statistics(teams: List[Dict[str, Any]]) -> Dict[str, Any]:
        """总体统计。"""
        if not teams:
            return {
                'total_teams': 0,
                'total_goals': 0,
                'total_matches': 0,
                'average_goals_per_team': 0,
                'top_scorer_team': None
            }
        
        total_teams = len(teams)
        total_goals = sum(team.get('goals', 0) for team in teams)
        total_matches = sum(team.get('matchesPlayed', 0) for team in teams)
        average_goals = round(total_goals / total_teams, 2) if total_teams > 0 else 0
        
        # 找到进球最多的球队
        top_scorer = max(teams, key=lambda x: x.get('goals', 0)) if teams else None
        
        return {
            'total_teams': total_teams,
            'total_goals': total_goals,
            'total_matches': total_matches,
            'average_goals_per_team': average_goals,
            'top_scorer_team': top_scorer.get('teamName') if top_scorer else None,
            'top_scorer_goals': top_scorer.get('goals', 0) if top_scorer else 0
        }
    
    @staticmethod
    def validate_player_data(players: List[Dict[str, Any]]) -> tuple[bool, str]:
        """验证球员列表。"""
        if not isinstance(players, list):
            return False, "球员数据必须是列表格式"
        
        if len(players) == 0:
            return False, "至少需要一名球员"
        
        if len(players) > 30:
            return False, "球员数量不能超过30人"
        
        # 检查球员号码是否重复
        numbers = []
        student_ids = []
        
        for i, player in enumerate(players):
            if not isinstance(player, dict):
                return False, f"第{i+1}个球员数据格式错误"
            
            # 检查必要字段
            if not player.get('name'):
                return False, f"第{i+1}个球员姓名不能为空"
            
            if not player.get('studentId'):
                return False, f"第{i+1}个球员学号不能为空"
            
            # 检查号码重复
            number = player.get('number', 1)
            try:
                number = int(number)
                if number in numbers:
                    return False, f"球员号码{number}重复"
                numbers.append(number)
            except (ValueError, TypeError):
                return False, f"第{i+1}个球员号码格式错误"
            
            # 检查学号重复
            student_id = str(player['studentId'])
            if student_id in student_ids:
                return False, f"学号{student_id}重复"
            student_ids.append(student_id)
        
        return True, ""
    
    @staticmethod
    def format_timestamp(timestamp) -> Optional[str]:
        """统一时间格式。"""
        if not timestamp:
            return None
        
        try:
            if hasattr(timestamp, 'isoformat'):
                return timestamp.isoformat()
            else:
                return str(timestamp)
        except Exception as e:
            logger.error(f"格式化时间戳失败: {str(e)}")
            return None
    
    @staticmethod
    def calculate_team_historical_metrics(participations_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """聚合历史指标。"""
        if not participations_data:
            return TeamUtils._get_empty_historical_stats()
        
        # 聚合统计
        total_tournaments = len(participations_data)
        total_goals = sum(p.get('tournament_goals', 0) for p in participations_data)
        total_goals_conceded = sum(p.get('goals_conceded', 0) for p in participations_data)
        total_points = sum(p.get('points', 0) for p in participations_data)
        total_matches = sum(p.get('matches_played', 0) for p in participations_data)
        total_wins = sum(p.get('wins', 0) for p in participations_data)
        total_draws = sum(p.get('draws', 0) for p in participations_data)
        total_losses = sum(p.get('losses', 0) for p in participations_data)
        total_red_cards = sum(p.get('red_cards', 0) for p in participations_data)
        total_yellow_cards = sum(p.get('yellow_cards', 0) for p in participations_data)
        
        # 计算衍生统计
        goal_difference = total_goals - total_goals_conceded
        win_rate = (total_wins / total_matches * 100) if total_matches > 0 else 0.0
        draw_rate = (total_draws / total_matches * 100) if total_matches > 0 else 0.0
        loss_rate = (total_losses / total_matches * 100) if total_matches > 0 else 0.0
        avg_goals_per_match = total_goals / total_matches if total_matches > 0 else 0.0
        avg_goals_conceded_per_match = total_goals_conceded / total_matches if total_matches > 0 else 0.0
        avg_points_per_match = total_points / total_matches if total_matches > 0 else 0.0
        
        # 最佳排名
        valid_ranks = [p.get('rank') for p in participations_data if p.get('rank') and p.get('rank') > 0]
        best_rank = min(valid_ranks) if valid_ranks else None
        
        return {
            'basic_stats': {
                'total_tournaments': total_tournaments,
                'total_matches_played': total_matches,
                'total_wins': total_wins,
                'total_draws': total_draws,
                'total_losses': total_losses,
                'total_points': total_points
            },
            'goal_stats': {
                'total_goals': total_goals,
                'total_goals_conceded': total_goals_conceded,
                'goal_difference': goal_difference,
                'avg_goals_per_match': round(avg_goals_per_match, 2),
                'avg_goals_conceded_per_match': round(avg_goals_conceded_per_match, 2)
            },
            'performance_stats': {
                'win_rate': round(win_rate, 2),
                'draw_rate': round(draw_rate, 2),
                'loss_rate': round(loss_rate, 2),
                'avg_points_per_match': round(avg_points_per_match, 2),
                'best_rank': best_rank
            },
            'discipline_stats': {
                'total_red_cards': total_red_cards,
                'total_yellow_cards': total_yellow_cards,
                'avg_red_cards_per_match': round(total_red_cards / total_matches, 2) if total_matches > 0 else 0.0,
                'avg_yellow_cards_per_match': round(total_yellow_cards / total_matches, 2) if total_matches > 0 else 0.0
            }
        }
    
    @staticmethod
    def _get_empty_historical_stats() -> Dict[str, Any]:
        """空历史结构。"""
        return {
            'basic_stats': {
                'total_tournaments': 0,
                'total_matches_played': 0,
                'total_wins': 0,
                'total_draws': 0,
                'total_losses': 0,
                'total_points': 0
            },
            'goal_stats': {
                'total_goals': 0,
                'total_goals_conceded': 0,
                'goal_difference': 0,
                'avg_goals_per_match': 0.0,
                'avg_goals_conceded_per_match': 0.0
            },
            'performance_stats': {
                'win_rate': 0.0,
                'draw_rate': 0.0,
                'loss_rate': 0.0,
                'avg_points_per_match': 0.0,
                'best_rank': None
            },
            'discipline_stats': {
                'total_red_cards': 0,
                'total_yellow_cards': 0,
                'avg_red_cards_per_match': 0.0,
                'avg_yellow_cards_per_match': 0.0
            }
        }
    
    @staticmethod
    def sort_teams_by_performance_criteria(teams_data: List[Dict[str, Any]], criteria: str = 'win_rate') -> List[Dict[str, Any]]:
        """按性能标准排序。"""
        if not teams_data:
            return []
        
        try:
            if criteria == 'win_rate':
                return sorted(teams_data, key=lambda x: x['stats']['performance_stats']['win_rate'], reverse=True)
            elif criteria == 'total_goals':
                return sorted(teams_data, key=lambda x: x['stats']['goal_stats']['total_goals'], reverse=True)
            elif criteria == 'total_tournaments':
                return sorted(teams_data, key=lambda x: x['stats']['basic_stats']['total_tournaments'], reverse=True)
            elif criteria == 'best_rank':
                return sorted(teams_data, key=lambda x: (
                    x['stats']['performance_stats']['best_rank'] is None,
                    x['stats']['performance_stats']['best_rank'] or float('inf')
                ))
            else:
                return teams_data
        except Exception as e:
            logger.error(f"排序球队数据失败: {e}")
            return teams_data
