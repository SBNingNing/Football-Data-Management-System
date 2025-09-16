"""
竞赛工具函数模块
提供竞赛相关的工具函数和数据处理功能
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

from app.utils.logger import get_logger

logger = get_logger(__name__)


class CompetitionUtils:
    """竞赛工具函数类"""
    
    @staticmethod
    def format_competition_name(name: str) -> str:
        """格式化竞赛名称"""
        if not name:
            return ""
        
        # 去除首尾空格并标准化
        formatted_name = name.strip()
        formatted_name = re.sub(r'\s+', ' ', formatted_name)
        
        # 首字母大写处理（如果是英文）
        if re.match(r'^[a-zA-Z]', formatted_name):
            formatted_name = formatted_name.title()
        
        return formatted_name
    
    @staticmethod
    def validate_competition_name(name: str) -> tuple[bool, str]:
        """验证竞赛名称是否符合规则"""
        if not name or not name.strip():
            return False, "竞赛名称不能为空"
        
        name = name.strip()
        
        if len(name) < 2:
            return False, "竞赛名称至少需要2个字符"
        
        if len(name) > 100:
            return False, "竞赛名称不能超过100个字符"
        
        # 字符检查 - 允许中文、英文、数字、空格、常用标点
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9\s\-_()（）]+$', name):
            return False, "竞赛名称只能包含中文、英文、数字、空格和常用标点符号"
        
        # 不能全是空格或特殊字符
        if re.match(r'^[\s\-_()（）]+$', name):
            return False, "竞赛名称不能只包含空格或标点符号"
        
        return True, ""
    
    @staticmethod
    def generate_competition_slug(name: str) -> str:
        """生成竞赛的URL友好标识符"""
        if not name:
            return ""
        
        # 转换为小写
        slug = name.lower().strip()
        
        # 替换中文和特殊字符为连字符
        slug = re.sub(r'[\u4e00-\u9fa5\s\-_()（）]+', '-', slug)
        
        # 只保留字母、数字和连字符
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        
        # 去除多余的连字符
        slug = re.sub(r'-+', '-', slug)
        
        # 去除首尾连字符
        slug = slug.strip('-')
        
        return slug or "competition"
    
    @staticmethod
    def format_competition_response(competition_data: Optional[Dict[str, Any]], 
                                  message: str = None) -> Dict[str, Any]:
        """格式化竞赛响应数据"""
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
        
        if message:
            response['message'] = message
        
        if competition_data:
            response['data'] = competition_data
        
        return response
    
    @staticmethod
    def format_error_response(error_message: str, 
                            error_code: str = None) -> Dict[str, Any]:
        """格式化错误响应数据"""
        response = {
            'status': 'error',
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        }
        
        if error_code:
            response['error_code'] = error_code
        
        return response
    
    @staticmethod
    def build_competition_dict(competition) -> Dict[str, Any]:
        """构建竞赛字典数据"""
        if not competition:
            return {}
        
        return {
            'competition_id': competition.competition_id,
            'name': competition.name,
            'slug': CompetitionUtils.generate_competition_slug(competition.name),
            'formatted_name': CompetitionUtils.format_competition_name(competition.name),
            'tournament_count': len(competition.tournaments) if hasattr(competition, 'tournaments') else 0,
            'created_at': datetime.now().isoformat()  # 如果模型有创建时间字段可以使用实际值
        }
    
    @staticmethod
    def sort_competitions(competitions: List[Dict[str, Any]], 
                         sort_by: str = 'name') -> List[Dict[str, Any]]:
        """对竞赛列表进行排序"""
        if not competitions:
            return []
        
        try:
            if sort_by == 'name':
                return sorted(competitions, key=lambda x: x.get('name', ''))
            elif sort_by == 'id':
                return sorted(competitions, key=lambda x: x.get('competition_id', 0))
            elif sort_by == 'tournament_count':
                return sorted(competitions, key=lambda x: x.get('tournament_count', 0), reverse=True)
            else:
                logger.warning(f"Unknown sort field: {sort_by}, using default 'name'")
                return sorted(competitions, key=lambda x: x.get('name', ''))
        except Exception as e:
            logger.error(f"Error sorting competitions: {e}")
            return competitions
    
    @staticmethod
    def filter_competitions(competitions: List[Dict[str, Any]], 
                          search_term: str = None) -> List[Dict[str, Any]]:
        """过滤竞赛列表"""
        if not competitions:
            return []
        
        if not search_term:
            return competitions
        
        search_term = search_term.lower().strip()
        
        filtered = []
        for competition in competitions:
            name = competition.get('name', '').lower()
            if search_term in name:
                filtered.append(competition)
        
        return filtered
    
    @staticmethod
    def get_competition_statistics(competitions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取竞赛统计信息"""
        if not competitions:
            return {
                'total_competitions': 0,
                'total_tournaments': 0,
                'average_tournaments_per_competition': 0
            }
        
        total_competitions = len(competitions)
        total_tournaments = sum(comp.get('tournament_count', 0) for comp in competitions)
        average_tournaments = round(total_tournaments / total_competitions, 2) if total_competitions > 0 else 0
        
        return {
            'total_competitions': total_competitions,
            'total_tournaments': total_tournaments,
            'average_tournaments_per_competition': average_tournaments,
            'most_active_competition': max(competitions, key=lambda x: x.get('tournament_count', 0)) if competitions else None
        }
