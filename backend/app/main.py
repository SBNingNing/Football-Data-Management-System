from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.models import db, migrate

def create_app():
    app = Flask(__name__, static_url_path='/static')
    
    # CORS 设置
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # JWT 设置
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # 更改为你的密钥
    jwt = JWTManager(app)
    
    # 数据库设置
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost:3306/football_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.teams import teams_bp
    from app.routes.matches import matches_bp
    from app.routes.events import events_bp
    from app.routes.players import players_bp  # 确保导入球员路由
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(teams_bp, url_prefix='/api/teams')
    app.register_blueprint(matches_bp, url_prefix='/api/matches')
    app.register_blueprint(events_bp, url_prefix='/api/events')
    app.register_blueprint(players_bp, url_prefix='/api/players')  # 确保注册球员路由
    
    return app