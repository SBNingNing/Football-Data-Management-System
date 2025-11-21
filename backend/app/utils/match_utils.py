"""
比赛模块工具类
提供日期解析、比赛类型判断、数据格式化等工具函数
"""

from datetime import datetime
import pytz
from typing import Optional, Dict, Any, List
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MatchUtils:
    """比赛工具类"""
    
    # 状态映射
    STATUS_MAP = {
        'P': '未开始',
        'F': '已完赛'
    }
    
    # 反向状态映射（支持多种前端格式）
    REVERSE_STATUS_MAP = {
        '未开始': 'P',
        '已完赛': 'F',
        # 兼容英文状态值
        'pending': 'P',
        'completed': 'F',
        # 兼容其他可能的状态值
        '待进行': 'P',
        'P': 'P',
        'F': 'F'
    }
    


    @staticmethod
    def parse_date_from_frontend(date_input: Any) -> Optional[datetime]:
        """解析前端传来的日期格式，并转换为北京时间"""
        if not date_input:
            return None

        date_str = str(date_input).strip()

        # 检查是否包含无效字符或占位符
        invalid_patterns = ['yyyy', 'MM', 'dd', 'We', 'placeholder']
        if any(pattern in date_str for pattern in invalid_patterns):
            raise ValueError('日期格式无效，请重新选择日期')

        # 如果是时间戳（毫秒或秒）
        if date_str.isdigit():
            timestamp = int(date_str)
            # 判断是毫秒还是秒
            if timestamp > 10000000000:  # 毫秒时间戳
                dt = datetime.fromtimestamp(timestamp / 1000)
            else:  # 秒时间戳
                dt = datetime.fromtimestamp(timestamp)
            # 转为北京时间
            sh_tz = pytz.timezone('Asia/Shanghai')
            dt = dt.replace(tzinfo=pytz.UTC).astimezone(sh_tz).replace(tzinfo=None)
            return dt

        # 常见的前端日期格式
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',     # 2024-01-01T10:00:00.000Z
            '%Y-%m-%dT%H:%M:%SZ',        # 2024-01-01T10:00:00Z
            '%Y-%m-%dT%H:%M:%S',         # 2024-01-01T10:00:00
            '%Y-%m-%d %H:%M:%S',         # 2024-01-01 10:00:00
            '%Y-%m-%d %H:%M',            # 2024-01-01 10:00
            '%Y-%m-%d',                  # 2024-01-01
            '%Y/%m/%d %H:%M:%S',         # 2024/01/01 10:00:00
            '%Y/%m/%d %H:%M',            # 2024/01/01 10:00
            '%Y/%m/%d',                  # 2024/01/01
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                # 只要不是Z结尾的，都是本地时间，直接转为北京时间
                sh_tz = pytz.timezone('Asia/Shanghai')
                dt = sh_tz.localize(dt).replace(tzinfo=None)
                return dt
            except ValueError:
                continue

        # 尝试使用 fromisoformat（Python 3.7+）
        try:
            clean_date = date_str.replace('Z', '').replace('+00:00', '')
            dt = datetime.fromisoformat(clean_date)
            sh_tz = pytz.timezone('Asia/Shanghai')
            dt = sh_tz.localize(dt).replace(tzinfo=None)
            return dt
        except ValueError:
            pass

        raise ValueError(f'无法解析日期格式: {date_str}')

    @staticmethod
    def determine_match_type(tournament) -> str:
        """根据赛事名称确定matchType"""
        if tournament and tournament.competition:
            return tournament.competition.name
            
        if tournament:
            return tournament.name
        else:
            return '未知赛事'

    @staticmethod
    def format_match_time(match_time: Optional[datetime]) -> Optional[str]:
        """格式化比赛时间为标准字符串"""
        return match_time.strftime('%Y-%m-%d %H:%M:%S') if match_time else None

    @staticmethod
    def format_match_date_iso(match_time: Optional[datetime]) -> str:
        """格式化比赛时间为ISO格式"""
        return match_time.isoformat() if match_time else ''

    @staticmethod
    def get_tournament_id_by_type(match_type: str) -> int:
        """根据比赛类型获取赛事ID"""
        # 已废弃，不再使用硬编码映射
        raise NotImplementedError("get_tournament_id_by_type is deprecated. Use dynamic lookup instead.")

    @staticmethod
    def get_tournament_id_by_frontend_type(match_type: str) -> Optional[int]:
        """根据前端比赛类型获取赛事ID"""
        # 已废弃
        return None

    @staticmethod
    def get_status_text(status: str) -> str:
        """获取状态中文描述"""
        return MatchUtils.STATUS_MAP.get(status, '待开始')

    @staticmethod
    def get_status_code(status_text: str) -> Optional[str]:
        """根据中文状态获取状态代码"""
        return MatchUtils.REVERSE_STATUS_MAP.get(status_text)

    @staticmethod
    def generate_match_id(tournament_id: int, existing_count: int) -> str:
        """生成比赛ID"""
        return f"M{tournament_id}{existing_count + 1:03d}"

    @staticmethod
    def safe_int_conversion(value: Any, default: int = 0) -> int:
        """安全的整数转换"""
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    @staticmethod
    def build_match_dict_basic(match) -> Dict[str, Any]:
        """构建基础比赛字典"""
        match_dict = match.to_dict()
        match_dict['matchName'] = match_dict['match_name']
        match_dict['team1'] = match.home_team.team_base.name if match.home_team and match.home_team.team_base else ''
        match_dict['team2'] = match.away_team.team_base.name if match.away_team and match.away_team.team_base else ''
        match_dict['date'] = MatchUtils.format_match_time(match.match_time)
        match_dict['home_score'] = match.home_score if match.home_score is not None else 0
        match_dict['away_score'] = match.away_score if match.away_score is not None else 0
        match_dict['status'] = MatchUtils.get_status_text(match.status)
        return match_dict

    @staticmethod
    def build_match_dict_with_type(match, tournament) -> Dict[str, Any]:
        """构建包含比赛类型的比赛字典"""
        match_dict = MatchUtils.build_match_dict_basic(match)
        match_dict['matchType'] = MatchUtils.determine_match_type(tournament)
        return match_dict

    @staticmethod
    def validate_match_data(data: Dict[str, Any]) -> List[str]:
        """验证比赛数据"""
        errors = []
        
        # 验证比赛名称
        if not data.get('matchName'):
            errors.append('缺少必要字段: matchName')

        # 验证主队 (兼容 team1 和 homeTeamId)
        if not (data.get('team1') or data.get('homeTeamId')):
            errors.append('缺少必要字段: homeTeamId')

        # 验证客队 (兼容 team2 和 awayTeamId)
        if not (data.get('team2') or data.get('awayTeamId')):
            errors.append('缺少必要字段: awayTeamId')

        # 验证时间 (兼容 date 和 matchTime)
        if not (data.get('date') or data.get('matchTime')):
            errors.append('缺少必要字段: matchTime')

        # 验证地点
        if not data.get('location'):
            errors.append('缺少必要字段: location')
        
        return errors

    @staticmethod
    def calculate_team_statistics(events: List, team_id: int) -> Dict[str, int]:
        """计算球队在比赛中的统计数据"""
        stats = {
            'goals': 0,
            'own_goals': 0,
            'yellow_cards': 0,
            'red_cards': 0
        }
        
        for event in events:
            if event.team_id == team_id:
                if event.event_type == '进球':
                    stats['goals'] += 1
                elif event.event_type == '乌龙球':
                    stats['own_goals'] += 1
                elif event.event_type == '黄牌':
                    stats['yellow_cards'] += 1
                elif event.event_type == '红牌':
                    stats['red_cards'] += 1
        
        return stats

    @staticmethod
    def calculate_score_from_events(events: List, home_team_id: int, away_team_id: int) -> tuple:
        """从事件中计算比分（包括乌龙球）"""
        home_score = 0
        away_score = 0
        
        for event in events:
            if event.event_type == '进球':
                if event.team_id == home_team_id:
                    home_score += 1
                elif event.team_id == away_team_id:
                    away_score += 1
            elif event.event_type == '乌龙球':
                # 乌龙球计入对方得分
                if event.team_id == home_team_id:
                    away_score += 1
                elif event.team_id == away_team_id:
                    home_score += 1
        
        return home_score, away_score

    @staticmethod
    def log_match_operation(operation: str, match_id: str, details: str = ""):
        """记录比赛操作日志"""
        logger.info(f"比赛操作 - {operation}: 比赛ID={match_id}, 详情={details}")