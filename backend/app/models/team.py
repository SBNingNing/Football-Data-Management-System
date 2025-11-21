from app.database import db

class Team(db.Model):
    """Team 视图模型（只读）。
    对应数据库中的 VIEW `team`，其来源是 team_tournament_participation JOIN team_base。
    由于视图不具备真正的外键约束，这里不声明 ForeignKey/relationship，避免 SQLAlchemy mapper 初始化错误。
    访问关联请通过派生属性 participation_record / tournament / team_base。"""
    __tablename__ = 'team'

    # 基础字段（直接映射视图列）
    id = db.Column('球队ID', db.Integer, primary_key=True)
    name = db.Column('球队名称', db.String(100))
    group_id = db.Column('小组ID', db.String(1))
    tournament_id = db.Column('赛事ID', db.Integer)
    tournament_goals = db.Column('赛事总进球数', db.Integer)
    tournament_goals_conceded = db.Column('赛事总失球数量', db.Integer)
    tournament_goal_difference = db.Column('赛事总净胜球', db.Integer)
    tournament_red_cards = db.Column('赛事红牌数', db.Integer)
    tournament_yellow_cards = db.Column('赛事黄牌数', db.Integer)
    tournament_points = db.Column('赛事积分', db.Integer)
    tournament_rank = db.Column('赛事排名', db.Integer)
    matches_played = db.Column('比赛轮数', db.Integer)
    wins = db.Column('胜场数', db.Integer)
    draws = db.Column('平场数', db.Integer)
    losses = db.Column('负场数', db.Integer)
    team_base_id = db.Column('球队基础ID', db.Integer)
    status = db.Column('参与状态', db.String(20))
    
    @property
    def participation_record(self):
        from .team_tournament_participation import TeamTournamentParticipation
        if not self.team_base_id or not self.tournament_id:
            return None
        return TeamTournamentParticipation.query.filter_by(球队基础ID=self.team_base_id, 赛事ID=self.tournament_id).first()

    @property
    def player_histories(self):
        record = self.participation_record
        return record.player_histories if record else []

    @property
    def events(self):
        record = self.participation_record
        return record.events if record else []

    @property
    def tournament(self):
        from .tournament import Tournament
        return Tournament.query.get(self.tournament_id) if self.tournament_id else None
    
    def __repr__(self):
        return f'<Team {self.name}>'
    
    def to_dict(self):
        """将对象转换为字典，便于API返回JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'group_id': self.group_id,
            'tournament_id': self.tournament_id,
            'tournament_goals': self.tournament_goals,
            'tournament_goals_conceded': self.tournament_goals_conceded,
            'tournament_goal_difference': self.tournament_goal_difference,
            'tournament_red_cards': self.tournament_red_cards,
            'tournament_yellow_cards': self.tournament_yellow_cards,
            'tournament_points': self.tournament_points,
            'tournament_rank': self.tournament_rank,
            'matches_played': self.matches_played,
            'wins': self.wins,
            'draws': self.draws,
            'losses': self.losses,
            'team_base_id': self.team_base_id,
            'status': self.status,
            'competitionId': self.tournament.competition_id if self.tournament else None
        }
