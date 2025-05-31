from . import db
from datetime import datetime

class Season(db.Model):
    __tablename__ = 'season'
    
    season_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    season_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    is_current = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<Season {self.season_name}>'
    
    def to_dict(self):
        return {
            'season_id': self.season_id,
            'season_name': self.season_name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_current': self.is_current
        }