from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import auth_required
from app.middleware.validation_middleware import validate_json, validate_user_data

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@validate_json(['username', 'password', 'email'])
@validate_user_data
def register():
    """用户注册"""
    data = request.get_json()
    
    user, error = AuthService.register_user(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )
    
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify({
        'message': '注册成功', 
        'user_id': user.用户ID
    }), 201

@auth_bp.route('/login', methods=['POST'])
@validate_json(['username', 'password'])
def login():
    """用户登录"""
    data = request.get_json()
    
    # 认证用户
    user, error = AuthService.authenticate_user(
        username=data['username'],
        password=data['password']
    )
    
    if error:
        status_code = 401 if '密码错误' in error or '用户名不存在' in error else 403
        return jsonify({'error': error}), status_code
    
    # 创建令牌
    access_token, token_error = AuthService.create_token(user.用户ID)
    if token_error:
        return jsonify({'error': token_error}), 500
    
    return jsonify({
        'message': '登录成功',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

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
        return jsonify(user), 200
    else:  # 注册用户
        return jsonify(user.to_dict()), 200

@auth_bp.route('/guest-login', methods=['POST'])
def guest_login():
    """游客登录"""
    access_token, error = AuthService.create_guest_token()
    
    if error:
        return jsonify({'error': error}), 500
        
    return jsonify({
        'message': '游客登录成功',
        'access_token': access_token,
        'user': {
            'username': 'guest',
            'role': 'guest'
        }
    }), 200
