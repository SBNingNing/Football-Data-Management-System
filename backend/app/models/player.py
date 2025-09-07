from app.database import db

class Player(db.Model):
    """球员表 - 存储球员基本信息"""
    __tablename__ = 'player'
    
    # 主键 - 使用学号
    id = db.Column('球员ID', db.String(20), primary_key=True, comment='球员ID(学号)')
    
    # 球员信息
    name = db.Column('球员姓名', db.String(50), nullable=False, comment='球员姓名')
    
    # 职业生涯统计数据
    career_goals = db.Column('职业生涯总进球数', db.Integer, default=0, comment='职业生涯总进球数')
    career_red_cards = db.Column('职业生涯总红牌数', db.Integer, default=0, comment='职业生涯总红牌数')
    career_yellow_cards = db.Column('职业生涯总黄牌数', db.Integer, default=0, comment='职业生涯总黄牌数')
    
    # 关系
    team_histories = db.relationship('PlayerTeamHistory', back_populates='player')
    events = db.relationship('Event', back_populates='player', lazy='dynamic')
    
    # 约束 - 匹配SQL定义
    __table_args__ = (
        db.CheckConstraint('职业生涯总进球数 >= 0', name='player_chk_1'),
        db.CheckConstraint('职业生涯总红牌数 >= 0', name='player_chk_2'),
        db.CheckConstraint('职业生涯总黄牌数 >= 0', name='player_chk_3'),
    )
    
    def __repr__(self):
        return f'<Player {self.id}: {self.name}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'career_goals': self.career_goals,
            'career_red_cards': self.career_red_cards,
            'career_yellow_cards': self.career_yellow_cards
        }
