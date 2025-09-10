from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.database import db, jwt
from app.utils.logger import get_logger
from app.utils.logging_config import setup_logging

logger = get_logger(__name__)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 设置日志配置（在应用配置之后立即设置）
    setup_logging(app)
    
    # 添加应用基本信息
    app.config['APP_NAME'] = 'Football Management System'
    app.config['APP_VERSION'] = '1.0.0'
    
    # 验证配置
    config_errors = config_class.validate_config()
    if config_errors:
        logger.warning(f"配置验证警告: {', '.join(config_errors)}")
    
    db.init_app(app)
    jwt.init_app(app)
    
    # 使用配置文件中的CORS设置
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ["http://localhost:3000", "http://localhost:8080"]),
            "methods": app.config.get('CORS_METHODS', ["GET", "POST", "PUT", "DELETE", "OPTIONS"]),
            "allow_headers": app.config.get('CORS_HEADERS', ["Content-Type", "Authorization"])
        }
    })
    
    # 导入模型以确保它们被注册
    from app.models import (
        User, Match, Player, Event, Team, TeamBase, Tournament, 
        Competition, Season, PlayerTeamHistory, TeamTournamentParticipation
    )
    
    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.matches import matches_bp
    from app.routes.events import events_bp
    from app.routes.teams import teams_bp
    from app.routes.tournaments import tournaments_bp
    from app.routes.competitions import competitions_bp
    from app.routes.seasons import seasons_bp
    from app.routes.player_history import player_history_bp
    from app.routes.team_history import team_history_bp
    from app.routes.stats import stats_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(matches_bp, url_prefix='/api/matches')
    app.register_blueprint(events_bp, url_prefix='/api/events')
    app.register_blueprint(teams_bp, url_prefix='/api/teams')
    app.register_blueprint(tournaments_bp, url_prefix='/api/tournaments')
    app.register_blueprint(competitions_bp, url_prefix='/api/competitions')
    app.register_blueprint(seasons_bp, url_prefix='/api/seasons')
    app.register_blueprint(player_history_bp, url_prefix='/api/player_history')
    app.register_blueprint(team_history_bp, url_prefix='/api/team_history')
    # stats_bp已经包含url_prefix='/api'，所以不需要额外添加
    app.register_blueprint(stats_bp)
    
    # 注册球员路由
    try:
        from app.routes.players import players_bp
        app.register_blueprint(players_bp, url_prefix='/api/players')
    except ImportError as e:
        logger.error(f"注册球员路由失败: {e}")
    except Exception as e:
        logger.error(f"球员路由注册过程中出现异常: {e}")
        
    return app
