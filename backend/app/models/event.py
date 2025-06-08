from app import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = 'event'
    
    id = db.Column('EventID', db.Integer, primary_key=True)
    event_type = db.Column('事件类型', db.String(20), nullable=False)
    match_id = db.Column('MatchID', db.Integer, db.ForeignKey('match.MatchID'), nullable=False)
    team_id = db.Column('球队ID', db.Integer, db.ForeignKey('team.球队ID'), nullable=True)
    player_id = db.Column('球员ID', db.Integer, db.ForeignKey('player.球员ID'), nullable=False)
    event_time = db.Column('事件时间', db.Integer, nullable=True)  # 存储比赛第几分钟
    
    # 关联关系
    match = db.relationship('Match', back_populates='events')
    team = db.relationship('Team', back_populates='events')
    player = db.relationship('Player', back_populates='events')
    
    def to_dict(self):
        """转换为字典格式，确保与触发器兼容"""
        try:
            return {
                'id': self.id,
                'eventType': self.event_type,
                'matchId': self.match_id,
                'teamId': self.team_id,
                'playerId': self.player_id,
                'eventTime': self.event_time,
                'playerName': self.player.name if self.player else None,
                'teamName': self.team.name if self.team else None
            }
        except Exception as e:
            # 返回基本信息，避免因关联数据问题导致整个请求失败
            import logging
            logging.getLogger(__name__).warning(f"Event {self.id} to_dict error: {str(e)}")
            return {
                'id': self.id,
                'eventType': self.event_type,
                'matchId': self.match_id,
                'teamId': self.team_id,
                'playerId': self.player_id,
                'eventTime': self.event_time,
                'playerName': None,
                'teamName': None
            }
    
    def __repr__(self):
        return f'<Event {self.id}: {self.event_type} by Player {self.player_id} at {self.event_time}min>'