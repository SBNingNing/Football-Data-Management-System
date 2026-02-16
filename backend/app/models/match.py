from app.database import db
from datetime import datetime

class Match(db.Model):
    """比赛表 - 存储比赛信息"""
    __tablename__ = 'match'
    
    # 主键 - 与SQL表结构匹配
    id = db.Column('MatchID', db.String(50), primary_key=True, comment='MatchID')
    
    # 比赛信息
    match_name = db.Column('比赛名称', db.String(50), nullable=False, comment='比赛名称')
    match_time = db.Column('比赛时间', db.DateTime, nullable=False, comment='比赛时间')
    location = db.Column('比赛地点', db.String(50), nullable=False, comment='比赛地点')
    home_score = db.Column('主队比分', db.Integer, default=0, comment='主队比分')
    away_score = db.Column('客队比分', db.Integer, default=0, comment='客队比分')
    group_id = db.Column('小组ID', db.String(1), comment='小组ID')
    status = db.Column('比赛状态', db.String(1), default='P', comment='比赛状态(F: 已结束，P: 未开始)')
    knockout_round = db.Column('淘汰赛轮次', db.Integer, comment='淘汰赛轮次')
    
    # 外键关系 - 修正为指向 team_tournament_participation 表
    home_team_id = db.Column('主队ID', db.Integer, 
                            db.ForeignKey('team_tournament_participation.参与ID', 
                                         ondelete='CASCADE', onupdate='CASCADE'), 
                            nullable=True, comment='主队ID')
    away_team_id = db.Column('客队ID', db.Integer, 
                            db.ForeignKey('team_tournament_participation.参与ID', 
                                         ondelete='CASCADE', onupdate='CASCADE'), 
                            nullable=True, comment='客队ID')
    tournament_id = db.Column('赛事ID', db.Integer, 
                             db.ForeignKey('tournament.赛事ID', ondelete='CASCADE', onupdate='CASCADE'), 
                             nullable=False, comment='赛事ID')
    
    # 关系 - 修正关系映射
    home_team = db.relationship('TeamTournamentParticipation', foreign_keys=[home_team_id], back_populates='home_matches')
    away_team = db.relationship('TeamTournamentParticipation', foreign_keys=[away_team_id], back_populates='away_matches')
    tournament = db.relationship('Tournament', back_populates='matches')
    events = db.relationship('Event', back_populates='match', lazy=True)
    
    # 索引和约束 - 匹配SQL定义
    __table_args__ = (
        db.Index('idx_match_home_team', '主队ID'),
        db.Index('idx_match_away_team', '客队ID'),
        db.Index('idx_match_tournament', '赛事ID'),
        db.Index('idx_match_time', '比赛时间'),
        db.Index('idx_match_status', '比赛状态'),
        db.CheckConstraint("比赛状态 in ('F','P')", name='match_chk_1'),
    )
    
    def __repr__(self):
        home_name = self.home_team.team_base.name if self.home_team and getattr(self.home_team, 'team_base', None) else "Unknown"
        away_name = self.away_team.team_base.name if self.away_team and getattr(self.away_team, 'team_base', None) else "Unknown"
        return f'<Match {self.id} {home_name} vs {away_name}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'match_name': self.match_name,
            'match_time': self.match_time.isoformat() if self.match_time else None,
            'location': self.location,
            'home_team_id': self.home_team_id,
            'home_team_name': (self.home_team.team_base.name if self.home_team and getattr(self.home_team, 'team_base', None) else None),
            'away_team_id': self.away_team_id,
            'away_team_name': (self.away_team.team_base.name if self.away_team and getattr(self.away_team, 'team_base', None) else None),
            'home_score': self.home_score,
            'away_score': self.away_score,
            'group_id': self.group_id,
            'tournament_id': self.tournament_id,
            'tournament_name': self.tournament.name if self.tournament else None,
            'competition_id': self.tournament.competition_id if self.tournament else None,
            'competitionId': self.tournament.competition_id if self.tournament else None,
            'status': self.status,
            'knockout_round': self.knockout_round
        }