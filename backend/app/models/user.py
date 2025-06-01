from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """用户表 - 存储用户账号信息"""
    __tablename__ = 'user'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, comment='用户ID')
    
    # 用户信息
    username = db.Column(db.String(80), unique=True, nullable=False, comment='用户名')
    password_hash = db.Column(db.String(128), nullable=False, comment='加密存储的用户密码')
    email = db.Column(db.String(120), unique=True, nullable=False, comment='用户邮箱地址')
    role = db.Column(db.String(50), nullable=False, default='user', comment='用户身份类型(admin, recorder, user等)')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='账户创建时间')
    last_login = db.Column(db.DateTime, default=datetime.utcnow, comment='最后登录时间')
    status = db.Column(db.String(1), default='A', comment='账户状态(A: 启用, D: 禁用)')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """设置用户密码"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """验证用户密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, exclude_sensitive=True):
        """将对象转换为字典，便于API返回JSON"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'status': self.status
        }
        # 排除敏感信息
        if not exclude_sensitive:
            data['password_hash'] = self.password_hash
            
        return data
