from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# 初始化扩展
CORS(app)
db.init_app(app)
jwt = JWTManager(app)

# 替换已弃用的 before_first_request 装饰器
with app.app_context():
    db.create_all()

# 用户登录
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'msg': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.verify_password(password):
        access_token = create_access_token(identity=username)
        return jsonify({
            'msg': '登录成功',
            'access_token': access_token,
            'username': username
        })
    
    return jsonify({'msg': '用户名或密码错误'}), 401

# 用户注册
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'msg': '用户名和密码不能为空'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'msg': '用户名已存在'}), 400
    
    user = User(username=username)
    user.password = password
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'msg': '注册成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': '注册失败', 'error': str(e)}), 500

# 受保护的路由示例
@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'logged_in_as': current_user})

if __name__ == '__main__':
    app.run(debug=True)
