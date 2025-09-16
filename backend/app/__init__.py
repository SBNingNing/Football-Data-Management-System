from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import init_extensions, db, jwt
from app.utils.logger import get_logger
from app.utils.logging_config import setup_logging
from app.errors import register_error_handlers
from flask import g
from app.middleware.context_middleware import ensure_request_context

logger = get_logger(__name__)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 设置日志配置
    setup_logging(app)
    app.config.setdefault('APP_NAME', 'Football Management System')
    app.config.setdefault('APP_VERSION', '1.0.0')

    # 在开发环境，如果未设置安全密钥，则自动生成一次性随机密钥，避免误用默认弱密钥
    try:
        if app.config.get('DEBUG', False):
            import secrets
            if not app.config.get('SECRET_KEY') or app.config.get('SECRET_KEY') == 'dev-key-should-be-changed':
                app.config['SECRET_KEY'] = secrets.token_urlsafe(32)
            if not app.config.get('JWT_SECRET_KEY') or app.config.get('JWT_SECRET_KEY') == 'jwt-dev-key-change-in-production':
                app.config['JWT_SECRET_KEY'] = secrets.token_urlsafe(32)
    except Exception:
        # 生成失败不阻断启动
        pass

    # 配置校验（使用运行时 app.config 进行校验，避免因为默认值导致的误报）
    config_errors = config_class.validate_config(app.config)
    if config_errors:
        logger.warning(f"配置验证警告: {', '.join(config_errors)}")

    # 扩展初始化
    init_extensions(app)

    # CORS 统一策略
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ["http://localhost:3000", "http://localhost:8080"]),
            "methods": app.config.get('CORS_METHODS', ["GET", "POST", "PUT", "DELETE", "OPTIONS"]),
            "allow_headers": app.config.get('CORS_HEADERS', ["Content-Type", "Authorization"])
        }
    })

    # request context middleware (before_request hook)
    @app.before_request
    def _inject_ctx():  # pragma: no cover - 简单注入逻辑
        ensure_request_context()

    # 导入模型确保元数据注册
    from app import models  # noqa: F401

    # 注册蓝图集合
    from app.routes import auth, matches, events, teams, tournaments, competitions, seasons, player_history, team_history, stats, health
    app.register_blueprint(auth.auth_bp, url_prefix='/api/auth')
    app.register_blueprint(matches.matches_bp, url_prefix='/api/matches')
    app.register_blueprint(events.events_bp, url_prefix='/api/events')
    app.register_blueprint(teams.teams_bp, url_prefix='/api/teams')
    app.register_blueprint(tournaments.tournaments_bp, url_prefix='/api/tournaments')
    app.register_blueprint(competitions.competitions_bp, url_prefix='/api/competitions')
    app.register_blueprint(seasons.seasons_bp, url_prefix='/api/seasons')
    app.register_blueprint(player_history.player_history_bp, url_prefix='/api/player-history')
    app.register_blueprint(team_history.team_history_bp, url_prefix='/api/team-history')
    app.register_blueprint(stats.stats_bp, url_prefix='/api')
    app.register_blueprint(health.health_bp, url_prefix='/api')
    try:
        from app.routes import players
        app.register_blueprint(players.players_bp, url_prefix='/api/players')
    except Exception as e:  # pragma: no cover
        logger.error(f"球员路由注册失败: {e}")

    register_error_handlers(app)
    return app

