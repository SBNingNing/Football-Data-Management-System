from app import db
from datetime import datetime

class Match(db.Model):
    """比赛表 - 存储比赛信息"""
    __tablename__ = 'match'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, comment='MatchID')
    
    # 比赛信息
    match_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='比赛时间')
    location = db.Column(db.String(100), comment='比赛地点')
    home_score = db.Column(db.Integer, default=0, comment='主队比分')
    away_score = db.Column(db.Integer, default=0, comment='客队比分')
    status = db.Column(db.String(1), default='P', comment='比赛状态(F: 已结束，P: 未结束)')
    
    # 外键关系
    home_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), comment='主队ID')
    away_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), comment='客队ID')
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), comment='赛事ID')
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), comment='赛季ID')
    
    # 关系
    home_team = db.relationship('Team', foreign_keys=[home_team_id], 
                               backref=db.backref('home_matches', lazy=True))
    away_team = db.relationship('Team', foreign_keys=[away_team_id], 
                               backref=db.backref('away_matches', lazy=True))
    tournament = db.relationship('Tournament', backref=db.backref('matches', lazy=True))
    season = db.relationship('Season', backref=db.backref('matches', lazy=True))
    events = db.relationship('Event', backref=db.backref('match', lazy=True))
    
    def __repr__(self):
        return f'<Match {self.id} {self.home_team.name if self.home_team else "Unknown"} vs {self.away_team.name if self.away_team else "Unknown"}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'match_time': self.match_time.isoformat() if self.match_time else None,
            'location': self.location,
            'home_team_id': self.home_team_id,
            'home_team_name': self.home_team.name if self.home_team else None,
            'away_team_id': self.away_team_id,
            'away_team_name': self.away_team.name if self.away_team else None,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'tournament_id': self.tournament_id,
            'tournament_name': self.tournament.name if self.tournament else None,
            'season_id': self.season_id,
            'status': self.status
        }
