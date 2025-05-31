from app import db
from datetime import datetime
import bcrypt

class User(db.Model):
    __tablename__ = 'user'
    
    用户ID = db.Column('用户ID', db.Integer, primary_key=True)
    用户名 = db.Column('用户名', db.String(100), unique=True, nullable=False)
    密码 = db.Column('密码', db.String(100), nullable=False)
    邮箱 = db.Column('邮箱', db.String(100), unique=True, nullable=False)
    身份_角色 = db.Column('身份/角色', db.String(20), default='user')
    创建时间 = db.Column('创建时间', db.DateTime, default=datetime.utcnow)
    最后登录时间 = db.Column('最后登录时间', db.DateTime)
    状态 = db.Column('状态', db.CHAR(1), default='A')  # A=活跃, I=禁用
    
    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.密码 = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.密码.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.用户ID,
            'username': self.用户名,
            'email': self.邮箱,
            'role': self.身份_角色,
            'status': self.状态,
            'created_at': self.创建时间.isoformat() if self.创建时间 else None,
            'last_login': self.最后登录时间.isoformat() if self.最后登录时间 else None
        }
