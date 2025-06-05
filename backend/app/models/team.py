from app import db

class Team(db.Model):
    """球队表 - 存储球队信息"""
    __tablename__ = 'team'
    
    # 主键
    id = db.Column('球队ID', db.Integer, primary_key=True, comment='球队ID')
    
    # 球队信息
    name = db.Column('球队名称', db.String(100), nullable=False, comment='球队名称')
    group_id = db.Column('小组ID', db.String(1), comment='小组ID')
    
    # 外键关系
    tournament_id = db.Column('赛事ID', db.Integer, db.ForeignKey('tournament.赛事ID'), nullable=False, comment='赛事ID')
    
    # 统计数据
    tournament_goals = db.Column('赛事总进球数', db.Integer, default=0, comment='赛事总进球数')
    tournament_goals_conceded = db.Column('赛事总失球数量', db.Integer, default=0, comment='赛事总失球数量')
    tournament_goal_difference = db.Column('赛事总净胜球', db.Integer, default=0, comment='赛事总净胜球')
    tournament_red_cards = db.Column('赛事红牌数', db.Integer, default=0, comment='赛事红牌数')
    tournament_yellow_cards = db.Column('赛事黄牌数', db.Integer, default=0, comment='赛事黄牌数')
    tournament_points = db.Column('赛事积分', db.Integer, default=0, comment='赛事积分')
    tournament_rank = db.Column('赛事排名', db.Integer, comment='赛事排名')
    
    # 关系
    tournament = db.relationship('Tournament', backref=db.backref('teams', lazy=True))
    player_histories = db.relationship('PlayerTeamHistory', back_populates='team')
    events = db.relationship('Event', back_populates='team', lazy=True)
    
    def __repr__(self):
        return f'<Team {self.name}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'group_id': self.group_id,
            'tournament_id': self.tournament_id,
            'tournament_name': self.tournament.name if self.tournament else None,
            'tournament_goals': self.tournament_goals,
            'tournament_goals_conceded': self.tournament_goals_conceded,
            'tournament_goal_difference': self.tournament_goal_difference,
            'tournament_red_cards': self.tournament_red_cards,
            'tournament_yellow_cards': self.tournament_yellow_cards,
            'tournament_points': self.tournament_points,
            'tournament_rank': self.tournament_rank
        }
