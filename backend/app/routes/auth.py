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

@auth_bp.route('/login', methods=['POST'])
@validate_json(['username', 'password'])
def login():
    """用户登录"""
    payload = LoginIn(**(request.get_json() or {}))
    
    # 认证用户
    user, error = AuthService.authenticate_user(
        username=payload.username,
        password=payload.password
    )
    
    if error:
        status_code = 401 if '密码错误' in error or '用户名不存在' in error else 403
        return jsonify({'error': error}), status_code
    
    # 创建令牌
    access_token, token_error = AuthService.create_token(user.用户ID)
    if token_error:
        return jsonify({'error': token_error}), 500
    
    out = LoginOut(access_token=access_token, user=UserView(**user.to_dict()))
    return jsonify(out.model_dump(by_alias=True)), 200

@auth_bp.route('/me', methods=['GET'])
@auth_required
def get_current_user():
    """获取当前用户信息"""
    user_id = get_jwt_identity()
    
    user, error = AuthService.get_user_by_id(user_id)
    if error:
        return jsonify({'error': error}), 404
    
    # 如果是注册用户，返回完整信息；如果是游客，返回基本信息
    if isinstance(user, dict):  # 游客用户
        guest = GuestUserView(**user)
        return jsonify(guest.model_dump(by_alias=True)), 200
    else:  # 注册用户
        view = UserView(**user.to_dict())
        return jsonify(view.model_dump(by_alias=True)), 200

@auth_bp.route('/guest-login', methods=['POST'])
def guest_login():
    """游客登录"""
    access_token, error = AuthService.create_guest_token()
    
    if error:
        return jsonify({'error': error}), 500
        
    out = GuestLoginOut(access_token=access_token)
    return jsonify(out.model_dump(by_alias=True)), 200
