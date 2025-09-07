from app.database import db
from app.models.competition import Competition
from app.utils.logging_config import get_logger
from app.middleware.error_middleware import log_error
from sqlalchemy.exc import IntegrityError

logger = get_logger(__name__)


class CompetitionService:
    """竞赛业务服务类"""
    
    @staticmethod
    def get_all_competitions():
        """获取所有赛事"""
        try:
            competitions = Competition.query.all()
            logger.debug(f"Retrieved {len(competitions)} competitions")
            return [comp.to_dict() for comp in competitions], None
        except Exception as e:
            log_error(e, "Failed to get all competitions")
            return None, f'获取赛事列表失败: {str(e)}'
    
    @staticmethod
    def get_competition_by_id(competition_id):
        """根据ID获取赛事"""
        try:
            competition = Competition.query.get(competition_id)
            if not competition:
                logger.warning(f"Competition not found: {competition_id}")
                return None, '赛事不存在'
            
            logger.debug(f"Retrieved competition: {competition.name}")
            return competition.to_dict(), None
        except Exception as e:
            log_error(e, f"Failed to get competition: {competition_id}")
            return None, f'获取赛事信息失败: {str(e)}'
    
    @staticmethod
    def create_competition(name):
        """创建新赛事"""
        try:
            if not name or not name.strip():
                return None, '赛事名称不能为空'
            
            competition = Competition(name=name.strip())
            db.session.add(competition)
            db.session.commit()
            
            logger.info(f"Competition created: {name} (ID: {competition.competition_id})")
            return competition.to_dict(), None
            
        except IntegrityError:
            db.session.rollback()
            logger.warning(f"Competition name already exists: {name}")
            return None, '赛事名称已存在'
        except Exception as e:
            db.session.rollback()
            log_error(e, f"Failed to create competition: {name}")
            return None, f'创建赛事失败: {str(e)}'
    
    @staticmethod
    def update_competition(competition_id, data):
        """更新赛事信息"""
        try:
            competition = Competition.query.get(competition_id)
            if not competition:
                return None, '赛事不存在'
            
            if not data:
                return None, '请提供要更新的数据'
            
            # 更新字段
            if 'name' in data and data['name']:
                competition.name = data['name'].strip()
            
            db.session.commit()
            
            logger.info(f"Competition updated: {competition.name} (ID: {competition_id})")
            return competition.to_dict(), None
            
        except IntegrityError:
            db.session.rollback()
            logger.warning(f"Competition name conflict during update: {competition_id}")
            return None, '赛事名称已存在'
        except Exception as e:
            db.session.rollback()
            log_error(e, f"Failed to update competition: {competition_id}")
            return None, f'更新赛事失败: {str(e)}'
    
    @staticmethod
    def delete_competition(competition_id):
        """删除赛事"""
        try:
            competition = Competition.query.get(competition_id)
            if not competition:
                return None, '赛事不存在'
            
            # 检查关联数据
            if hasattr(competition, 'tournaments') and competition.tournaments:
                logger.warning(f"Cannot delete competition with tournaments: {competition_id}")
                return None, '该赛事下还有赛季实例，无法删除'
            
            competition_name = competition.name
            db.session.delete(competition)
            db.session.commit()
            
            logger.info(f"Competition deleted: {competition_name} (ID: {competition_id})")
            return True, None
            
        except Exception as e:
            db.session.rollback()
            log_error(e, f"Failed to delete competition: {competition_id}")
            return None, f'删除赛事失败: {str(e)}'
