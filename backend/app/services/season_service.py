"""
赛季服务层 - 处理赛季相关的业务逻辑
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.database import db
from app.models.season import Season
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SeasonService:
    """赛季业务逻辑服务类"""
    
    @staticmethod
    def get_all_seasons() -> List[Dict[str, Any]]:
        """获取所有赛季信息"""
        try:
            logger.info("开始获取所有赛季信息")
            seasons = Season.query.order_by(Season.start_time.desc()).all()
            
            result = [season.to_dict() for season in seasons]
            logger.info(f"成功获取 {len(result)} 个赛季信息")
            
            return result
            
        except Exception as e:
            logger.error(f"获取赛季列表失败: {str(e)}")
            raise
    
    @staticmethod
    def get_season_by_id(season_id: int) -> Dict[str, Any]:
        """根据ID获取单个赛季信息"""
        try:
            logger.info(f"开始获取赛季信息: {season_id}")
            season = Season.query.get_or_404(season_id)
            
            result = season.to_dict()
            logger.info(f"成功获取赛季信息: {season.name}")
            
            return result
            
        except Exception as e:
            logger.error(f"获取赛季信息失败: {str(e)}")
            raise
    
    @staticmethod
    def create_season(season_data: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """创建新赛季"""
        try:
            logger.info(f"开始创建赛季: {season_data.get('name', 'Unknown')}")
            
            # 解析和验证时间
            start_time = SeasonService._parse_datetime(season_data['start_time'])
            end_time = SeasonService._parse_datetime(season_data['end_time'])
            
            if start_time >= end_time:
                raise ValueError('开始时间必须早于结束时间')
            
            season = Season(
                name=season_data['name'],
                start_time=start_time,
                end_time=end_time
            )
            
            db.session.add(season)
            db.session.commit()
            
            # 直接获取ID，SQLAlchemy通常会在commit后自动回填
            season_id = season.season_id
            logger.info(f"成功创建赛季: {season.name} (ID: {season_id})")
            return season.to_dict(), '赛季创建成功'
            
        except IntegrityError:
            db.session.rollback()
            logger.warning(f"赛季名称已存在: {season_data.get('name', 'Unknown')}")
            raise ValueError('赛季名称已存在')
        except ValueError as e:
            logger.warning(f"赛季数据验证失败: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"创建赛季失败: {str(e)}\n详细堆栈: {error_details}")
            # 抛出包含更多信息的错误，以便前端能看到
            raise Exception(f"{str(e)} (Type: {type(e).__name__})")
    
    @staticmethod
    def update_season(season_id: int, update_data: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """更新赛季信息"""
        try:
            logger.info(f"开始更新赛季: {season_id}")
            season = Season.query.get_or_404(season_id)
            original_name = season.name
            
            # 更新字段
            if 'name' in update_data:
                season.name = update_data['name']
            
            if 'start_time' in update_data:
                season.start_time = SeasonService._parse_datetime(update_data['start_time'])
            
            if 'end_time' in update_data:
                season.end_time = SeasonService._parse_datetime(update_data['end_time'])
            
            # 验证时间逻辑
            if season.start_time >= season.end_time:
                raise ValueError('开始时间必须早于结束时间')
            
            db.session.commit()
            
            logger.info(f"成功更新赛季: {original_name} -> {season.name}")
            return season.to_dict(), '赛季更新成功'
            
        except IntegrityError:
            db.session.rollback()
            logger.warning(f"赛季名称已存在: {update_data.get('name', 'Unknown')}")
            raise IntegrityError('赛季名称已存在', None, None)
        except ValueError as e:
            logger.warning(f"赛季数据验证失败: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新赛季失败: {str(e)}")
            raise
    
    @staticmethod
    def delete_season(season_id: int) -> str:
        """删除赛季"""
        try:
            logger.info(f"开始删除赛季: {season_id}")
            season = Season.query.get_or_404(season_id)
            season_name = season.name
            
            # 检查关联数据
            if season.tournaments:
                raise ValueError('该赛季下还有赛事实例，无法删除')
            
            db.session.delete(season)
            db.session.commit()
            
            logger.info(f"成功删除赛季: {season_name}")
            return '赛季删除成功'
            
        except ValueError as e:
            logger.warning(f"删除赛季失败: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除赛季失败: {str(e)}")
            raise
    
    @staticmethod
    def _parse_datetime(datetime_str: str) -> datetime:
        """解析时间字符串"""
        try:
            # 处理 ISO 8601 格式时间
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            raise ValueError('时间格式无效')
    
    @staticmethod
    def get_seasons_by_date_range(start_date: Optional[datetime] = None, 
                                 end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """根据日期范围获取赛季"""
        try:
            logger.info(f"按日期范围查询赛季: {start_date} - {end_date}")
            
            query = Season.query
            
            if start_date:
                query = query.filter(Season.end_time >= start_date)
            
            if end_date:
                query = query.filter(Season.start_time <= end_date)
            
            seasons = query.order_by(Season.start_time.desc()).all()
            
            result = [season.to_dict() for season in seasons]
            logger.info(f"查询到 {len(result)} 个符合条件的赛季")
            
            return result
            
        except Exception as e:
            logger.error(f"按日期范围查询赛季失败: {str(e)}")
            raise
    
    @staticmethod
    def check_season_overlap(start_time: datetime, end_time: datetime, 
                           exclude_id: Optional[int] = None) -> bool:
        """检查赛季时间是否重叠"""
        try:
            query = Season.query.filter(
                Season.start_time < end_time,
                Season.end_time > start_time
            )
            
            if exclude_id:
                query = query.filter(Season.id != exclude_id)
            
            overlapping_seasons = query.first()
            
            return overlapping_seasons is not None
            
        except Exception as e:
            logger.error(f"检查赛季时间重叠失败: {str(e)}")
            raise
