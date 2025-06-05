from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.player import Player
from app.models.player_team_history import PlayerTeamHistory
from app.models.tournament import Tournament

players_bp = Blueprint('players', __name__)

@players_bp.route('', methods=['GET'])
def get_players():
    """获取所有球员信息（公共接口）"""
    try:
        players = Player.query.all()
        players_data = []
        
        for player in players:
            player_dict = player.to_dict()
            
            # 获取球员所有队伍信息
            current_history = PlayerTeamHistory.query.filter_by(player_id=player.id).first()
            if current_history:
                player_dict['team_name'] = current_history.team.name
                player_dict['team_id'] = current_history.team_id
                player_dict['player_number'] = current_history.player_number
                
                # 根据tournament_id确定matchType
                tournament_to_match_type = {1: 'champions-cup', 2: 'womens-cup', 3: 'eight-a-side'}
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

@players_bp.route('', methods=['POST'])
@jwt_required()
def create_player():
    """创建球员信息"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('studentId'):
        return jsonify({'status': 'error', 'message': '球员姓名和学号不能为空'}), 400
    
    try:
        player_id = data['studentId']
        
        # 检查球员是否已存在
        existing_player = Player.query.get(player_id)
        if existing_player:
            return jsonify({'status': 'error', 'message': '球员已存在'}), 400
        
        # 创建新球员
        new_player = Player(
            id=player_id,
            name=data['name']
        )
        db.session.add(new_player)
        db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': '球员创建成功',
            'data': new_player.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500

@players_bp.route('/<string:player_id>', methods=['PUT'])
@jwt_required()
def update_player(player_id):
    """更新球员信息"""
    data = request.get_json()
    
    try:
        player = Player.query.get(player_id)
        if not player:
            return jsonify({'status': 'error', 'message': '球员不存在'}), 404
        
        # 更新球员信息
        if data.get('name'):
            player.name = data['name']
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': '更新成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500

@players_bp.route('/<string:player_id>', methods=['DELETE'])
@jwt_required()
def delete_player(player_id):
    """删除球员"""
    try:
        player = Player.query.get(player_id)
        if not player:
            return jsonify({'status': 'error', 'message': '球员不存在'}), 404
        
        # 删除关联的球员-队伍历史记录
        PlayerTeamHistory.query.filter_by(player_id=player_id).delete()
        
        # 删除球员
        db.session.delete(player)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': '删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500

@players_bp.route('/<string:player_id>', methods=['GET'])
def get_player(player_id):
    """获取单个球员信息"""
    try:
        player = Player.query.get(player_id)
        if not player:
            return jsonify({'status': 'error', 'message': '球员不存在'}), 404
        
        player_dict = player.to_dict()
        
        # 获取球员所有的队伍历史信息
        all_histories = PlayerTeamHistory.query.filter_by(player_id=player.id).all()
        
        # 组织球员的所有队伍信息
        team_histories = []
        seasons_data = {}  # 按赛季分组的数据
        
        for history in all_histories:
            # 获取赛事信息
            tournament = Tournament.query.get(history.tournament_id)
            
            team_info = {
                'team_name': history.team.name,
                'team_id': history.team_id,
                'player_number': history.player_number,
                'tournament_id': history.tournament_id,
                'tournament_name': tournament.name if tournament else None,
                'season_name': tournament.season_name if tournament else None
            }
            
            # 根据赛事名称确定matchType
            if tournament:
                tournament_name = tournament.name.lower()
                if '冠军杯' in tournament_name or 'champions' in tournament_name:
                    match_type = 'champions-cup'
                elif '巾帼杯' in tournament_name or 'womens' in tournament_name:
                    match_type = 'womens-cup'
                elif '八人制' in tournament_name or 'eight' in tournament_name:
                    match_type = 'eight-a-side'
                else:
                    match_type = 'champions-cup'
                
                team_info['matchType'] = match_type
                
                # 按赛季分组数据
                season_key = tournament.season_name
                if season_key not in seasons_data:
                    seasons_data[season_key] = {
                        'season_name': season_key,
                        'tournaments': {}
                    }
                
                if tournament.name not in seasons_data[season_key]['tournaments']:
                    seasons_data[season_key]['tournaments'][tournament.name] = {
                        'tournament_name': tournament.name,
                        'match_type': match_type,
                        'teams': []
                    }
                
                seasons_data[season_key]['tournaments'][tournament.name]['teams'].append({
                    'team_name': history.team.name,
                    'team_id': history.team_id,
                    'player_number': history.player_number,
                    'tournament_goals': history.tournament_goals,
                    'tournament_red_cards': history.tournament_red_cards,
                    'tournament_yellow_cards': history.tournament_yellow_cards
                })
            else:
                team_info['matchType'] = 'champions-cup'
            
            team_histories.append(team_info)
        
        # 计算每个赛季的总统计数据
        for season_name, season_data in seasons_data.items():
            season_total_goals = 0
            season_total_yellow_cards = 0
            season_total_red_cards = 0
            
            for tournament_data in season_data['tournaments'].values():
                for team_data in tournament_data['teams']:
                    season_total_goals += team_data.get('tournament_goals', 0)
                    season_total_yellow_cards += team_data.get('tournament_yellow_cards', 0)
                    season_total_red_cards += team_data.get('tournament_red_cards', 0)
            
            season_data['total_goals'] = season_total_goals
            season_data['total_yellow_cards'] = season_total_yellow_cards
            season_data['total_red_cards'] = season_total_red_cards
        
        # 添加所有队伍历史信息到返回数据
        player_dict['team_histories'] = team_histories
        player_dict['seasons'] = list(seasons_data.values())
        
        # 保留当前队伍信息（最近的一条记录）
        current_history = all_histories[0] if all_histories else None
        if current_history:
            tournament = Tournament.query.get(current_history.tournament_id)
            player_dict['team_name'] = current_history.team.name
            player_dict['team_id'] = current_history.team_id
            player_dict['player_number'] = current_history.player_number
            player_dict['tournament_name'] = tournament.name if tournament else None
            player_dict['season_name'] = tournament.season_name if tournament else None
            
            # 根据赛事名称确定matchType
            if tournament:
                tournament_name = tournament.name.lower()
                if '冠军杯' in tournament_name or 'champions' in tournament_name:
                    match_type = 'champions-cup'
                elif '巾帼杯' in tournament_name or 'womens' in tournament_name:
                    match_type = 'womens-cup'
                elif '八人制' in tournament_name or 'eight' in tournament_name:
                    match_type = 'eight-a-side'
                else:
                    match_type = 'champions-cup'
                
                player_dict['matchType'] = match_type
            else:
                player_dict['matchType'] = 'champions-cup'
        else:
            player_dict['team_name'] = None
            player_dict['team_id'] = None
            player_dict['player_number'] = None
            player_dict['tournament_name'] = None
            player_dict['season_name'] = None
            player_dict['matchType'] = 'champions-cup'
        
        return jsonify({'status': 'success', 'data': player_dict}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500
