from app import db
from datetime import datetime

class TeamBase(db.Model):
    """球队基础信息表 - 存储球队的核心信息"""
    __tablename__ = 'team_base'
    
    # 主键
    id = db.Column('球队基础ID', db.Integer, primary_key=True, comment='球队基础ID')
    
    # 球队基础信息
    name = db.Column('球队名称', db.String(100), nullable=False, unique=True, comment='球队名称')
    created_at = db.Column('创建时间', db.DateTime, default=datetime.utcnow, comment='创建时间')
    notes = db.Column('备注', db.Text, comment='备注信息')
    
    # 关系
    team_instances = db.relationship('Team', back_populates='team_base', lazy='dynamic')
    participations = db.relationship('TeamTournamentParticipation', back_populates='team_base', lazy=True)
    
    def __repr__(self):
        return f'<TeamBase {self.name}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'notes': self.notes,
            'participation_count': len(self.participations) if self.participations else 0
        }
    
    @property
    def total_tournaments(self):
        """参与的赛事总数"""
        return len(self.participations) if self.participations else 0
    
    @property
    def total_goals(self):
        """历史总进球数"""
        return sum(p.goals for p in self.participations) if self.participations else 0
    
    @property
    def total_points(self):
        """历史总积分"""
        return sum(p.points for p in self.participations) if self.participations else 0
    
    @property
    def total_matches(self):
        """历史总比赛场次"""
        return sum(p.matches_played for p in self.participations) if self.participations else 0
    
    @property
    def total_wins(self):
        """历史总胜场"""
        return sum(p.wins for p in self.participations) if self.participations else 0
    
    @property
    def win_rate(self):
        """历史胜率"""
        total_matches = self.total_matches
        if total_matches == 0:
            return 0.0
        return round((self.total_wins / total_matches) * 100, 2)
    
    @property
    def best_rank(self):
        """最佳排名"""
        if not self.participations:
            return None
        valid_ranks = [p.rank for p in self.participations if p.rank and p.rank > 0]
        return min(valid_ranks) if valid_ranks else None
    
    def get_historical_stats(self):
        """获取历史统计数据"""
        return {
            'total_tournaments': self.total_tournaments,
            'total_goals': self.total_goals,
            'total_goals_conceded': sum(p.goals_conceded for p in self.participations) if self.participations else 0,
            'total_goal_difference': sum(p.goal_difference for p in self.participations) if self.participations else 0,
            'total_red_cards': sum(p.red_cards for p in self.participations) if self.participations else 0,
            'total_yellow_cards': sum(p.yellow_cards for p in self.participations) if self.participations else 0,
            'total_points': self.total_points,
            'total_matches_played': self.total_matches,
            'total_wins': self.total_wins,
            'total_draws': sum(p.draws for p in self.participations) if self.participations else 0,
            'total_losses': sum(p.losses for p in self.participations) if self.participations else 0,
            'win_rate': self.win_rate,
            'best_rank': self.best_rank
        }
    
    def get_participation_by_tournament(self, tournament_id):
        """获取指定赛事的参赛记录"""
        for p in self.participations:
            if p.tournament_id == tournament_id:
                return p
        return None
    
    def get_recent_participations(self, limit=5):
        """获取最近的参赛记录"""
        if not self.participations:
            return []
        # 按赛事ID倒序排列（假设赛事ID越大越新）
        sorted_participations = sorted(self.participations, key=lambda p: p.tournament_id, reverse=True)
        return sorted_participations[:limit]
