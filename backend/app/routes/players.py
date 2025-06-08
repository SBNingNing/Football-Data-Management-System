from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.player import Player
from app.models.player_team_history import PlayerTeamHistory
from app.models.tournament import Tournament
import traceback

players_bp = Blueprint('players', __name__)

@players_bp.route('', methods=['GET'])
def get_players():
    """获取所有球员信息（公共接口）"""
    try:
        players = Player.query.all()
        players_data = []
        
        for player in players:
            try:
                # 验证player对象是否有效
                if not player or not hasattr(player, 'id') or not hasattr(player, 'name'):
                    print(f"跳过无效的球员对象: {player}")
                    continue
                
                player_dict = player.to_dict()
                
                # 安全地初始化默认值
                player_dict.setdefault('teamName', None)
                player_dict.setdefault('team_id', None)
                player_dict.setdefault('number', None)
                player_dict.setdefault('matchType', 'champions-cup')
                player_dict.setdefault('studentId', player.id)
                
                # 获取球员当前队伍信息（最新的一条记录）
                try:
                    current_history = PlayerTeamHistory.query.filter_by(
                        player_id=player.id
                    ).order_by(PlayerTeamHistory.id.desc()).first()
                    
                    if current_history:
                        # 安全地获取team信息
                        if hasattr(current_history, 'team') and current_history.team:
                            player_dict['teamName'] = getattr(current_history.team, 'name', None)
                            player_dict['team_id'] = getattr(current_history, 'team_id', None)
                        
                        player_dict['number'] = getattr(current_history, 'player_number', None)
                        
                        # 根据tournament_id确定matchType
                        tournament_id = getattr(current_history, 'tournament_id', None)
                        if tournament_id:
                            try:
                                tournament = Tournament.query.get(tournament_id)
                                if tournament and hasattr(tournament, 'name') and tournament.name:
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
                            except Exception as tournament_error:
                                print(f"获取tournament信息时出错: {str(tournament_error)}")
                                
                except Exception as history_error:
                    print(f"获取球员 {player.id} 历史记录时出错: {str(history_error)}")
                
                players_data.append(player_dict)
                
            except Exception as player_error:
                # 如果单个球员处理失败，记录错误但继续处理其他球员
                print(f"处理球员 {getattr(player, 'id', 'unknown') if player else 'unknown'} 时出错: {str(player_error)}")
                traceback.print_exc()
                continue
        
        return jsonify({
            'status': 'success', 
            'data': players_data,
            'total': len(players_data)
        }), 200
        
    except Exception as e:
        print(f"获取球员列表失败: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'status': 'error', 
            'message': f'获取球员信息失败: {str(e)}',
            'data': []
        }), 500

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
        # 验证输入参数
        if not player_id:
            return jsonify({'status': 'error', 'message': '球员ID不能为空'}), 400
        
        player = Player.query.get(player_id)
        if not player:
            return jsonify({'status': 'error', 'message': '球员不存在'}), 404
        
        player_dict = player.to_dict()
        
        # 安全地初始化默认值
        player_dict.setdefault('team_histories', [])
        player_dict.setdefault('seasons', [])
        
        try:
            # 获取球员所有的队伍历史信息
            all_histories = PlayerTeamHistory.query.filter_by(player_id=player.id).all()
            
            # 组织球员的所有队伍信息
            team_histories = []
            seasons_data = {}  # 按赛季分组的数据
            
            for history in all_histories:
                try:
                    # 验证history对象
                    if not history or not hasattr(history, 'team'):
                        continue
                    
                    # 获取赛事信息
                    tournament = None
                    if hasattr(history, 'tournament_id') and history.tournament_id:
                        tournament = Tournament.query.get(history.tournament_id)
                    
                    team_info = {
                        'team_name': getattr(history.team, 'name', None) if history.team else None,
                        'team_id': getattr(history, 'team_id', None),
                        'player_number': getattr(history, 'player_number', None),
                        'tournament_id': getattr(history, 'tournament_id', None),
                        'tournament_name': getattr(tournament, 'name', None) if tournament else None,
                        'season_name': getattr(tournament, 'season_name', None) if tournament else None
                    }
                    
                    # 根据赛事名称确定matchType
                    if tournament and hasattr(tournament, 'name') and tournament.name:
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
                        if season_key and season_key not in seasons_data:
                            seasons_data[season_key] = {
                                'season_name': season_key,
                                'tournaments': {}
                            }
                        
                        if season_key and tournament.name not in seasons_data[season_key]['tournaments']:
                            seasons_data[season_key]['tournaments'][tournament.name] = {
                                'tournament_name': tournament.name,
                                'match_type': match_type,
                                'teams': []
                            }
                        
                        if season_key:
                            seasons_data[season_key]['tournaments'][tournament.name]['teams'].append({
                                'team_name': team_info['team_name'],
                                'team_id': team_info['team_id'],
                                'player_number': team_info['player_number'],
                                'tournament_goals': getattr(history, 'tournament_goals', 0),
                                'tournament_red_cards': getattr(history, 'tournament_red_cards', 0),
                                'tournament_yellow_cards': getattr(history, 'tournament_yellow_cards', 0)
                            })
                    else:
                        team_info['matchType'] = 'champions-cup'
                    
                    team_histories.append(team_info)
                    
                except Exception as history_process_error:
                    print(f"处理球员历史记录时出错: {str(history_process_error)}")
                    continue
            
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
        
        except Exception as histories_error:
            print(f"获取球员历史记录时出错: {str(histories_error)}")
            # 设置默认值，确保API仍能返回基本的球员信息
            player_dict['team_histories'] = []
            player_dict['seasons'] = []
        
        return jsonify({'status': 'success', 'data': player_dict}), 200
        
    except Exception as e:
        print(f"获取球员详情失败: {str(e)}")
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': f'获取球员信息失败: {str(e)}'}), 500
