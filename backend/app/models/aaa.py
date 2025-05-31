from app import create_app
from app.models import db, User, Player, Team, Match, Event, Tournament, Season
import os

app = create_app()

def init_db():
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否存在管理员用户
        admin = User.query.filter_by(username='admin').first()
        if admin is None:
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin',
                status='A'
            )
            admin.password = 'admin123'  # 设置初始密码
            db.session.add(admin)
            
        # 提交会话
        db.session.commit()
        print('数据库初始化完成!')

if __name__ == '__main__':
    init_db()