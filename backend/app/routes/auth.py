from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.team import Team
from app.models.player import Player
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
            'access_token': access_token
        }), 200
    except Exception as e:
        return jsonify({'error': f'游客登录失败: {str(e)}'}), 500

@auth_bp.route('/teams', methods=['POST'])
@jwt_required()
def create_team():
    """创建球队和球员信息"""
    data = request.get_json()
    
    if not data or not data.get('teamName'):
        return jsonify({'status': 'error', 'message': '球队名称不能为空'}), 400
    
    # 检查球队名称是否已存在
    existing_team = Team.query.filter_by(name=data['teamName']).first()
    if existing_team:
        return jsonify({'status': 'error', 'message': '球队名称已存在'}), 400
    
    try:
        # 创建球队
        new_team = Team(
            name=data['teamName'],
            tournament_id=1,  # 根据matchType设置对应的赛事ID
            season_id=1       # 当前赛季ID
        )
        db.session.add(new_team)
        db.session.flush()  # 获取球队ID
        
        # 创建球员
        players_data = data.get('players', [])
        for player_data in players_data:
            if player_data.get('name') and player_data.get('number'):
                new_player = Player(
                    name=player_data['name'],
                    gender='M',  # 默认性别，可根据比赛类型调整
                    team_id=new_team.id,
                    season_id=1
                )
                db.session.add(new_player)
        
        db.session.commit()
        
        # 返回创建成功的球队信息
        team_dict = new_team.to_dict()
        team_dict['teamName'] = team_dict['name']  # 前端期望的字段名
        team_dict['players'] = [{'name': p.name, 'number': str(p.id)} for p in 
                               Player.query.filter_by(team_id=new_team.id).all()]
        team_dict['matchType'] = data.get('matchType', 'champions-cup')
        
        return jsonify({
            'status': 'success', 
            'message': '球队创建成功',
            'data': team_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500

@auth_bp.route('/teams', methods=['GET'])
@jwt_required()
def get_teams():
    """获取所有球队信息"""
    try:
        teams = Team.query.all()
        teams_data = []
        
        for team in teams:
            team_dict = team.to_dict()
            # 添加前端期望的字段名
            team_dict['teamName'] = team_dict['name']
            # 添加球员信息
            players = Player.query.filter_by(team_id=team.id).all()
            team_dict['players'] = [{'name': p.name, 'number': str(p.id)} for p in players]
            team_dict['matchType'] = 'champions-cup'  # 根据实际业务逻辑设置
            teams_data.append(team_dict)
        
        return jsonify({'status': 'success', 'data': teams_data}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

@auth_bp.route('/teams/<int:team_id>', methods=['PUT'])
@jwt_required()
def update_team(team_id):
    """更新球队信息"""
    data = request.get_json()
    
    try:
        team = Team.query.get(team_id)
        if not team:
            return jsonify({'status': 'error', 'message': '球队不存在'}), 404
        
        # 更新球队信息
        if data.get('teamName'):
            team.name = data['teamName']
        
        # 删除原有球员
        Player.query.filter_by(team_id=team_id).delete()
        
        # 添加新球员
        players_data = data.get('players', [])
        for player_data in players_data:
            if player_data.get('name'):
                new_player = Player(
                    name=player_data['name'],
                    gender='M',
                    team_id=team_id,
                    season_id=1
                )
                db.session.add(new_player)
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': '更新成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500

@auth_bp.route('/teams/<int:team_id>', methods=['DELETE'])
@jwt_required()
def delete_team(team_id):
    """删除球队"""
    try:
        team = Team.query.get(team_id)
        if not team:
            return jsonify({'status': 'error', 'message': '球队不存在'}), 404
        
        # 删除关联的球员
        Player.query.filter_by(team_id=team_id).delete()
        
        # 删除球队
        db.session.delete(team)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': '删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500

@auth_bp.route('/players', methods=['GET'])
@jwt_required()
def get_players():
    """获取所有球员信息"""
    try:
        players = Player.query.all()
        players_data = []
        
        for player in players:
            player_dict = player.to_dict()
            player_dict['matchType'] = 'champions-cup'  # 根据实际业务逻辑设置
            players_data.append(player_dict)
        
        return jsonify({'status': 'success', 'data': players_data}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500
