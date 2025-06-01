from app import db

class Team(db.Model):
    """球队表 - 存储球队信息"""
    __tablename__ = 'team'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, comment='球队ID')
    
    # 球队信息
    name = db.Column(db.String(100), nullable=False, comment='球队名称')
    
    # 外键关系
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), comment='赛事ID')
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), comment='赛季ID')
    
    # 统计数据
    goals_season = db.Column(db.Integer, default=0, comment='赛季总进球数')
    yellow_cards_season = db.Column(db.Integer, default=0, comment='赛季黄牌数')
    red_cards_season = db.Column(db.Integer, default=0, comment='赛季红牌数')
    points_season = db.Column(db.Integer, default=0, comment='赛季积分')
    rank_season = db.Column(db.Integer, comment='赛季排名')
    goals_history = db.Column(db.Integer, default=0, comment='历史总进球数')
    yellow_cards_history = db.Column(db.Integer, default=0, comment='历史总黄牌数')
    red_cards_history = db.Column(db.Integer, default=0, comment='历史总红牌数')
    
    # 关系（Match关系在Match模型中定义，避免循环引用）
    tournament = db.relationship('Tournament', backref=db.backref('teams', lazy=True))
    season = db.relationship('Season', backref=db.backref('teams', lazy=True))
    events = db.relationship('Event', backref=db.backref('team', lazy=True), 
                            foreign_keys='Event.team_id')
    
    def __repr__(self):
        return f'<Team {self.name}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'tournament_id': self.tournament_id,
            'tournament_name': self.tournament.name if self.tournament else None,
            'season_id': self.season_id,
            'goals_season': self.goals_season,
            'yellow_cards_season': self.yellow_cards_season,
            'red_cards_season': self.red_cards_season,
            'points_season': self.points_season,
            'rank_season': self.rank_season,
            'goals_history': self.goals_history,
            'yellow_cards_history': self.yellow_cards_history,
            'red_cards_history': self.red_cards_history
        }
