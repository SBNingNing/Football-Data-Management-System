from app.database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """用户表 - 存储用户账号信息"""
    __tablename__ = 'user'
    
    # 主键 - 使用中文字段名匹配数据库
    用户ID = db.Column('用户ID', db.Integer, primary_key=True, comment='用户ID')
    
    # 用户信息 - 使用中文字段名匹配数据库
    用户名 = db.Column('用户名', db.String(50), unique=True, nullable=False, comment='用户名')
    密码 = db.Column('密码', db.String(255), nullable=False, comment='加密存储的用户密码')
    邮箱 = db.Column('邮箱', db.String(100), unique=True, nullable=False, comment='用户邮箱地址')
    身份_角色 = db.Column('身份角色', db.String(20), nullable=False, default='user', comment='用户身份类型')
    创建时间 = db.Column('创建时间', db.DateTime, default=datetime.utcnow, comment='账户创建时间')
    最后登录时间 = db.Column('最后登录时间', db.DateTime, comment='最后登录时间')
    状态 = db.Column('状态', db.String(1), default='A', comment='账户状态(A: 启用, D: 禁用)')
    
    # 约束 - 匹配SQL定义
    __table_args__ = (
        db.CheckConstraint("状态 in ('A','D')", name='user_chk_1'),
    )
    
    def __repr__(self):
        return f'<User {self.用户名}>'
    
    def set_password(self, password):
        """设置用户密码"""
        self.密码 = generate_password_hash(password)
        
    def check_password(self, password):
        """验证用户密码"""
        return check_password_hash(self.密码, password)
    
    def to_dict(self, exclude_sensitive=True):
        """将对象转换为字典，便于API返回JSON"""
        data = {
            'user_id': self.用户ID,
            'username': self.用户名,
            'email': self.邮箱,
            'role': self.身份_角色,
            'created_at': self.创建时间.isoformat() if self.创建时间 else None,
            'last_login': self.最后登录时间.isoformat() if self.最后登录时间 else None,
            'status': self.状态
        }
        # 排除敏感信息
        if not exclude_sensitive:
            data['password_hash'] = self.密码
            
        return data
