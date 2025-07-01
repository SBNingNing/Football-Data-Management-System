from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.match import Match
from app.models.team import Team
from app.models.tournament import Tournament
from datetime import datetime
import pytz
from sqlalchemy import or_

matches_bp = Blueprint('matches', __name__)

def parse_date_from_frontend(date_input):
    """解析前端传来的日期格式，并转换为北京时间"""
    if not date_input:
        return None

    date_str = str(date_input).strip()

    # 检查是否包含无效字符或占位符
    invalid_patterns = ['yyyy', 'MM', 'dd', 'We', 'placeholder']
    if any(pattern in date_str for pattern in invalid_patterns):
        raise ValueError('日期格式无效，请重新选择日期')

    # 如果是时间戳（毫秒或秒）
    if date_str.isdigit():
        timestamp = int(date_str)
        # 判断是毫秒还是秒
        if timestamp > 10000000000:  # 毫秒时间戳
            dt = datetime.fromtimestamp(timestamp / 1000)
        else:  # 秒时间戳
            dt = datetime.fromtimestamp(timestamp)
        # 转为北京时间
        sh_tz = pytz.timezone('Asia/Shanghai')
        dt = dt.replace(tzinfo=pytz.UTC).astimezone(sh_tz).replace(tzinfo=None)
        return dt

    # 常见的前端日期格式
    formats = [
        '%Y-%m-%dT%H:%M:%S.%fZ',     # 2024-01-01T10:00:00.000Z
        '%Y-%m-%dT%H:%M:%SZ',        # 2024-01-01T10:00:00Z
        '%Y-%m-%dT%H:%M:%S',         # 2024-01-01T10:00:00
        '%Y-%m-%d %H:%M:%S',         # 2024-01-01 10:00:00
        '%Y-%m-%d %H:%M',            # 2024-01-01 10:00
        '%Y-%m-%d',                  # 2024-01-01
        '%Y/%m/%d %H:%M:%S',         # 2024/01/01 10:00:00
        '%Y/%m/%d %H:%M',            # 2024/01/01 10:00
        '%Y/%m/%d',                  # 2024/01/01
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            # 只要不是Z结尾的，都是本地时间，直接转为北京时间
            sh_tz = pytz.timezone('Asia/Shanghai')
            dt = sh_tz.localize(dt).replace(tzinfo=None)
            return dt
        except ValueError:
            continue

    # 尝试使用 fromisoformat（Python 3.7+）
    try:
        clean_date = date_str.replace('Z', '').replace('+00:00', '')
        dt = datetime.fromisoformat(clean_date)
        sh_tz = pytz.timezone('Asia/Shanghai')
        dt = sh_tz.localize(dt).replace(tzinfo=None)
        return dt
    except ValueError:
        pass

    raise ValueError(f'无法解析日期格式: {date_str}')

def determine_match_type(tournament):
    """根据赛事名称确定matchType"""
    if tournament:
        tournament_name = tournament.name.lower()
        if '冠军杯' in tournament_name or 'champions' in tournament_name:
            return 'champions-cup'
        elif '巾帼杯' in tournament_name or 'womens' in tournament_name:
            return 'womens-cup'
        elif '八人制' in tournament_name or 'eight' in tournament_name:
            return 'eight-a-side'
        else:
            return 'champions-cup'
    else:
        return 'champions-cup'

@matches_bp.route('', methods=['POST'])
@jwt_required()
def create_match():
    """创建比赛"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('matchName', 'team1', 'team2', 'date', 'location')):
        return jsonify({'status': 'error', 'message': '缺少必要信息'}), 400
    
    try:
        # 根据matchType确定赛事ID
        match_type_to_tournament = {
            'champions-cup': 1,
            'womens-cup': 2,
            'eight-a-side': 3
        }
        tournament_id = match_type_to_tournament.get(data.get('matchType', 'champions-cup'), 1)
        
        # 查找球队
        team1 = Team.query.filter_by(name=data['team1'], tournament_id=tournament_id).first()
        team2 = Team.query.filter_by(name=data['team2'], tournament_id=tournament_id).first()
        
        if not team1 or not team2:
            return jsonify({'status': 'error', 'message': '球队不存在'}), 400
        
        # 生成比赛ID
        existing_matches = Match.query.filter_by(tournament_id=tournament_id).count()
        match_id = f"M{tournament_id}{existing_matches + 1:03d}"
        
        # 使用新的日期解析函数
        try:
            match_time = parse_date_from_frontend(data['date'])
            if match_time is None:
                match_time = datetime.now()
        except ValueError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
        
        # 创建比赛
        new_match = Match(
            id=match_id,
            match_name=data['matchName'],
            match_time=match_time,
            location=data['location'],
            home_team_id=team1.id,
            away_team_id=team2.id,
            tournament_id=tournament_id,
            status='P'
        )
        db.session.add(new_match)
        db.session.commit()
        
        # 返回比赛信息时使用标准格式
        match_dict = new_match.to_dict()
        match_dict['matchName'] = match_dict['match_name']
        match_dict['team1'] = data['team1']
        match_dict['team2'] = data['team2']
        # 使用标准格式返回时间
        match_dict['date'] = match_time.strftime('%Y-%m-%d %H:%M:%S') if match_time else None
        
        tournament = Tournament.query.get(tournament_id)
        match_dict['matchType'] = determine_match_type(tournament)
        
        return jsonify({
            'status': 'success',
            'message': '比赛创建成功',
            'data': match_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500

@matches_bp.route('/<string:match_id>/complete', methods=['PUT'])
@jwt_required()
def complete_match(match_id):
    """标记比赛为已完赛"""
    try:
        match = Match.query.get(match_id)
        if not match:
            return jsonify({'status': 'error', 'message': '比赛不存在'}), 404
        
        # 检查比赛是否已经完赛
        if match.status == 'F':
            return jsonify({'status': 'error', 'message': '比赛已经完赛'}), 400
        
        # 更新比赛状态为已完赛
        match.status = 'F'
        db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': '比赛已标记为完赛',
            'data': {
                'id': match.id,
                'status': 'completed'
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'操作失败: {str(e)}'}), 500

@matches_bp.route('', methods=['GET'])
@jwt_required()
def get_matches():
    """获取所有比赛"""
    try:
        matches = Match.query.all()
        matches_data = []
        
        for match in matches:
            match_dict = match.to_dict()
            match_dict['matchName'] = match_dict['match_name']
            # 允许主队或客队为None
            match_dict['team1'] = match.home_team.name if match.home_team else ''
            match_dict['team2'] = match.away_team.name if match.away_team else ''
            # 使用标准格式返回时间
            match_dict['date'] = match.match_time.strftime('%Y-%m-%d %H:%M:%S') if match.match_time else None
            
            # 添加比分信息
            match_dict['home_score'] = match.home_score if match.home_score is not None else 0
            match_dict['away_score'] = match.away_score if match.away_score is not None else 0
            
            tournament = Tournament.query.get(match.tournament_id)
            match_dict['matchType'] = determine_match_type(tournament)
            
            # 修正状态映射 - 根据数据库模型注释
            status_map = {'P': 'pending', 'O': 'ongoing', 'F': 'completed'}
            match_dict['status'] = status_map.get(match.status, 'pending')
            
            matches_data.append(match_dict)
        
        return jsonify({'status': 'success', 'data': matches_data}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

@matches_bp.route('/<string:match_id>', methods=['PUT'])
@jwt_required()
def update_match(match_id):
    """更新比赛信息"""
    data = request.get_json()
    
    try:
        match = Match.query.get(match_id)
        if not match:
            return jsonify({'status': 'error', 'message': '比赛不存在'}), 404
        
        # 更新比赛类型
        if data.get('matchType'):
            match_type_to_tournament = {
                'champions-cup': 1,
                'womens-cup': 2,
                'eight-a-side': 3
            }
            new_tournament_id = match_type_to_tournament.get(data['matchType'], 1)
            match.tournament_id = new_tournament_id
        
        # 更新比赛信息
        if data.get('matchName'):
            match.match_name = data['matchName']
        if data.get('date'):
            try:
                match_time = parse_date_from_frontend(data['date'])
                if match_time:
                    match.match_time = match_time
            except ValueError as e:
                return jsonify({'status': 'error', 'message': str(e)}), 400
        if data.get('location'):
            match.location = data['location']
        
        # 更新比分信息
        if 'home_score' in data:
            try:
                match.home_score = int(data['home_score']) if data['home_score'] is not None else 0
            except (ValueError, TypeError):
                match.home_score = 0
        
        if 'away_score' in data:
            try:
                match.away_score = int(data['away_score']) if data['away_score'] is not None else 0
            except (ValueError, TypeError):
                match.away_score = 0
        
        # 更新球队信息（需要在正确的赛事中查找）
        if data.get('team1'):
            team1 = Team.query.filter_by(name=data['team1'], tournament_id=match.tournament_id).first()
            if team1:
                match.home_team_id = team1.id
        
        if data.get('team2'):
            team2 = Team.query.filter_by(name=data['team2'], tournament_id=match.tournament_id).first()
            if team2:
                match.away_team_id = team2.id
        
        db.session.commit()
        
        # 返回更新后的比赛信息
        match_dict = match.to_dict()
        match_dict['matchName'] = match_dict['match_name']
        match_dict['team1'] = match.home_team.name if match.home_team else ''
        match_dict['team2'] = match.away_team.name if match.away_team else ''
        match_dict['date'] = match.match_time.strftime('%Y-%m-%d %H:%M:%S') if match.match_time else None
        match_dict['home_score'] = match.home_score if match.home_score is not None else 0
        match_dict['away_score'] = match.away_score if match.away_score is not None else 0
        
        tournament = Tournament.query.get(match.tournament_id)
        match_dict['matchType'] = determine_match_type(tournament)
        
        status_map = {'P': 'pending', 'O': 'ongoing', 'F': 'completed'}
        match_dict['status'] = status_map.get(match.status, 'pending')
        
        return jsonify({
            'status': 'success', 
            'message': '更新成功',
            'data': match_dict
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500

@matches_bp.route('/<string:match_id>', methods=['DELETE'])
@jwt_required()
def delete_match(match_id):
    """删除比赛"""
    try:
        match = Match.query.get(match_id)
        if not match:
            return jsonify({'status': 'error', 'message': '比赛不存在'}), 404
        
        # 删除关联的事件
        from app.models.event import Event
        Event.query.filter_by(match_id=match_id).delete()
        
        # 删除比赛
        db.session.delete(match)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': '删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500

@matches_bp.route('/match-records', methods=['GET'])
@jwt_required()
def get_match_records():
    """
    获取比赛记录，支持筛选类型、搜索关键字、状态筛选和分页
    参数:
      - type: 比赛类型 (championsCup, womensCup, eightASide)
      - status: 比赛状态 (pending, ongoing, completed)
      - keyword: 搜索关键字（比赛名称/球队/地点）
      - page: 页码（从1开始）
      - pageSize: 每页数量
    """
    try:
        match_type = request.args.get('type', '').strip()
        status_filter = request.args.get('status', '').strip()
        keyword = request.args.get('keyword', '').strip().lower()
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))

        query = Match.query

        # 类型筛选 - 修正映射关系
        if match_type:
            tournament_map = {
                'championsCup': 1,
                'womensCup': 2, 
                'eightASide': 3
            }
            tournament_id = tournament_map.get(match_type)
            if tournament_id:
                query = query.filter(Match.tournament_id == tournament_id)

        # 状态筛选 - 添加状态过滤
        if status_filter:
            status_map = {
                'pending': 'P',
                'ongoing': 'O', 
                'completed': 'F'
            }
            db_status = status_map.get(status_filter)
            if db_status:
                query = query.filter(Match.status == db_status)

        # 搜索关键字 - 修改为支持NULL值的查询
        if keyword:
            query = query.filter(
                or_(
                    Match.match_name.ilike(f'%{keyword}%'),
                    Match.location.ilike(f'%{keyword}%'),
                    Match.home_team.has(Team.name.ilike(f'%{keyword}%')),
                    Match.away_team.has(Team.name.ilike(f'%{keyword}%'))
                )
            )

        total = query.count()
        matches = query.order_by(Match.match_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

        records = []
        for match in matches:
            match_dict = match.to_dict()
            match_dict['id'] = match.id  # 确保有id字段
            match_dict['name'] = match.match_name
            # 允许主队或客队为None
            match_dict['team1'] = match.home_team.name if match.home_team else ''
            match_dict['team2'] = match.away_team.name if match.away_team else ''
            match_dict['date'] = match.match_time.strftime('%Y-%m-%d %H:%M:%S') if match.match_time else None
            match_dict['location'] = match.location
            # 添加比分信息
            match_dict['home_score'] = match.home_score if match.home_score is not None else 0
            match_dict['away_score'] = match.away_score if match.away_score is not None else 0
            # 添加格式化的比分显示
            match_dict['score'] = f"{match_dict['home_score']} : {match_dict['away_score']}"
            
            # 修正状态映射 - 确保与前端一致
            status_map = {
                'P': {'text': '待进行', 'type': 'info'},
                'O': {'text': '进行中', 'type': 'warning'}, 
                'F': {'text': '已完赛', 'type': 'success'}
            }
            status_info = status_map.get(match.status, {'text': '待进行', 'type': 'info'})
            match_dict['status'] = status_info['text']
            match_dict['status_type'] = status_info['type']
            
            # 修正比赛类型映射 - 确保与前端select选项一致
            type_map = {
                1: 'championsCup',
                2: 'womensCup',
                3: 'eightASide'
            }
            match_dict['type'] = type_map.get(match.tournament_id, 'championsCup')
            
            records.append(match_dict)

        return jsonify({
            'status': 'success',
            'data': {
                'records': records,
                'total': total,
                'page': page,
                'pageSize': page_size
            }
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取比赛记录失败: {str(e)}'}), 500

@matches_bp.route('/<string:match_id>', methods=['GET'])
@jwt_required()
def get_match_detail(match_id):
    """获取单个比赛的详细信息"""
    try:
        # 参数验证
        if not match_id or not match_id.strip():
            return jsonify({'status': 'error', 'message': '比赛ID不能为空'}), 400
        
        match = Match.query.get(match_id.strip())
        if not match:
            return jsonify({'status': 'error', 'message': f'未找到ID为{match_id}的比赛'}), 404
        
        # 获取比赛相关的事件数据
        from app.models.event import Event
        from app.models.player import Player
        from app.models.player_team_history import PlayerTeamHistory
        
        events = Event.query.filter_by(match_id=match_id).all()
        print(f"找到 {len(events)} 个事件记录")
        
        # 统计比赛数据
        total_goals = sum(1 for event in events if event.event_type == 'goal')
        total_yellow_cards = sum(1 for event in events if event.event_type == 'yellow_card')
        total_red_cards = sum(1 for event in events if event.event_type == 'red_card')
        
        # 统计主队和客队数据
        home_goals = 0
        away_goals = 0
        home_yellow_cards = 0
        away_yellow_cards = 0
        home_red_cards = 0
        away_red_cards = 0
        
        if match.home_team_id and match.away_team_id:
            # 通过球员队伍历史记录来获取正确的队伍归属
            home_goals = sum(1 for event in events if event.event_type == 'goal' and _is_player_in_team(event.player_id, match.home_team_id, match.tournament_id))
            away_goals = sum(1 for event in events if event.event_type == 'goal' and _is_player_in_team(event.player_id, match.away_team_id, match.tournament_id))
            
            home_yellow_cards = sum(1 for event in events if event.event_type == 'yellow_card' and _is_player_in_team(event.player_id, match.home_team_id, match.tournament_id))
            away_yellow_cards = sum(1 for event in events if event.event_type == 'yellow_card' and _is_player_in_team(event.player_id, match.away_team_id, match.tournament_id))
            
            home_red_cards = sum(1 for event in events if event.event_type == 'red_card' and _is_player_in_team(event.player_id, match.home_team_id, match.tournament_id))
            away_red_cards = sum(1 for event in events if event.event_type == 'red_card' and _is_player_in_team(event.player_id, match.away_team_id, match.tournament_id))
        
        # 获取参赛球员信息 - 优化查询逻辑
        player_ids = list(set(event.player_id for event in events if event.player_id))
        players_data = []
        
        print(f"找到 {len(player_ids)} 个不重复的球员ID: {player_ids}")
        
        # 如果没有事件数据，尝试从球队阵容中获取球员
        if not player_ids and match.home_team_id and match.away_team_id:
            print("没有事件数据，尝试从球队阵容获取球员...")
            # 获取主队球员
            home_team_histories = PlayerTeamHistory.query.filter_by(
                team_id=match.home_team_id,
                tournament_id=match.tournament_id
            ).all()
            
            # 获取客队球员
            away_team_histories = PlayerTeamHistory.query.filter_by(
                team_id=match.away_team_id,
                tournament_id=match.tournament_id
            ).all()
            
            all_team_histories = home_team_histories + away_team_histories
            print(f"从队伍历史中找到 {len(all_team_histories)} 个球员记录")
            
            for team_history in all_team_histories:
                if team_history.player_id and team_history.player:
                    players_data.append({
                        'player_id': team_history.player_id,
                        'player_name': team_history.player.name or '未知球员',
                        'team_name': team_history.team.name if team_history.team else '未知球队',
                        'player_number': team_history.player_number or 0,
                        'goals': 0,
                        'yellow_cards': 0,
                        'red_cards': 0
                    })
        else:
            # 从事件中获取球员信息
            for player_id in player_ids:
                try:
                    player = Player.query.get(player_id)
                    if player:
                        # 获取球员在此赛事中的队伍归属
                        team_history = PlayerTeamHistory.query.filter_by(
                            player_id=player_id,
                            tournament_id=match.tournament_id
                        ).first()
                        
                        player_events = [e for e in events if e.player_id == player_id]
                        player_goals = sum(1 for e in player_events if e.event_type == 'goal')
                        player_yellow_cards = sum(1 for e in player_events if e.event_type == 'yellow_card')
                        player_red_cards = sum(1 for e in player_events if e.event_type == 'red_card')
                        
                        # 获取球员号码和队伍名称
                        player_number = team_history.player_number if team_history else (player.number or 0)
                        team_name = team_history.team.name if team_history and team_history.team else (player.team.name if player.team else '未知球队')
                        
                        players_data.append({
                            'player_id': player.id,
                            'player_name': player.name or '未知球员',
                            'team_name': team_name,
                            'player_number': player_number,
                            'goals': player_goals,
                            'yellow_cards': player_yellow_cards,
                            'red_cards': player_red_cards
                        })
                except Exception as player_error:
                    print(f"处理球员{player_id}数据时出错: {player_error}")
                    continue
        
        print(f"最终获取到 {len(players_data)} 个球员数据")
        
        # 构建返回数据
        match_data = {
            'id': match.id,
            'home_team_name': match.home_team.name if match.home_team else '主队',
            'away_team_name': match.away_team.name if match.away_team else '客队',
            'home_score': match.home_score if match.home_score is not None else 0,
            'away_score': match.away_score if match.away_score is not None else 0,
            'match_date': match.match_time.isoformat() if match.match_time else '',
            'tournament_name': match.tournament.name if match.tournament else '友谊赛',
            'season_name': f"{match.match_time.year}赛季" if match.match_time else '2024赛季',
            'status': match.status or 'P',
            'total_goals': total_goals,
            'total_yellow_cards': total_yellow_cards,
            'total_red_cards': total_red_cards,
            'total_players': len(players_data),
            'home_goals': home_goals,
            'away_goals': away_goals,
            'home_yellow_cards': home_yellow_cards,
            'away_yellow_cards': away_yellow_cards,
            'home_red_cards': home_red_cards,
            'away_red_cards': away_red_cards,
            'players': players_data
        }
        
        return jsonify({
            'status': 'success',
            'data': match_data
        }), 200
        
    except Exception as e:
        print(f"获取比赛详情异常: {str(e)}")
        return jsonify({'status': 'error', 'message': f'获取比赛详情失败: {str(e)}'}), 500

def _is_player_in_team(player_id, team_id, tournament_id):
    """检查球员是否属于指定队伍（基于赛事历史记录）"""
    if not player_id or not team_id:
        return False
    
    from app.models.player_team_history import PlayerTeamHistory
    
    # 首先检查球员队伍历史记录
    team_history = PlayerTeamHistory.query.filter_by(
        player_id=player_id,
        team_id=team_id,
        tournament_id=tournament_id
    ).first()
    
    if team_history:
        return True
    
    # 如果没有历史记录，回退到球员当前队伍
    from app.models.player import Player
    player = Player.query.get(player_id)
    return player and player.team_id == team_id
