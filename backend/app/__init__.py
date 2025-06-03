from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # 导入模型以确保它们被注册
    from app.models import User, Match, Player, Event
    from app.models.team import Team
    from app.models.tournament import Tournament
    from app.models.player_team_history import PlayerTeamHistory
    
    # 在应用上下文中创建数据库表
    with app.app_context():
        db.create_all()
    
    # 导入和注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.matches import matches_bp
    from app.routes.events import events_bp
    from app.routes.teams import teams_bp
    from app.routes.players import players_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(matches_bp, url_prefix='/api/matches')
    app.register_blueprint(events_bp, url_prefix='/api/events')
    app.register_blueprint(teams_bp, url_prefix='/api/teams')
    app.register_blueprint(players_bp, url_prefix='/api/players')
    
    @app.route('/api/test')
    def test_route():
        return {"message": "API is working!"}
        
    return app
