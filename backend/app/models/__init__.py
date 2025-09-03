from app.models.user import User
from app.models.player import Player
from app.models.team import Team
from app.models.team_base import TeamBase
from app.models.team_tournament_participation import TeamTournamentParticipation
from app.models.match import Match
from app.models.event import Event
from app.models.tournament import Tournament
from app.models.competition import Competition
from app.models.season import Season
from app.models.player_team_history import PlayerTeamHistory

# 确保所有模型可以通过 app.models 直接访问
__all__ = [
    'User', 'Player', 'Team', 'TeamBase', 'TeamTournamentParticipation',
    'Match', 'Event', 'Tournament', 'Competition', 'Season', 'PlayerTeamHistory'
]
