from . import db
from datetime import datetime

class Player(db.Model):
    __tablename__ = 'player'
    
    player_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(1), nullable=False)  # 'M' 男, 'F' 女
    team_id = db.Column(db.Integer, db.ForeignKey('team.team_id'))
    season_id = db.Column(db.Integer, db.ForeignKey('season.season_id'))
    season_goals = db.Column(db.Integer, default=0)
    season_cards = db.Column(db.Integer, default=0)
    historical_goals = db.Column(db.Integer, default=0)
    historical_cards = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    team = db.relationship('Team', backref=db.backref('players', lazy=True))
    season = db.relationship('Season', backref=db.backref('players', lazy=True))
    events = db.relationship('Event', backref=db.backref('player', lazy=True))
    
    def __repr__(self):
        return f'<Player {self.player_name}>'
    
    def to_dict(self):
        return {
            'player_id': self.player_id,
            'player_name': self.player_name,
            'gender': self.gender,
            'team_id': self.team_id,
            'team_name': self.team.team_name if self.team else None,
            'season_id': self.season_id,
            'season_goals': self.season_goals,
            'season_cards': self.season_cards,
            'historical_goals': self.historical_goals,
            'historical_cards': self.historical_cards
        }