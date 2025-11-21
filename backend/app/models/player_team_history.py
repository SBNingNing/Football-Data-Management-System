from app.database import db

class PlayerTeamHistory(db.Model):
    """球员-队伍记录表 - 存储球员在特定赛事中的队伍归属和统计信息。
    注意：这里的 team_id 实际指向的是 team_tournament_participation.参与ID (即某支基础球队在某赛事中的参赛实例)，
    而不是旧结构中的 team.球队ID。因此与 Team 的关联需要通过 participation -> team_base + tournament 反查。"""
    __tablename__ = 'player_team_history'
    
    # 主键
    id = db.Column('记录ID', db.Integer, primary_key=True, comment='记录ID')
    
    # 外键关系 - 修正为正确的引用
    player_id = db.Column('球员ID', db.String(20), 
                          db.ForeignKey('player.球员ID', ondelete='CASCADE'), 
                          nullable=False, comment='球员ID')
    player_number = db.Column('球员号码', db.Integer, nullable=False, comment='球员号码')
    # 参与记录ID（外键到 team_tournament_participation.参与ID）
    team_id = db.Column('球队ID', db.Integer,
                        db.ForeignKey('team_tournament_participation.参与ID', ondelete='CASCADE'),
                        nullable=True, comment='参赛记录ID（team_tournament_participation.参与ID）')
    tournament_id = db.Column('赛事ID', db.Integer, 
                             db.ForeignKey('tournament.赛事ID', ondelete='CASCADE'), 
                             nullable=False, comment='赛事ID')
    
    # 赛事统计数据
    tournament_goals = db.Column('赛事进球数', db.Integer, default=0, comment='赛事进球数')
    tournament_red_cards = db.Column('赛事红牌数', db.Integer, default=0, comment='赛事红牌数')
    tournament_yellow_cards = db.Column('赛事黄牌数', db.Integer, default=0, comment='赛事黄牌数')
    remarks = db.Column('备注', db.Text, comment='备注信息')
    
    # 关系 - 修正关系映射
    player = db.relationship('Player', back_populates='team_histories')
    team_participation = db.relationship('TeamTournamentParticipation', back_populates='player_histories')
    tournament = db.relationship('Tournament', back_populates='player_histories')
    
    # 约束和索引 - 匹配SQL定义
    __table_args__ = (
        db.UniqueConstraint('球员ID', '球队ID', '赛事ID', name='unique_active_player_team_tournament'),
        db.Index('idx_team_tournament', '球队ID', '赛事ID'),
        db.Index('idx_player_tournament', '球员ID', '赛事ID'),
        db.CheckConstraint('赛事进球数 >= 0', name='player_team_history_chk_1'),
        db.CheckConstraint('赛事红牌数 >= 0', name='player_team_history_chk_2'),
        db.CheckConstraint('赛事黄牌数 >= 0', name='player_team_history_chk_3'),
    )
    
    # 兼容调用：提供 team_info 和 team_base 动态属性用于旧代码访问
    @property
    def team_info(self):
        """通过参赛记录反查 Team（如果仍然存在旧 Team 记录）。
        如果 Team 表与新的 participation 模型并存，可尝试根据 team_base_id + tournament_id 查找。"""
        try:
            participation = self.team_participation
            if not participation:
                return None
            from .team import Team
            return Team.query.filter_by(team_base_id=participation.team_base_id,
                                        tournament_id=participation.tournament_id).first()
        except Exception:
            return None

    @property
    def team_base(self):
        participation = self.team_participation
        return participation.team_base if participation else None
    
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
            'team_name': self.team_base.name if self.team_base else None,
            'tournament_id': self.tournament_id,
            'tournament_name': self.tournament.name if self.tournament else None,
            'tournament_goals': self.tournament_goals,
            'tournament_red_cards': self.tournament_red_cards,
            'tournament_yellow_cards': self.tournament_yellow_cards,
            'remarks': self.remarks
        }
