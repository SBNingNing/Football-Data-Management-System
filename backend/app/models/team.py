from app import db

class Team(db.Model):
    """球队表 - 存储球队信息（保持向后兼容的视图）"""
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
    
    # 比赛统计数据（新增）
    matches_played = db.Column('比赛轮数', db.Integer, default=0, nullable=False, comment='比赛轮数')
    wins = db.Column('胜场数', db.Integer, default=0, nullable=False, comment='胜场数')
    draws = db.Column('平场数', db.Integer, default=0, nullable=False, comment='平场数')
    losses = db.Column('负场数', db.Integer, default=0, nullable=False, comment='负场数')
    
    # 基础球队ID（连接到team_base）
    team_base_id = db.Column('基础球队ID', db.Integer, db.ForeignKey('team_base.基础球队ID'), comment='基础球队ID')
    
    # 关系
    tournament = db.relationship('Tournament', back_populates='teams')
    player_histories = db.relationship('PlayerTeamHistory', back_populates='team')
    events = db.relationship('Event', back_populates='team', lazy=True)
    team_base = db.relationship('TeamBase', back_populates='team_instances')
    
    @property
    def participation_record(self):
        """获取对应的参赛记录"""
        from .team_tournament_participation import TeamTournamentParticipation
        return TeamTournamentParticipation.query.filter_by(
            team_id=self.id,
            tournament_id=self.tournament_id
        ).first()
    
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
            'tournament_rank': self.tournament_rank,
            'matches_played': self.matches_played,
            'wins': self.wins,
            'draws': self.draws,
            'losses': self.losses
        }
