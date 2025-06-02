from app import db

class Event(db.Model):
    """事件表 - 存储比赛中的事件（进球、红黄牌等）"""
    __tablename__ = 'event'
    
    # 主键
    id = db.Column('eventID', db.Integer, primary_key=True, comment='eventID')
    
    # 事件信息
    event_type = db.Column('事件类型', db.String(50), nullable=False, comment='事件类型(goal, yellow_card, red_card等)')
    time = db.Column('事件发生时间', db.Integer, comment='事件发生时间(分钟)')
    
    # 外键关系
    match_id = db.Column('MatchID', db.Integer, db.ForeignKey('match.MatchID'), nullable=False, comment='比赛ID')
    team_id = db.Column('球队ID', db.Integer, db.ForeignKey('team.球队ID'), comment='球队ID')
    player_id = db.Column('球员ID', db.Integer, db.ForeignKey('player.球员ID'), comment='球员ID')
    season_id = db.Column('赛季ID', db.Integer, db.ForeignKey('season.赛季ID'), comment='赛季ID')
    
    # 关系在其他模型中定义
    
    def __repr__(self):
        return f'<Event {self.id} {self.event_type}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'time': self.time,
            'match_id': self.match_id,
            'team_id': self.team_id,
            'team_name': self.team.name if self.team else None,
            'player_id': self.player_id,
            'player_name': self.player.name if hasattr(self, 'player') and self.player else None,
            'season_id': self.season_id
        }
