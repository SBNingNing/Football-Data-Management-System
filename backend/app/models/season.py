from app import db
from datetime import datetime

class Season(db.Model):
    """赛季表 - 存储赛季信息"""
    __tablename__ = 'season'
    
    # 主键
    season_id = db.Column('season_id', db.Integer, primary_key=True, comment='赛季ID')
    
    # 赛季信息
    name = db.Column('赛季名称', db.String(50), nullable=False, unique=True, comment='赛季名称')
    start_time = db.Column('开始时间', db.DateTime, nullable=False, comment='开始时间')
    end_time = db.Column('结束时间', db.DateTime, nullable=False, comment='结束时间')
    
    # 关系
    tournaments = db.relationship('Tournament', back_populates='season', lazy=True)
    
    def __repr__(self):
        return f'<Season {self.name}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'season_id': self.season_id,
            'name': self.name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }
