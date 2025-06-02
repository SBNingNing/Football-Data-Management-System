from app import db
from datetime import datetime

class Season(db.Model):
    """赛季表 - 存储赛季信息"""
    __tablename__ = 'season'
    
    # 主键
    id = db.Column('赛季ID', db.Integer, primary_key=True, comment='赛季ID')
    
    # 赛季信息
    name = db.Column('赛季名称', db.String(100), nullable=False, comment='赛季名称')
    start_time = db.Column('赛季开始时间', db.DateTime, nullable=False, comment='赛季开始时间')
    end_time = db.Column('赛季结束时间', db.DateTime, nullable=False, comment='赛季结束时间')
    
    # 关系在其他模型中定义
    
    def __repr__(self):
        return f'<Season {self.name}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }
