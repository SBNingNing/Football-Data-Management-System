from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import auth_required
from app.middleware.validation_middleware import validate_json, validate_user_data
from app.schemas import RegisterIn, LoginIn, LoginOut, RegisterOut, GuestLoginOut, UserView, GuestUserView

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@validate_json(['username', 'password', 'email'])
@validate_user_data
def register():
    """用户注册"""
    payload = RegisterIn(**(request.get_json() or {}))
    
    user, error = AuthService.register_user(
        username=payload.username,
        email=payload.email,
        password=payload.password
    )
    
    if error:
        return jsonify({'error': error}), 400
        
    out = RegisterOut(user_id=user.用户ID)
    return jsonify(out.model_dump(by_alias=True)), 201

@auth_bp.route('/register-admin', methods=['POST'])
@validate_json(['username', 'password', 'email'])
@validate_user_data
def register_admin():
    """管理员注册 - 直接创建管理员账号"""
    payload = RegisterIn(**(request.get_json() or {}))
    
    # 使用 AuthService 创建管理员账号
    user, error = AuthService.register_user(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        role='admin'  # 明确指定为管理员角色
    )
    
    if error:
        return jsonify({'error': error}), 400
        
    out = RegisterOut(user_id=user.用户ID)
    return jsonify(out.model_dump(by_alias=True)), 201

@auth_bp.route('/login', methods=['POST'])
@validate_json(['username', 'password'])
def login():
    """用户登录"""
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    payload = LoginIn(**(request.get_json() or {}))
    
    logger.info(f"Login attempt for user: {payload.username}")
    
    # 认证用户
    user, error = AuthService.authenticate_user(
        username=payload.username,
        password=payload.password
    )
    
    if error:
        status_code = 401 if '密码错误' in error or '用户名不存在' in error else 403
        logger.warning(f"Login failed for {payload.username}: {error}")
        generic_error = "用户名或密码错误"
        return jsonify({'error': generic_error, 'message': generic_error}), status_code
    
    # 确定令牌类型（为未来分离做准备）
    token_type = 'admin' if user.身份_角色 == 'admin' else 'user'
    
    # 创建令牌
    access_token, token_error = AuthService.create_token(user.用户ID, token_type)
    if token_error:
        logger.error(f"Token creation failed for {user.用户名}: {token_error}")
        return jsonify({'error': token_error}), 500
    
    out = LoginOut(access_token=access_token, user=UserView(**user.to_dict()))
    logger.info(f"Login successful for {user.用户名} (role: {user.身份_角色})")
    return jsonify(out.model_dump(by_alias=True)), 200

@auth_bp.route('/guest-login', methods=['POST'])
def guest_login():
    """游客登录"""
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    logger.info("Guest login attempt")
    
    # 调用服务层处理游客登录
    guest_user, access_token, error = AuthService.guest_login()
    
    if error:
        logger.error(f"Guest login failed: {error}")
        return jsonify({'error': error}), 500
        
    # 使用 Pydantic 模型格式化输出
    out = GuestLoginOut(
        access_token=access_token,
        user=GuestUserView(**guest_user)
    )
    
    logger.info("Guest login successful")
    return jsonify(out.model_dump(by_alias=True)), 200

@auth_bp.route('/me', methods=['GET'])
@auth_required
def get_current_user():
    """获取当前用户信息"""
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        user_id = get_jwt_identity()
        logger.info(f"Fetching user info for ID: {user_id}")
        
        user, error = AuthService.get_user_by_id(user_id)
        if error:
            logger.error(f"Failed to get user {user_id}: {error}")
            return jsonify({
                'error': error,
                'message': '获取用户信息失败',
                'status': 'error'
            }), 404
        
        # 如果是注册用户，返回完整信息；如果是游客，返回基本信息
        if isinstance(user, dict):  # 游客用户
            guest = GuestUserView(**user)
            logger.info(f"Returning guest user info")
            return jsonify(guest.model_dump(by_alias=True)), 200
        else:  # 注册用户
            view = UserView(**user.to_dict())
            logger.info(f"Returning registered user info for {user.用户名}")
            return jsonify(view.model_dump(by_alias=True)), 200
    except Exception as e:
        logger.error(f"Exception in get_current_user: {str(e)}", exc_info=True)
        return jsonify({
            'error': '服务器内部错误',
            'message': str(e),
            'status': 'error'
        }), 500

