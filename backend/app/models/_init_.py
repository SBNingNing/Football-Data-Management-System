from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .player import Player
from .team import Team
from .match import Match
from .event import Event
from .tournament import Tournament
from .season import Season
from .user import User