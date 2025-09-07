"""
赛季工具函数 - 提供赛季相关的通用工具函数
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from calendar import monthrange

from app.utils.logger import get_logger

logger = get_logger(__name__)


class SeasonUtils:
    """赛季工具类"""
    
    @staticmethod
    def format_season_display_name(season_name: str, start_time: datetime, end_time: datetime) -> str:
        """格式化赛季显示名称"""
        start_year = start_time.year
        end_year = end_time.year
        
        if start_year == end_year:
            return f"{season_name} ({start_year})"
        else:
            return f"{season_name} ({start_year}-{end_year})"
    
    @staticmethod
    def calculate_season_duration(start_time: datetime, end_time: datetime) -> Dict[str, int]:
        """计算赛季持续时间"""
        duration = end_time - start_time
        days = duration.days
        weeks = days // 7
        months = SeasonUtils._calculate_months_between(start_time, end_time)
        
        return {
            'days': days,
            'weeks': weeks,
            'months': months
        }
    
    @staticmethod
    def _calculate_months_between(start_date: datetime, end_date: datetime) -> int:
        """计算两个日期之间的月数"""
        return (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
    
    @staticmethod
    def get_season_progress(start_time: datetime, end_time: datetime, 
                          current_time: Optional[datetime] = None) -> Dict[str, Any]:
        """获取赛季进度信息"""
        if current_time is None:
            current_time = datetime.now()
        
        total_duration = end_time - start_time
        
        if current_time < start_time:
            # 赛季未开始
            status = 'not_started'
            progress_percentage = 0.0
            remaining_days = (start_time - current_time).days
        elif current_time > end_time:
            # 赛季已结束
            status = 'finished'
            progress_percentage = 100.0
            remaining_days = 0
        else:
            # 赛季进行中
            status = 'ongoing'
            elapsed_duration = current_time - start_time
            progress_percentage = (elapsed_duration.total_seconds() / total_duration.total_seconds()) * 100
            remaining_days = (end_time - current_time).days
        
        return {
            'status': status,
            'progress_percentage': round(progress_percentage, 2),
            'remaining_days': remaining_days,
            'total_days': total_duration.days
        }
    
    @staticmethod
    def validate_season_time_range(start_time: datetime, end_time: datetime) -> Tuple[bool, Optional[str]]:
        """验证赛季时间范围的合理性"""
        # 检查开始时间是否早于结束时间
        if start_time >= end_time:
            return False, '开始时间必须早于结束时间'
        
        # 检查赛季是否过短（少于1天）
        duration = end_time - start_time
        if duration.days < 1:
            return False, '赛季持续时间不能少于1天'
        
        # 检查赛季是否过长（超过2年）
        if duration.days > 730:
            return False, '赛季持续时间不能超过2年'
        
        # 检查是否在合理的未来时间范围内（不超过10年）
        current_time = datetime.now()
        if start_time > current_time + timedelta(days=3650):
            return False, '赛季开始时间不能超过10年后'
        
        return True, None
    
    @staticmethod
    def generate_season_calendar(start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """生成赛季日历信息"""
        calendar = []
        current_date = start_time.replace(day=1)  # 从月初开始
        
        while current_date <= end_time:
            month_days = monthrange(current_date.year, current_date.month)[1]
            month_end = current_date.replace(day=month_days)
            
            # 计算该月在赛季中的实际天数
            actual_start = max(current_date, start_time)
            actual_end = min(month_end, end_time)
            
            if actual_start <= actual_end:
                season_days = (actual_end - actual_start).days + 1
                
                calendar.append({
                    'year': current_date.year,
                    'month': current_date.month,
                    'month_name': current_date.strftime('%B'),
                    'total_days': month_days,
                    'season_days': season_days,
                    'start_date': actual_start.strftime('%Y-%m-%d'),
                    'end_date': actual_end.strftime('%Y-%m-%d')
                })
            
            # 移动到下个月
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return calendar
    
    @staticmethod
    def suggest_season_name(start_time: datetime, end_time: datetime) -> str:
        """根据时间范围建议赛季名称"""
        start_year = start_time.year
        end_year = end_time.year
        start_month = start_time.month
        
        # 根据开始月份判断赛季类型
        if start_month in [9, 10, 11]:  # 秋季开始
            if start_year == end_year:
                return f"{start_year}秋季赛"
            else:
                return f"{start_year}-{end_year}赛季"
        elif start_month in [3, 4, 5]:  # 春季开始
            return f"{start_year}春季赛"
        elif start_month in [6, 7, 8]:  # 夏季开始
            return f"{start_year}夏季赛"
        elif start_month in [12, 1, 2]:  # 冬季开始
            if start_month == 12:
                return f"{start_year}-{end_year}冬季赛"
            else:
                return f"{start_year}冬季赛"
        else:
            # 默认命名
            if start_year == end_year:
                return f"{start_year}赛季"
            else:
                return f"{start_year}-{end_year}赛季"
    
    @staticmethod
    def get_overlapping_seasons_info(seasons_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """检查赛季之间的重叠情况"""
        overlaps = []
        
        for i, season1 in enumerate(seasons_data):
            for j, season2 in enumerate(seasons_data[i+1:], i+1):
                start1 = datetime.fromisoformat(season1['start_time'])
                end1 = datetime.fromisoformat(season1['end_time'])
                start2 = datetime.fromisoformat(season2['start_time'])
                end2 = datetime.fromisoformat(season2['end_time'])
                
                # 检查重叠
                if start1 < end2 and start2 < end1:
                    overlap_start = max(start1, start2)
                    overlap_end = min(end1, end2)
                    overlap_days = (overlap_end - overlap_start).days + 1
                    
                    overlaps.append({
                        'season1_id': season1['id'],
                        'season1_name': season1['name'],
                        'season2_id': season2['id'],
                        'season2_name': season2['name'],
                        'overlap_start': overlap_start.strftime('%Y-%m-%d'),
                        'overlap_end': overlap_end.strftime('%Y-%m-%d'),
                        'overlap_days': overlap_days
                    })
        
        return overlaps
    
    @staticmethod
    def format_season_summary(season_data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化赛季摘要信息"""
        try:
            start_time = datetime.fromisoformat(season_data['start_time'])
            end_time = datetime.fromisoformat(season_data['end_time'])
            
            duration_info = SeasonUtils.calculate_season_duration(start_time, end_time)
            progress_info = SeasonUtils.get_season_progress(start_time, end_time)
            display_name = SeasonUtils.format_season_display_name(
                season_data['name'], start_time, end_time
            )
            
            return {
                'id': season_data['id'],
                'name': season_data['name'],
                'display_name': display_name,
                'start_time': season_data['start_time'],
                'end_time': season_data['end_time'],
                'duration': duration_info,
                'progress': progress_info,
                'created_at': season_data.get('created_at'),
                'updated_at': season_data.get('updated_at')
            }
            
        except Exception as e:
            logger.error(f"格式化赛季摘要失败: {str(e)}")
            return season_data  # 返回原始数据
