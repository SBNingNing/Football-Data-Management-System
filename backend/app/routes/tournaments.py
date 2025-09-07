"""
赛事路由层
负责处理HTTP请求和响应
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.services.tournament_service import TournamentService
from app.middleware.tournament_middleware import TournamentMiddleware
from app.utils.tournament_utils import TournamentUtils

tournaments_bp = Blueprint('tournaments', __name__)


@tournaments_bp.route('/<tournament_name>', methods=['GET'])
def get_tournament(tournament_name):
    """根据赛事名称获取赛事信息和统计数据"""
    try:
        tournament_info = TournamentService.get_tournament_info_by_name(tournament_name)
        return jsonify(TournamentMiddleware.format_tournament_response(tournament_info)), 200
    except ValueError as ve:
        _, all_names = TournamentService.find_tournament_by_name(tournament_name)
        return jsonify(TournamentMiddleware.format_error_response(
            str(ve), 
            available_tournaments=all_names
        )), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'查询失败: {str(e)}'}), 500


@tournaments_bp.route('', methods=['GET'])
def get_tournaments():
    """获取所有赛事信息（公共接口）"""
    try:
        validated_params = TournamentMiddleware.validate_query_params(request.args)
        tournaments_data = TournamentService.get_all_tournaments(
            group_by_name=validated_params['group_by_name']
        )
        
        return jsonify(TournamentMiddleware.format_tournament_response(tournaments_data)), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'查询失败: {str(e)}'}), 500


@tournaments_bp.route('', methods=['POST'])
@jwt_required()
def create_tournament():
    """创建赛事"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'status': 'error', 'message': '赛事名称不能为空'}), 400
        
        if not data.get('season_name'):
            return jsonify({'status': 'error', 'message': '赛季名称不能为空'}), 400
        
        new_tournament = TournamentService.create_tournament(data)
        tournament_dict = TournamentUtils.build_tournament_dict_from_model(new_tournament)
        
        return jsonify(TournamentMiddleware.format_tournament_response(
            tournament_dict,
            message='赛事创建成功'
        )), 201
        
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500


@tournaments_bp.route('/<int:tournament_id>', methods=['PUT'])
@jwt_required()
def update_tournament(tournament_id):
    """更新赛事信息"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': '请提供要更新的数据'}), 400
        
        TournamentService.update_tournament(tournament_id, data)
        
        return jsonify(TournamentMiddleware.format_tournament_response(
            None,
            message='更新成功'
        )), 200
        
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500


@tournaments_bp.route('/<int:tournament_id>', methods=['DELETE'])
@jwt_required()
def delete_tournament(tournament_id):
    """删除赛事"""
    try:
        TournamentService.delete_tournament(tournament_id)
        
        return jsonify(TournamentMiddleware.format_tournament_response(
            None,
            message='删除成功'
        )), 200
        
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500


@tournaments_bp.route('/instances', methods=['POST'])
@jwt_required()
def create_tournament_instance():
    """创建新的赛事-赛季实例"""
    try:
        data = request.get_json()
        
        required_fields = ['competition_id', 'season_id']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'status': 'error', 'message': f'{field}不能为空'}), 400
        
        tournament = TournamentService.create_tournament_instance(data)
        
        return jsonify(TournamentMiddleware.format_tournament_response(
            tournament.to_dict(),
            message='赛事实例创建成功'
        )), 201
        
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500


@tournaments_bp.route('/instances/<int:tournament_id>', methods=['PUT'])
@jwt_required()
def update_tournament_instance(tournament_id):
    """更新赛事实例"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': '请提供要更新的数据'}), 400
        
        tournament = TournamentService.update_tournament_instance(tournament_id, data)
        
        return jsonify(TournamentMiddleware.format_tournament_response(
            tournament.to_dict(),
            message='赛事实例更新成功'
        )), 200
        
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500
