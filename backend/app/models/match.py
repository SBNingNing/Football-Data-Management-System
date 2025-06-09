from app import db
from datetime import datetime

class Match(db.Model):
    """比赛表 - 存储比赛信息"""
    __tablename__ = 'match'
    
    # 主键
    id = db.Column('MatchID', db.String(50), primary_key=True, comment='MatchID')
    
    # 比赛信息
    match_name = db.Column('比赛名称', db.String(50), nullable=False, comment='比赛名称')
    match_time = db.Column('比赛时间', db.DateTime, nullable=False, comment='比赛时间')
    location = db.Column('比赛地点', db.String(50), nullable=False, comment='比赛地点')
    home_score = db.Column('主队比分', db.Integer, default=0, comment='主队比分')
    away_score = db.Column('客队比分', db.Integer, default=0, comment='客队比分')
    group_id = db.Column('小组ID', db.String(1), comment='小组ID')
    status = db.Column('比赛状态', db.String(1), default='P', comment='比赛状态(F: 已结束，O:正在进行，P: 未结束)')
    knockout_round = db.Column('淘汰赛轮次', db.Integer, comment='淘汰赛轮次(0:常规赛, 1:附加赛, 2:1/4决赛, 3:半决赛, 4:决赛)')
    
    # 外键关系
    home_team_id = db.Column('主队ID', db.Integer, db.ForeignKey('team.球队ID'), nullable=True, comment='主队ID')
    away_team_id = db.Column('客队ID', db.Integer, db.ForeignKey('team.球队ID'), nullable=True, comment='客队ID')
    tournament_id = db.Column('赛事ID', db.Integer, db.ForeignKey('tournament.赛事ID'), nullable=False, comment='赛事ID')
    
    # 关系
    home_team = db.relationship('Team', foreign_keys=[home_team_id], 
                               backref=db.backref('home_matches', lazy=True))
    away_team = db.relationship('Team', foreign_keys=[away_team_id], 
                               backref=db.backref('away_matches', lazy=True))
    tournament = db.relationship('Tournament', backref=db.backref('matches', lazy=True))
    events = db.relationship('Event', back_populates='match', lazy=True)
    
    def __repr__(self):
        return f'<Match {self.id} {self.home_team.name if self.home_team else "Unknown"} vs {self.away_team.name if self.away_team else "Unknown"}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'match_name': self.match_name,
            'match_time': self.match_time.isoformat() if self.match_time else None,
            'location': self.location,
            'home_team_id': self.home_team_id,
            'home_team_name': self.home_team.name if self.home_team else None,
            'away_team_id': self.away_team_id,
            'away_team_name': self.away_team.name if self.away_team else None,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'group_id': self.group_id,
            'tournament_id': self.tournament_id,
            'tournament_name': self.tournament.name if self.tournament else None,
            'status': self.status,
            'knockout_round': self.knockout_round
        }