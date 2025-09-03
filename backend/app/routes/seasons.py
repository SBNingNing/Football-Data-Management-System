from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.season import Season
from datetime import datetime
from sqlalchemy.exc import IntegrityError

seasons_bp = Blueprint('seasons', __name__)

@seasons_bp.route('', methods=['GET'])
def get_seasons():
    """获取所有赛季信息"""
    try:
        seasons = Season.query.order_by(Season.start_time.desc()).all()
        
        return jsonify({
            'status': 'success',
            'data': [season.to_dict() for season in seasons]
        }), 200
        
    except Exception as e:
        print(f"[ERROR] 获取赛季列表失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

@seasons_bp.route('/<int:season_id>', methods=['GET'])
def get_season(season_id):
    """根据ID获取单个赛季信息"""
    try:
        season = Season.query.get_or_404(season_id)
        
        return jsonify({
            'status': 'success',
            'data': season.to_dict()
        }), 200
        
    except Exception as e:
        print(f"[ERROR] 获取赛季信息失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

@seasons_bp.route('', methods=['POST'])
@jwt_required()
def create_season():
    """创建新赛季"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'start_time', 'end_time']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'status': 'error', 'message': f'{field}不能为空'}), 400
        
        # 解析时间
        try:
            start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'status': 'error', 'message': '时间格式无效'}), 400
        
        if start_time >= end_time:
            return jsonify({'status': 'error', 'message': '开始时间必须早于结束时间'}), 400
        
        season = Season(
            name=data['name'],
            start_time=start_time,
            end_time=end_time
        )
        
        db.session.add(season)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '赛季创建成功',
            'data': season.to_dict()
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': '赛季名称已存在'}), 400
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] 创建赛季失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500

@seasons_bp.route('/<int:season_id>', methods=['PUT'])
@jwt_required()
def update_season(season_id):
    """更新赛季信息"""
    try:
        season = Season.query.get_or_404(season_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': '请提供要更新的数据'}), 400
        
        if 'name' in data:
            season.name = data['name']
        
        if 'start_time' in data:
            try:
                season.start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'status': 'error', 'message': '开始时间格式无效'}), 400
        
        if 'end_time' in data:
            try:
                season.end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'status': 'error', 'message': '结束时间格式无效'}), 400
        
        if season.start_time >= season.end_time:
            return jsonify({'status': 'error', 'message': '开始时间必须早于结束时间'}), 400
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '赛季更新成功',
            'data': season.to_dict()
        }), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': '赛季名称已存在'}), 400
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] 更新赛季失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500

@seasons_bp.route('/<int:season_id>', methods=['DELETE'])
@jwt_required()
def delete_season(season_id):
    """删除赛季"""
    try:
        season = Season.query.get_or_404(season_id)
        
        # 检查是否有关联的tournaments
        if season.tournaments:
            return jsonify({
                'status': 'error', 
                'message': '该赛季下还有赛事实例，无法删除'
            }), 400
        
        db.session.delete(season)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '赛季删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] 删除赛季失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500
