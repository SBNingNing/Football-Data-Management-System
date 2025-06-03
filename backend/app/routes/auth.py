from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.team import Team
from app.models.player import Player
from app.models.player_team_history import PlayerTeamHistory
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
        # 根据matchType确定赛事ID
        match_type_to_tournament = {
            'champions-cup': 1,  # 冠军杯
            'women-cup': 2,      # 巾帼杯
            'eight-man': 3       # 八人制比赛
        }
        tournament_id = match_type_to_tournament.get(data.get('matchType', 'champions-cup'), 1)
        
        # 创建球队
        new_team = Team(
            name=data['teamName'],
            tournament_id=tournament_id,
            group_id=data.get('groupId')  # 如果有分组信息
        )
        db.session.add(new_team)
        db.session.flush()  # 获取球队ID
        
        # 创建球员和球员-队伍历史记录
        players_data = data.get('players', [])
        for i, player_data in enumerate(players_data):
            if player_data.get('name'):
                # 生成球员ID（使用简单的格式，实际应该是学号）
                player_id = f"STU{new_team.id:03d}{i+1:02d}"
                
                # 检查球员是否已存在
                existing_player = Player.query.get(player_id)
                if not existing_player:
                    # 创建新球员
                    new_player = Player(
                        id=player_id,
                        name=player_data['name']
                    )
                    db.session.add(new_player)
                
                # 创建球员-队伍历史记录
                player_history = PlayerTeamHistory(
                    player_id=player_id,
                    player_number=player_data.get('number', i+1),
                    team_id=new_team.id,
                    tournament_id=tournament_id
                )
                db.session.add(player_history)
        
        db.session.commit()
        
        # 返回创建成功的球队信息
        team_dict = new_team.to_dict()
        team_dict['teamName'] = team_dict['name']
        
        # 获取球员信息
        team_players = []
        for history in PlayerTeamHistory.query.filter_by(team_id=new_team.id, tournament_id=tournament_id).all():
            team_players.append({
                'name': history.player.name,
                'number': str(history.player_number),
                'id': history.player_id
            })
        
        team_dict['players'] = team_players
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
            team_dict['teamName'] = team_dict['name']
            
            # 获取球队在当前赛事中的球员
            team_players = []
            for history in team.player_histories:
                team_players.append({
                    'name': history.player.name,
                    'number': str(history.player_number),
                    'id': history.player_id
                })
            
            team_dict['players'] = team_players
            
            # 根据tournament_id确定matchType
            tournament_to_match_type = {1: 'champions-cup', 2: 'women-cup', 3: 'eight-man'}
            team_dict['matchType'] = tournament_to_match_type.get(team.tournament_id, 'champions-cup')
            
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
        
        # 删除原有的球员-队伍历史记录
        PlayerTeamHistory.query.filter_by(team_id=team_id, tournament_id=team.tournament_id).delete()
        
        # 添加新的球员和历史记录
        players_data = data.get('players', [])
        for i, player_data in enumerate(players_data):
            if player_data.get('name'):
                # 如果提供了player_id则使用，否则生成新的
                player_id = player_data.get('id') or f"STU{team_id:03d}{i+1:02d}"
                
                # 检查球员是否已存在
                existing_player = Player.query.get(player_id)
                if not existing_player:
                    new_player = Player(
                        id=player_id,
                        name=player_data['name']
                    )
                    db.session.add(new_player)
                else:
                    # 更新球员姓名
                    existing_player.name = player_data['name']
                
                # 创建新的球员-队伍历史记录
                player_history = PlayerTeamHistory(
                    player_id=player_id,
                    player_number=player_data.get('number', i+1),
                    team_id=team_id,
                    tournament_id=team.tournament_id
                )
                db.session.add(player_history)
        
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
        
        # 删除关联的球员-队伍历史记录
        PlayerTeamHistory.query.filter_by(team_id=team_id).delete()
        
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
            
            # 获取球员当前的队伍信息
            current_history = PlayerTeamHistory.query.filter_by(player_id=player.id).first()
            if current_history:
                player_dict['team_name'] = current_history.team.name
                player_dict['team_id'] = current_history.team_id
                player_dict['player_number'] = current_history.player_number
                
                # 根据tournament_id确定matchType
                tournament_to_match_type = {1: 'champions-cup', 2: 'women-cup', 3: 'eight-man'}
                player_dict['matchType'] = tournament_to_match_type.get(current_history.tournament_id, 'champions-cup')
            else:
                player_dict['team_name'] = None
                player_dict['team_id'] = None
                player_dict['player_number'] = None
                player_dict['matchType'] = 'champions-cup'
            
            players_data.append(player_dict)
        
        return jsonify({'status': 'success', 'data': players_data}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500
