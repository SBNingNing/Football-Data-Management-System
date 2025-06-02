from app import db

class Tournament(db.Model):
    """赛事表 - 存储赛事信息"""
    __tablename__ = 'tournament'
    
    # 主键
    id = db.Column('赛事ID', db.Integer, primary_key=True, comment='赛事ID')
    
    # 赛事信息
    name = db.Column('赛事名称', db.String(100), nullable=False, comment='赛事名称')
    type = db.Column('赛事类型', db.String(50), nullable=False, comment='赛事类型(11人制、8人制等)')
    participant_type = db.Column('参赛单位类型', db.String(50), comment='参赛单位类型(学院、俱乐部等)')
    gender_restriction = db.Column('性别限制', db.String(1), default='U', comment='性别限制(M: 男，F: 女，U: 不限)')
    
    # 关系在其他模型中定义
    
    def __repr__(self):
        return f'<Tournament {self.name}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'participant_type': self.participant_type,
            'gender_restriction': self.gender_restriction
        }
