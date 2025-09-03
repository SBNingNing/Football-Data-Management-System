from app import db
from datetime import datetime

class TeamTournamentParticipation(db.Model):
    """球队赛事参与表 - 记录球队在特定赛事中的表现"""
    __tablename__ = 'team_tournament_participation'
    
    # 主键
    id = db.Column('参与ID', db.Integer, primary_key=True, comment='参与ID')
    
    # 外键关系
    team_base_id = db.Column('球队基础ID', db.Integer, 
                            db.ForeignKey('team_base.球队基础ID', ondelete='CASCADE'), 
                            nullable=False, comment='球队基础ID')
    tournament_id = db.Column('赛事ID', db.Integer, 
                             db.ForeignKey('tournament.赛事ID', ondelete='CASCADE'), 
                             nullable=False, comment='赛事ID')
    
    # 比赛信息
    group_id = db.Column('小组ID', db.String(1), comment='小组ID')
    
    # 赛事统计数据
    tournament_goals = db.Column('赛事总进球数', db.Integer, default=0, comment='赛事总进球数')
    tournament_goals_conceded = db.Column('赛事总失球数量', db.Integer, default=0, comment='赛事总失球数量')
    tournament_goal_difference = db.Column('赛事总净胜球', db.Integer, default=0, comment='赛事总净胜球')
    tournament_red_cards = db.Column('赛事红牌数', db.Integer, default=0, comment='赛事红牌数')
    tournament_yellow_cards = db.Column('赛事黄牌数', db.Integer, default=0, comment='赛事黄牌数')
    tournament_points = db.Column('赛事积分', db.Integer, default=0, comment='赛事积分')
    tournament_rank = db.Column('赛事排名', db.Integer, comment='赛事排名')
    
    # 比赛记录统计
    matches_played = db.Column('比赛轮数', db.Integer, default=0, nullable=False, comment='比赛轮数')
    wins = db.Column('胜场数', db.Integer, default=0, nullable=False, comment='胜场数')
    draws = db.Column('平场数', db.Integer, default=0, nullable=False, comment='平场数')
    losses = db.Column('负场数', db.Integer, default=0, nullable=False, comment='负场数')
    
    # 参与状态和时间
    registration_time = db.Column('报名时间', db.DateTime, default=datetime.utcnow, comment='报名时间')
    status = db.Column('状态', db.Enum('active', 'withdrawn', 'completed', name='participation_status'), 
                       default='active', comment='参与状态')
    
    # 关系
    team_base = db.relationship('TeamBase', back_populates='participations')
    tournament = db.relationship('Tournament', back_populates='team_participations')
    player_histories = db.relationship('PlayerTeamHistory', back_populates='team_participation')
    events = db.relationship('Event', back_populates='team_participation', lazy=True)
    
    # 索引和约束
    __table_args__ = (
        db.UniqueConstraint('球队基础ID', '赛事ID', name='uk_team_tournament'),
        db.Index('idx_team_base', '球队基础ID'),
        db.Index('idx_tournament', '赛事ID'),
        db.Index('idx_team_tournament_status', '球队基础ID', '赛事ID', '状态'),
    )
    
    def __repr__(self):
        team_name = self.team_base.name if self.team_base else 'Unknown'
        tournament_name = self.tournament.name if self.tournament else 'Unknown'
        return f'<TeamTournamentParticipation {team_name} in {tournament_name}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'team_base_id': self.team_base_id,
            'tournament_id': self.tournament_id,
            'team_name': self.team_base.name if self.team_base else None,
            'tournament_name': self.tournament.name if self.tournament else None,
            'group_id': self.group_id,
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
            'losses': self.losses,
            'win_rate': self.win_rate,
            'registration_time': self.registration_time.isoformat() if self.registration_time else None,
            'status': self.status
        }
    
    @property
    def win_rate(self):
        """胜率计算"""
        if self.matches_played == 0:
            return 0.0
        return round((self.wins / self.matches_played) * 100, 2)
    
    @property
    def avg_goals_per_match(self):
        """场均进球"""
        if self.matches_played == 0:
            return 0.0
        return round(self.tournament_goals / self.matches_played, 2)
    
    @property
    def avg_goals_conceded_per_match(self):
        """场均失球"""
        if self.matches_played == 0:
            return 0.0
        return round(self.tournament_goals_conceded / self.matches_played, 2)
    
    def calculate_goal_difference(self):
        """计算净胜球并更新"""
        self.tournament_goal_difference = self.tournament_goals - self.tournament_goals_conceded
        return self.tournament_goal_difference
    
    def update_match_result(self, is_win=False, is_draw=False):
        """更新比赛结果统计"""
        self.matches_played += 1
        if is_win:
            self.wins += 1
        elif is_draw:
            self.draws += 1
        else:
            self.losses += 1
