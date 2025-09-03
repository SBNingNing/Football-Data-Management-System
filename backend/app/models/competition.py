from app import db

class Competition(db.Model):
    """赛事表 - 存储赛事信息"""
    __tablename__ = 'competition'
    
    # 主键
    competition_id = db.Column('competition_id', db.Integer, primary_key=True, comment='赛事ID')
    
    # 赛事信息
    name = db.Column('赛事名称', db.String(100), nullable=False, unique=True, comment='赛事名称')
    
    # 关系
    tournaments = db.relationship('Tournament', back_populates='competition', lazy=True)
    
    def __repr__(self):
        return f'<Competition {self.name}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'competition_id': self.competition_id,
            'name': self.name
        }
