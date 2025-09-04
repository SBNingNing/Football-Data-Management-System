from app import db
from datetime import datetime

class TeamBase(db.Model):
    """球队基础信息表 - 存储球队的核心信息"""
    __tablename__ = 'team_base'
    
    # 主键 - 与SQL表结构完全匹配
    id = db.Column('球队基础ID', db.Integer, primary_key=True, comment='球队基础ID')
    
    # 球队基础信息
    name = db.Column('球队名称', db.String(100), nullable=False, unique=True, comment='球队名称')
    created_at = db.Column('创建时间', db.DateTime, default=datetime.utcnow, comment='创建时间')
    notes = db.Column('备注', db.Text, comment='备注信息')
    
    # 关系 - 修正外键引用
    team_instances = db.relationship('Team', back_populates='team_base', lazy='dynamic')
    participations = db.relationship('TeamTournamentParticipation', back_populates='team_base', lazy=True)
    
    # 索引
    __table_args__ = (
        db.Index('uk_team_name', '球队名称'),
    )
    
    def __repr__(self):
        return f'<TeamBase {self.name}>'
    
    def to_dict(self, include_stats=False):
        """将对象转换为字典，便于API返回JSON"""
        data = {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'notes': self.notes,
            'participation_count': len(self.participations) if self.participations else 0
        }
        
        if include_stats:
            # 委托给服务层处理统计计算
            from app.services.team_base_statistics_service import TeamBaseStatisticsService
            stats = TeamBaseStatisticsService.calculate_team_historical_stats(self)
            data['historical_stats'] = stats
        
        return data
