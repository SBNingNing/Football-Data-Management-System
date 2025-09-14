from app.database import db
from datetime import datetime

class Event(db.Model):
    """事件表 - 存储比赛事件"""
    __tablename__ = 'event'
    
    # 主键 - 与SQL表结构匹配
    id = db.Column('eventID', db.Integer, primary_key=True, comment='事件ID')
    
    # 事件信息
    event_type = db.Column('事件类型', db.String(50), nullable=False, comment='事件类型')
    event_time = db.Column('事件时间', db.Integer, nullable=True, comment='事件发生时间（比赛第几分钟）')
    
    # 外键关系 - 修正为正确的引用
    match_id = db.Column('MatchID', db.String(50), 
                         db.ForeignKey('match.MatchID', ondelete='CASCADE', onupdate='CASCADE'), 
                         nullable=False, comment='比赛ID')
    team_id = db.Column('球队ID', db.Integer, 
                        db.ForeignKey('team_tournament_participation.参与ID', ondelete='CASCADE', onupdate='CASCADE'), 
                        nullable=False, comment='球队ID（引用team_tournament_participation表的参与ID）')
    player_id = db.Column('球员ID', db.String(20), 
                          db.ForeignKey('player.球员ID', ondelete='CASCADE', onupdate='CASCADE'), 
                          nullable=False, comment='球员ID')
    
    # 关系映射 - 修正关系
    match = db.relationship('Match', back_populates='events')
    team_participation = db.relationship('TeamTournamentParticipation', back_populates='events')
    player = db.relationship('Player', back_populates='events')
    
    # 索引 - 匹配SQL定义
    __table_args__ = (
        db.Index('idx_event_match', 'MatchID'),
        db.Index('idx_event_team', '球队ID'),
        db.Index('idx_event_player', '球员ID'),
        db.Index('idx_event_type', '事件类型'),
    )
    
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
                'teamName': self.team_participation.team_base.name if self.team_participation and self.team_participation.team_base else None
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

    # 兼容旧结构：提供 team 属性（可能返回 None）
    @property
    def team(self):
        try:
            if not self.team_participation:
                return None
            from .team import Team
            return Team.query.filter_by(team_base_id=self.team_participation.team_base_id,
                                        tournament_id=self.team_participation.tournament_id).first()
        except Exception:
            return None