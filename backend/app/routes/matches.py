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
            match_dict['team1'] = match.home_team.name
            match_dict['team2'] = match.away_team.name
            # 使用标准格式返回时间
            match_dict['date'] = match.match_time.strftime('%Y-%m-%d %H:%M:%S') if match.match_time else None
            
            tournament = Tournament.query.get(match.tournament_id)
            match_dict['matchType'] = determine_match_type(tournament)
            
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
        
        # 更新球队信息
        if data.get('team1'):
            team1 = Team.query.filter_by(name=data['team1'], tournament_id=match.tournament_id).first()
            if team1:
                match.home_team_id = team1.id
        
        if data.get('team2'):
            team2 = Team.query.filter_by(name=data['team2'], tournament_id=match.tournament_id).first()
            if team2:
                match.away_team_id = team2.id
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': '更新成功'}), 200
        
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
    获取比赛记录，支持筛选类型、搜索关键字和分页
    参数:
      - type: 比赛类型 (championsCup, womensCup, eightASide)
      - keyword: 搜索关键字（比赛名称/球队/地点）
      - page: 页码（从1开始）
      - pageSize: 每页数量
    """
    try:
        match_type = request.args.get('type', '').strip()
        keyword = request.args.get('keyword', '').strip().lower()
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))

        query = Match.query

        # 类型筛选
        if match_type:
            tournament_map = {
                'championsCup': 1,
                'womensCup': 2,
                'eightASide': 3
            }
            tournament_id = tournament_map.get(match_type)
            if tournament_id:
                query = query.filter(Match.tournament_id == tournament_id)

        # 搜索关键字
        if keyword:
            query = query.join(Team, Match.home_team_id == Team.id) \
                .join(Team, Match.away_team_id == Team.id) \
                .filter(
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
            match_dict['team1'] = match.home_team.name
            match_dict['team2'] = match.away_team.name
            match_dict['date'] = match.match_time.strftime('%Y-%m-%d %H:%M:%S') if match.match_time else None
            match_dict['location'] = match.location
            tournament = Tournament.query.get(match.tournament_id)
            match_dict['type'] = (
                '冠军杯' if match.tournament_id == 1 else
                '巾帼杯' if match.tournament_id == 2 else
                '八人制'
            )
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
