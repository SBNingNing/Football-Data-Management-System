from datetime import datetime
from flask_jwt_extended import create_access_token
from app.database import db
from app.models.user import User
from app.utils.logging_config import get_logger
from app.middleware.error_middleware import log_error, log_security_event

logger = get_logger(__name__)


class AuthService:
    """认证服务类"""
    
    @staticmethod
    def register_user(username, email, password, role='user'):
        """注册新用户"""
        try:
            logger.info(f"Registering user: {username}")
            
            # 检查用户名和邮箱是否已存在
            if User.query.filter_by(用户名=username).first():
                logger.warning(f"Username exists: {username}")
                return None, '用户名已存在'
                
            if User.query.filter_by(邮箱=email).first():
                logger.warning(f"Email exists: {email}")
                return None, '邮箱已被注册'
            
            # 创建用户
            new_user = User(
                用户名=username, 邮箱=email, 身份_角色=role,
                创建时间=datetime.utcnow(), 状态='A'
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            logger.info(f"User registered: {username} (ID: {new_user.用户ID})")
            log_security_event("USER_REGISTERED", username, new_user.用户ID)
            
            return new_user, None
            
        except Exception as e:
            db.session.rollback()
            log_error(e, f"Registration failed: {username}")
            return None, f'注册失败: {str(e)}'
    
    @staticmethod
    def authenticate_user(username, password):
        """用户认证"""
        try:
            logger.debug(f"Authenticating: {username}")
            user = User.query.filter_by(用户名=username).first()
            
            # 验证用户存在性、密码、状态
            checks = [
                (not user, '用户名不存在', "User not found"),
                (user and not user.check_password(password), '密码错误', "Wrong password"),
                (user and user.状态 != 'A', '账号已被禁用', "Account disabled")
            ]
            
            for condition, error_msg, log_msg in checks:
                if condition:
                    logger.warning(f"Auth failed - {log_msg}: {username}")
                    log_security_event("LOGIN_FAILED", f"{log_msg}: {username}", 
                                     user.用户ID if user else None)
                    return None, error_msg
            
            # 更新登录时间
            user.最后登录时间 = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"User authenticated: {username}")
            log_security_event("LOGIN_SUCCESS", username, user.用户ID)
            
            return user, None
            
        except Exception as e:
            log_error(e, f"Authentication error: {username}")
            return None, f'登录失败: {str(e)}'
    
    @staticmethod
    def create_token(user_id):
        """创建JWT令牌"""
        try:
            token = create_access_token(identity=user_id)
            logger.debug(f"Token created for: {user_id}")
            return token, None
        except Exception as e:
            log_error(e, f"Token creation failed: {user_id}")
            return None, f'令牌创建失败: {str(e)}'
    
    @staticmethod
    def get_user_by_id(user_id):
        """根据ID获取用户"""
        try:
            if user_id == 'guest':
                return {'username': 'guest', 'role': 'guest'}, None
                
            user = User.query.get(user_id)
            if not user:
                logger.warning(f"User not found: {user_id}")
                return None, '用户不存在'
            
            return user, None
            
        except Exception as e:
            log_error(e, f"Get user failed: {user_id}")
            return None, f'获取用户信息失败: {str(e)}'
    
    @staticmethod
    def create_guest_token():
        """创建游客令牌"""
        try:
            token = create_access_token(identity='guest')
            logger.info("Guest token created")
            log_security_event("GUEST_LOGIN", "Guest access")
            return token, None
        except Exception as e:
            log_error(e, "Guest token creation failed")
            return None, f'游客登录失败: {str(e)}'
