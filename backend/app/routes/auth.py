from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 验证必填字段
    if not data or not all(k in data for k in ('username', 'password', 'email')):
        return jsonify({'error': '缺少必要信息'}), 400
        
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(用户名=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
        
    if User.query.filter_by(邮箱=data['email']).first():
        return jsonify({'error': '邮箱已被注册'}), 400
    
    # 创建新用户
    new_user = User(
        用户名=data['username'],
        邮箱=data['email'],
        身份_角色='user',
        创建时间=datetime.utcnow(),
        状态='A'
    )
    new_user.set_password(data['password'])
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': '注册成功', 'user_id': new_user.用户ID}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'注册失败: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'password')):
        return jsonify({'error': '请提供用户名和密码'}), 400
    
    user = User.query.filter_by(用户名=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    if user.状态 != 'A':
        return jsonify({'error': '账号已被禁用'}), 403
    
    # 更新登录时间
    user.最后登录时间 = datetime.utcnow()
    db.session.commit()
    
    # 创建JWT令牌
    access_token = create_access_token(identity=user.用户ID)
    
    return jsonify({
        'message': '登录成功',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
        
    return jsonify(user.to_dict()), 200

@auth_bp.route('/guest-login', methods=['POST'])
def guest_login():
    try:
        # 创建游客身份令牌
        access_token = create_access_token(identity='guest')
        return jsonify({
            'message': '游客登录成功',
            'access_token': access_token,
            'user': {
                'username': 'guest',
                'role': 'guest'
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'游客登录失败: {str(e)}'}), 500
