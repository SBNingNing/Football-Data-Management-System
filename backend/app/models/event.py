from app import db

class Event(db.Model):
    """事件表 - 存储比赛中的事件（进球、红黄牌等）"""
    __tablename__ = 'event'
    
    # 主键
    id = db.Column('eventID', db.Integer, primary_key=True, comment='eventID')
    
    # 事件信息
    event_type = db.Column('事件类型', db.String(50), nullable=False, comment='事件类型(goal, yellow_card, red_card等)')
    
    # 外键关系 - 修复 MatchID 字段类型
    match_id = db.Column('MatchID', db.String(10), db.ForeignKey('match.MatchID'), nullable=False, comment='比赛ID')
    team_id = db.Column('球队ID', db.Integer, db.ForeignKey('team.球队ID'), nullable=False, comment='球队ID')
    player_id = db.Column('球员ID', db.String(20), db.ForeignKey('player.球员ID'), nullable=False, comment='球员ID')
    
    # 关系 - 修复关系定义，避免backref冲突
    match = db.relationship('Match', back_populates='events')
    team = db.relationship('Team', backref=db.backref('events', lazy=True))
    player = db.relationship('Player', back_populates='events')
    
    def __repr__(self):
        return f'<Event {self.id} {self.event_type}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'match_id': self.match_id,
            'team_id': self.team_id,
            'team_name': self.team.name if self.team else None,
            'player_id': self.player_id,
            'player_name': self.player.name if self.player else None
        }
