from app import db

class PlayerTeamHistory(db.Model):
    """球员-队伍记录表 - 存储球员在特定赛事中的队伍归属和统计信息"""
    __tablename__ = 'player_team_history'
    
    # 主键
    id = db.Column('记录ID', db.Integer, primary_key=True, comment='记录ID')
    
    # 外键关系
    player_id = db.Column('球员ID', db.String(20), db.ForeignKey('player.球员ID'), nullable=False, comment='球员ID')
    player_number = db.Column('球员号码', db.Integer, nullable=False, comment='球员号码')
    team_id = db.Column('球队ID', db.Integer, db.ForeignKey('team.球队ID'), nullable=False, comment='球队ID')
    tournament_id = db.Column('赛事ID', db.Integer, db.ForeignKey('tournament.赛事ID'), nullable=False, comment='赛事ID')
    
    # 赛事统计数据
    tournament_goals = db.Column('赛事进球数', db.Integer, default=0, comment='赛事进球数')
    tournament_red_cards = db.Column('赛事红牌数', db.Integer, default=0, comment='赛事红牌数')
    tournament_yellow_cards = db.Column('赛事黄牌数', db.Integer, default=0, comment='赛事黄牌数')
    remarks = db.Column('备注', db.Text, comment='备注信息')
    
    # 关系
    player = db.relationship('Player', back_populates='team_histories')
    team = db.relationship('Team', back_populates='player_histories')
    tournament = db.relationship('Tournament', backref=db.backref('player_histories', lazy=True))
    
    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('球员ID', '球队ID', '赛事ID', name='unique_player_team_tournament'),
        db.Index('idx_team_tournament', '球队ID', '赛事ID'),
        db.Index('idx_player_tournament', '球员ID', '赛事ID'),
    )
    
    def __repr__(self):
        return f'<PlayerTeamHistory {self.player_id} in Team {self.team_id}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'player_id': self.player_id,
            'player_name': self.player.name if self.player else None,
            'player_number': self.player_number,
            'team_id': self.team_id,
            'team_name': self.team.name if self.team else None,
            'tournament_id': self.tournament_id,
            'tournament_name': self.tournament.name if self.tournament else None,
            'tournament_goals': self.tournament_goals,
            'tournament_red_cards': self.tournament_red_cards,
            'tournament_yellow_cards': self.tournament_yellow_cards,
            'remarks': self.remarks
        }
