from typing import List, Dict, Any, Optional, Tuple
import csv
import io
from app.utils.logger import get_logger

logger = get_logger(__name__)


class StatsUtils:
    """统计工具类 - 提供各种统计计算和数据处理功能"""
    
    @staticmethod
    def calculate_percentage(part: int, total: int, decimal_places: int = 2) -> float:
        """计算百分比"""
        if total == 0:
            return 0.0
        return round((part / total) * 100, decimal_places)
    
    @staticmethod
    def calculate_average(values: List[float], decimal_places: int = 2) -> float:
        """计算平均值"""
        if not values:
            return 0.0
        return round(sum(values) / len(values), decimal_places)
    
    @staticmethod
    def calculate_win_rate(wins: int, total_matches: int, decimal_places: int = 2) -> float:
        """计算胜率"""
        return StatsUtils.calculate_percentage(wins, total_matches, decimal_places)
    
    @staticmethod
    def format_ranking_display(rankings: List[Dict[str, Any]], 
                             include_rank: bool = True) -> List[Dict[str, Any]]:
        """格式化排行榜显示"""
        try:
            formatted_rankings = []
            for i, item in enumerate(rankings, 1):
                formatted_item = item.copy()
                if include_rank:
                    formatted_item['rank'] = i
                
                for key, value in formatted_item.items():
                    if isinstance(value, (int, float)):
                        if key.endswith('_percentage') or key.endswith('Rate'):
                            formatted_item[key] = f"{value:.1f}%"
                        elif isinstance(value, float):
                            formatted_item[key] = round(value, 2)
                formatted_rankings.append(formatted_item)
            return formatted_rankings
        except Exception as e:
            logger.error(f"格式化排行榜失败: {str(e)}")
            return rankings
    
    @staticmethod
    def calculate_team_form(recent_matches: List[str], match_count: int = 5) -> Dict[str, Any]:
        """计算球队近期状态"""
        if not recent_matches:
            return {
                'form': '',
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'points': 0,
                'win_rate': 0.0
            }
        
        recent = recent_matches[-match_count:]
        wins = recent.count('W')
        draws = recent.count('D')
        losses = recent.count('L')
        points = wins * 3 + draws * 1
        win_rate = StatsUtils.calculate_win_rate(wins, len(recent))
        
        return {
            'form': ''.join(recent),
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'points': points,
            'win_rate': win_rate
        }
    
    @staticmethod
    def generate_stats_summary(stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成统计摘要"""
        try:
            summary = {
                'total_records': 0,
                'categories': [],
                'highlights': [],
                'trends': []
            }
            
            for key, value in stats_data.items():
                if isinstance(value, list):
                    summary['total_records'] += len(value)
                    summary['categories'].append({'name': key, 'count': len(value)})
            
            # 添加射手王信息
            if 'topScorers' in stats_data and stats_data['topScorers'].get('players'):
                top_scorer = stats_data['topScorers']['players'][0]
                summary['highlights'].append(
                    f"射手王：{top_scorer['name']} ({top_scorer['goals']}球)"
                )
            
            # 添加积分榜领头羊信息
            if 'points' in stats_data and stats_data['points']:
                leader = stats_data['points'][0]
                summary['highlights'].append(
                    f"积分榜领头羊：{leader['team']} ({leader['points']}分)"
                )
            
            return summary
        except Exception as e:
            logger.error(f"生成统计摘要失败: {str(e)}")
            return {'error': '摘要生成失败'}
    
    @staticmethod
    def validate_stats_data(stats_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证统计数据"""
        errors = []
        try:
            required_fields = ['totalMatches', 'completedMatches', 'upcomingMatches']
            for field in required_fields:
                if field not in stats_data:
                    errors.append(f"缺少必要字段: {field}")
                elif not isinstance(stats_data[field], (int, float)):
                    errors.append(f"字段 {field} 必须是数字")
                elif stats_data[field] < 0:
                    errors.append(f"字段 {field} 不能为负数")
            
            if all(field in stats_data for field in required_fields):
                total = stats_data['totalMatches']
                completed = stats_data['completedMatches']
                upcoming = stats_data['upcomingMatches']
                
                if completed + upcoming > total:
                    errors.append("已完成比赛数 + 即将进行比赛数 不能大于总比赛数")
            
            return len(errors) == 0, errors
        except Exception as e:
            logger.error(f"验证统计数据失败: {str(e)}")
            return False, [f"验证过程出错: {str(e)}"]
    
    @staticmethod
    def convert_stats_to_chart_data(stats_data: Dict[str, Any], 
                                   chart_type: str = 'bar') -> Dict[str, Any]:
        """转换统计数据为图表数据"""
        try:
            if chart_type == 'bar':
                return StatsUtils._convert_to_bar_chart(stats_data)
            elif chart_type == 'pie':
                return StatsUtils._convert_to_pie_chart(stats_data)
            elif chart_type == 'line':
                return StatsUtils._convert_to_line_chart(stats_data)
            else:
                raise ValueError(f"不支持的图表类型: {chart_type}")
        except Exception as e:
            logger.error(f"转换图表数据失败: {str(e)}")
            return {'error': '图表数据转换失败'}
    
    @staticmethod
    def _convert_to_bar_chart(stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """转换为柱状图数据"""
        if 'points' in stats_data:
            labels = [team['team'] for team in stats_data['points'][:10]]
            data = [team['points'] for team in stats_data['points'][:10]]
            
            return {
                'type': 'bar',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': '积分',
                        'data': data,
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                        'borderColor': 'rgba(54, 162, 235, 1)',
                        'borderWidth': 1
                    }]
                }
            }
        return {'error': '无法生成柱状图数据'}
    
    @staticmethod
    def _convert_to_pie_chart(stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """转换为饼图数据"""
        if all(key in stats_data for key in ['totalMatches', 'completedMatches', 'upcomingMatches']):
            return {
                'type': 'pie',
                'data': {
                    'labels': ['已完成', '即将进行', '其他'],
                    'datasets': [{
                        'data': [
                            stats_data['completedMatches'],
                            stats_data['upcomingMatches'],
                            stats_data['totalMatches'] - stats_data['completedMatches'] - stats_data['upcomingMatches']
                        ],
                        'backgroundColor': [
                            'rgba(75, 192, 192, 0.2)',
                            'rgba(255, 206, 86, 0.2)',
                            'rgba(255, 99, 132, 0.2)'
                        ]
                    }]
                }
            }
        return {'error': '无法生成饼图数据'}
    
    @staticmethod
    def _convert_to_line_chart(stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """转换为折线图数据"""
        return {'type': 'line', 'data': {'labels': [], 'datasets': []}}
    
    @staticmethod
    def export_stats_to_csv(stats_data: Dict[str, Any], 
                           filename: Optional[str] = None) -> str:
        """导出统计数据为CSV格式"""
        try:
            output = io.StringIO()
            
            # 导出积分榜数据
            if 'points' in stats_data and stats_data['points']:
                writer = csv.writer(output)
                headers = ['排名', '球队', '积分', '进球', '失球', '净胜球', '比赛场次']
                writer.writerow(headers)
                
                for i, team in enumerate(stats_data['points'], 1):
                    row = [
                        i,
                        team.get('team', ''),
                        team.get('points', 0),
                        team.get('goalsFor', 0),
                        team.get('goalsAgainst', 0),
                        team.get('goalDifference', 0),
                        team.get('matchesPlayed', 0)
                    ]
                    writer.writerow(row)
            
            content = output.getvalue()
            output.close()
            logger.info(f"成功导出CSV数据，长度: {len(content)}")
            return content
        except Exception as e:
            logger.error(f"导出CSV失败: {str(e)}")
            return "导出失败"
    
    @staticmethod
    def calculate_efficiency_metrics(stats_data: Dict[str, Any]) -> Dict[str, float]:
        """计算效率指标"""
        try:
            metrics = {}
            
            # 如果有积分榜数据
            if 'points' in stats_data and stats_data['points']:
                teams = stats_data['points']
                
                total_points = sum(team.get('points', 0) for team in teams)
                total_matches = sum(team.get('matchesPlayed', 0) for team in teams)
                
                if total_matches > 0:
                    metrics['avg_points_per_match'] = round(total_points / total_matches, 2)
                
                total_goals = sum(team.get('goalsFor', 0) for team in teams)
                if total_matches > 0:
                    metrics['avg_goals_per_match'] = round(total_goals / total_matches, 2)
                
                total_conceded = sum(team.get('goalsAgainst', 0) for team in teams)
                if total_matches > 0:
                    metrics['avg_conceded_per_match'] = round(total_conceded / total_matches, 2)
            
            return metrics
        except Exception as e:
            logger.error(f"计算效率指标失败: {str(e)}")
            return {}
    
    @staticmethod
    def generate_tournament_key(tournament_name: str) -> str:
        """生成赛事key（与服务层保持一致）"""
        return tournament_name.lower().replace(' ', '_').replace('-', '_')
    
    @staticmethod
    def calculate_team_participation_metrics(participation_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算球队参赛记录的基础指标"""
        matches_played = participation_data.get('matches_played', 0)
        wins = participation_data.get('wins', 0)
        draws = participation_data.get('draws', 0)
        losses = participation_data.get('losses', 0)
        goals_for = participation_data.get('goals_for', 0)
        goals_against = participation_data.get('goals_against', 0)
        points = participation_data.get('points', 0)
        
        return {
            'basic_stats': {
                'matches_played': matches_played,
                'wins': wins,
                'draws': draws,
                'losses': losses,
                'points': points,
                'rank': participation_data.get('rank')
            },
            'goal_stats': {
                'goals_for': goals_for,
                'goals_against': goals_against,
                'goal_difference': goals_for - goals_against
            },
            'discipline_stats': {
                'red_cards': participation_data.get('red_cards', 0),
                'yellow_cards': participation_data.get('yellow_cards', 0)
            },
            'performance_metrics': StatsUtils.calculate_performance_metrics(
                matches_played, wins, draws, losses, goals_for, goals_against, points
            )
        }
    
    @staticmethod
    def calculate_performance_metrics(matches_played: int, wins: int, draws: int, losses: int,
                                    goals_for: int, goals_against: int, points: int) -> Dict[str, float]:
        """计算性能指标"""
        if matches_played == 0:
            return {
                'win_rate': 0.0,
                'draw_rate': 0.0,
                'loss_rate': 0.0,
                'avg_goals_per_match': 0.0,
                'avg_goals_conceded_per_match': 0.0,
                'avg_goal_difference_per_match': 0.0,
                'points_per_match': 0.0
            }
        
        goal_difference = goals_for - goals_against
        return {
            'win_rate': round((wins / matches_played) * 100, 2),
            'draw_rate': round((draws / matches_played) * 100, 2),
            'loss_rate': round((losses / matches_played) * 100, 2),
            'avg_goals_per_match': round(goals_for / matches_played, 2),
            'avg_goals_conceded_per_match': round(goals_against / matches_played, 2),
            'avg_goal_difference_per_match': round(goal_difference / matches_played, 2),
            'points_per_match': round(points / matches_played, 2)
        }
    
    @staticmethod
    def calculate_overall_tournament_summary(tournament_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算多个赛事的总体统计摘要"""
        if not tournament_stats:
            return {}
        
        total_matches = sum(stats['basic_stats']['matches_played'] for stats in tournament_stats)
        total_wins = sum(stats['basic_stats']['wins'] for stats in tournament_stats)
        total_draws = sum(stats['basic_stats']['draws'] for stats in tournament_stats)
        total_losses = sum(stats['basic_stats']['losses'] for stats in tournament_stats)
        total_goals_for = sum(stats['goal_stats']['goals_for'] for stats in tournament_stats)
        total_goals_against = sum(stats['goal_stats']['goals_against'] for stats in tournament_stats)
        total_points = sum(stats['basic_stats']['points'] for stats in tournament_stats)
        
        return {
            'total_tournaments': len(tournament_stats),
            'total_matches': total_matches,
            'total_wins': total_wins,
            'total_draws': total_draws,
            'total_losses': total_losses,
            'total_goals_for': total_goals_for,
            'total_goals_against': total_goals_against,
            'total_goal_difference': total_goals_for - total_goals_against,
            'total_points': total_points,
            'overall_performance': StatsUtils.calculate_performance_metrics(
                total_matches, total_wins, total_draws, total_losses,
                total_goals_for, total_goals_against, total_points
            )
        }
