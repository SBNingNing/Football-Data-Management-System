from app import db
from datetime import datetime

class Tournament(db.Model):
    """赛事表 - 存储赛事信息（合并了赛季信息）"""
    __tablename__ = 'tournament'
    
    # 主键
    id = db.Column('赛事ID', db.Integer, primary_key=True, comment='赛事ID')
    
    # 赛事信息
    name = db.Column('赛事名称', db.String(100), nullable=False, comment='赛事名称')
    type = db.Column('赛事类型', db.String(50), nullable=False, comment='赛事类型')
    season_name = db.Column('赛季名称', db.String(50), nullable=False, comment='赛季名称')
    is_grouped = db.Column('是否分组', db.Boolean, default=False, comment='是否需要分组进行')
    season_start_time = db.Column('赛季开始时间', db.DateTime, nullable=False, comment='赛季开始时间')
    season_end_time = db.Column('赛季结束时间', db.DateTime, nullable=False, comment='赛季结束时间')
    
    def __repr__(self):
        return f'<Tournament {self.name}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'season_name': self.season_name,
            'is_grouped': self.is_grouped,
            'season_start_time': self.season_start_time.isoformat() if self.season_start_time else None,
            'season_end_time': self.season_end_time.isoformat() if self.season_end_time else None
        }
