from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.match import Match
from app.models.team import Team
from app.models.tournament import Tournament
from datetime import datetime

matches_bp = Blueprint('matches', __name__)

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
        
        # 解析日期
        match_time = datetime.fromisoformat(data['date'].replace('Z', '+00:00')) if data['date'] else datetime.now()
        
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
        
        # 返回比赛信息
        match_dict = new_match.to_dict()
        match_dict['matchName'] = match_dict['match_name']
        match_dict['team1'] = data['team1']
        match_dict['team2'] = data['team2']
        match_dict['date'] = data['date']
        
        tournament_to_match_type = {1: 'champions-cup', 2: 'womens-cup', 3: 'eight-a-side'}
        match_dict['matchType'] = tournament_to_match_type.get(tournament_id, 'champions-cup')
        
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
            match_dict['date'] = match.match_time.isoformat() if match.match_time else None
            
            tournament_to_match_type = {1: 'champions-cup', 2: 'womens-cup', 3: 'eight-a-side'}
            match_dict['matchType'] = tournament_to_match_type.get(match.tournament_id, 'champions-cup')
            
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
            match.match_time = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
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
