from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.competition import Competition
from sqlalchemy.exc import IntegrityError

competitions_bp = Blueprint('competitions', __name__)

@competitions_bp.route('', methods=['GET'])
def get_competitions():
    """获取所有赛事信息"""
    try:
        competitions = Competition.query.all()
        
        return jsonify({
            'status': 'success',
            'data': [competition.to_dict() for competition in competitions]
        }), 200
        
    except Exception as e:
        print(f"[ERROR] 获取赛事列表失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

@competitions_bp.route('/<int:competition_id>', methods=['GET'])
def get_competition(competition_id):
    """根据ID获取单个赛事信息"""
    try:
        competition = Competition.query.get_or_404(competition_id)
        
        return jsonify({
            'status': 'success',
            'data': competition.to_dict()
        }), 200
        
    except Exception as e:
        print(f"[ERROR] 获取赛事信息失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

@competitions_bp.route('', methods=['POST'])
@jwt_required()
def create_competition():
    """创建新赛事"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'status': 'error', 'message': '赛事名称不能为空'}), 400
        
        competition = Competition(
            name=data['name']
        )
        
        db.session.add(competition)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '赛事创建成功',
            'data': competition.to_dict()
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': '赛事名称已存在'}), 400
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] 创建赛事失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500

@competitions_bp.route('/<int:competition_id>', methods=['PUT'])
@jwt_required()
def update_competition(competition_id):
    """更新赛事信息"""
    try:
        competition = Competition.query.get_or_404(competition_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': '请提供要更新的数据'}), 400
        
        if 'name' in data:
            competition.name = data['name']
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '赛事更新成功',
            'data': competition.to_dict()
        }), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': '赛事名称已存在'}), 400
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] 更新赛事失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500

@competitions_bp.route('/<int:competition_id>', methods=['DELETE'])
@jwt_required()
def delete_competition(competition_id):
    """删除赛事"""
    try:
        competition = Competition.query.get_or_404(competition_id)
        
        # 检查是否有关联的tournaments
        if competition.tournaments:
            return jsonify({
                'status': 'error', 
                'message': '该赛事下还有赛季实例，无法删除'
            }), 400
        
        db.session.delete(competition)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '赛事删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] 删除赛事失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500
