from app import db

class Player(db.Model):
    """球员表 - 存储球员信息"""
    __tablename__ = 'player'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, comment='球员ID')
    
    # 球员信息
    name = db.Column(db.String(100), nullable=False, comment='球员姓名')
    gender = db.Column(db.String(1), nullable=False, comment='性别(M/F)')
    
    # 外键关系
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), comment='球队ID')
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), comment='赛季ID')
    
    # 统计数据
    goals_season = db.Column(db.Integer, default=0, comment='赛季进球数')
    cards_season = db.Column(db.Integer, default=0, comment='赛季红黄牌数')
    goals_history = db.Column(db.Integer, default=0, comment='历史进球数')
    cards_history = db.Column(db.Integer, default=0, comment='历史红黄牌数')
    
    # 关系
    team = db.relationship('Team', backref=db.backref('players', lazy=True))
    season = db.relationship('Season', backref=db.backref('players', lazy=True))
    events = db.relationship('Event', backref=db.backref('player', lazy=True), 
                            foreign_keys='Event.player_id')
    
    def __repr__(self):
        return f'<Player {self.name}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'team_id': self.team_id,
            'team_name': self.team.name if self.team else None,
            'season_id': self.season_id,
            'goals_season': self.goals_season,
            'cards_season': self.cards_season,
            'goals_history': self.goals_history,
            'cards_history': self.cards_history
        }
