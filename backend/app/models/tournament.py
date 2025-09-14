from app.database import db
from datetime import datetime

class Tournament(db.Model):
    """赛事-赛季实例表 - 存储赛事和赛季的组合实例"""
    __tablename__ = 'tournament'
    
    # 主键
    id = db.Column('赛事ID', db.Integer, primary_key=True, comment='赛事ID')
    
    # 外键关系
    competition_id = db.Column('competition_id', db.Integer, 
                              db.ForeignKey('competition.competition_id', ondelete='CASCADE'), 
                              nullable=False, comment='赛事ID')
    season_id = db.Column('season_id', db.Integer, 
                         db.ForeignKey('season.season_id', ondelete='CASCADE'), 
                         nullable=False, comment='赛季ID')
    
    # 赛事配置
    is_grouped = db.Column('常规赛是否分组', db.Boolean, default=False, comment='是否需要分组进行')
    group_count = db.Column('常规赛小组数', db.SmallInteger, nullable=True, comment='常规赛小组数量')
    playoff_spots = db.Column('淘汰赛名额数', db.SmallInteger, nullable=True, comment='淘汰赛名额数量')
    
    # 关系
    competition = db.relationship('Competition', back_populates='tournaments')
    season = db.relationship('Season', back_populates='tournaments')
    # 不再直接 relationship 到 Team 视图（无真实外键），改用 property
    team_participations = db.relationship('TeamTournamentParticipation', back_populates='tournament', lazy=True)  # 新的关系
    matches = db.relationship('Match', back_populates='tournament', lazy=True)
    player_histories = db.relationship('PlayerTeamHistory', back_populates='tournament', lazy=True)
    
    # 索引
    __table_args__ = (
        db.Index('idx_tournament_competition', 'competition_id'),
        db.Index('idx_tournament_season', 'season_id'),
    )
    
    def __repr__(self):
        competition_name = self.competition.name if self.competition else 'Unknown'
        season_name = self.season.name if self.season else 'Unknown'
        return f'<Tournament {competition_name} - {season_name}>'
    
    @property
    def name(self):
        """返回赛事名称，保持向后兼容"""
        return self.competition.name if self.competition else ''
    
    @property
    def season_name(self):
        """返回赛季名称，保持向后兼容"""
        return self.season.name if self.season else ''
    
    @property
    def season_start_time(self):
        """返回赛季开始时间，保持向后兼容"""
        return self.season.start_time if self.season else None
    
    @property
    def season_end_time(self):
        """返回赛季结束时间，保持向后兼容"""
        return self.season.end_time if self.season else None
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'competition_id': self.competition_id,
            'season_id': self.season_id,
            'name': self.name,
            'season_name': self.season_name,
            'is_grouped': self.is_grouped,
            'group_count': self.group_count,
            'playoff_spots': self.playoff_spots,
            'season_start_time': self.season_start_time.isoformat() if self.season_start_time else None,
            'season_end_time': self.season_end_time.isoformat() if self.season_end_time else None,
            'competition': self.competition.to_dict() if self.competition else None,
            'season': self.season.to_dict() if self.season else None
        }

    @property
    def teams(self):
        from .team import Team
        return Team.query.filter_by(tournament_id=self.id).all()
