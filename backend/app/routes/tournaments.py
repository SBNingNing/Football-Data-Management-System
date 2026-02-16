"""赛事路由。"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from app.services.tournament_service import TournamentService
from app.models.tournament import Tournament
from app.utils.tournament_utils import TournamentUtils
from app.schemas import TournamentInstanceCreate, TournamentUpdate, TournamentQuickCreate

tournaments_bp = Blueprint('tournaments', __name__)


@tournaments_bp.route('/<tournament_name>', methods=['GET'])
def get_tournament(tournament_name):
    """按数字ID或名称获取赛事。"""
    try:
        # 数字 ID 优先
        if tournament_name.isdigit():
            t_obj = Tournament.query.get(int(tournament_name))
            if t_obj:
                # 复用已有统计构建逻辑：单个名称查询接口期望 records 列表
                teams_data = TournamentService.get_tournament_teams_data(t_obj.id)
                single_record = TournamentService.build_tournament_record_dict(t_obj, teams_data)
                payload = {
                    'tournamentName': t_obj.name,
                    'totalSeasons': 1,
                    'records': [single_record],
                    'matchedMode': 'id'
                }
                return jsonify({'status': 'success', 'data': payload}), 200
        # 名称逻辑
        tournament_info = TournamentService.get_tournament_info_by_name(tournament_name)
        tournament_info['matchedMode'] = 'name'
        return jsonify({'status': 'success', 'data': tournament_info}), 200
    except ValueError as ve:
        _, all_names = TournamentService.find_tournament_by_name(tournament_name)
        return jsonify({
            'status': 'error',
            'message': str(ve),
            'available_tournaments': all_names
        }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'查询失败: {str(e)}'}), 500


@tournaments_bp.route('', methods=['GET'])
def get_tournaments():
    """全部赛事列表。"""
    try:
        group_by_name = request.args.get('group_by_name', 'true').lower() == 'true'
        tournaments_data = TournamentService.get_all_tournaments(
            group_by_name=group_by_name
        )
        
        return jsonify({'status': 'success', 'data': tournaments_data}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'查询失败: {str(e)}'}), 500


@tournaments_bp.route('', methods=['POST'])
@jwt_required()
def create_tournament():
    """创建赛事实例：要求 competition_id + season_id。"""
    try:
        payload = TournamentInstanceCreate(**(request.get_json() or {}))
        data = payload.model_dump(by_alias=True)

        tournament = TournamentService.create_tournament_instance(data)
        return jsonify({
            'status': 'success',
            'data': tournament.to_dict(),
            'message': '赛事实例创建成功'
        }), 201

    except ValidationError as ve:
        return jsonify({'status': 'error', 'message': '参数验证失败', 'details': ve.errors()}), 400
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500


@tournaments_bp.route('/<int:tournament_id>', methods=['PUT'])
@jwt_required()
def update_tournament(tournament_id):
    """更新赛事。"""
    try:
        payload = TournamentUpdate(**(request.get_json() or {}))
        data = payload.model_dump(exclude_unset=True, by_alias=True)
        
        if not data:
            return jsonify({'status': 'error', 'message': '请提供要更新的数据'}), 400
        
        TournamentService.update_tournament(tournament_id, data)
        
        return jsonify({
            'status': 'success',
            'data': None,
            'message': '更新成功'
        }), 200
        
    except ValidationError as ve:
        return jsonify({'status': 'error', 'message': '参数验证失败', 'details': ve.errors()}), 400
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500


@tournaments_bp.route('/<int:tournament_id>', methods=['DELETE'])
@jwt_required()
def delete_tournament(tournament_id):
    """删除赛事。"""
    try:
        TournamentService.delete_tournament(tournament_id)
        
        return jsonify({
            'status': 'success',
            'data': None,
            'message': '删除成功'
        }), 200
        
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500


@tournaments_bp.route('/instances', methods=['POST'])
@jwt_required()
def create_tournament_instance():
    """创建赛事实例。"""
    try:
        data = request.get_json()
        
        required_fields = ['competition_id', 'season_id']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'status': 'error', 'message': f'{field}不能为空'}), 400
        
        tournament = TournamentService.create_tournament_instance(data)
        
        return jsonify({
            'status': 'success',
            'data': tournament.to_dict(),
            'message': '赛事实例创建成功'
        }), 201
        
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500


@tournaments_bp.route('/instances/<int:tournament_id>', methods=['PUT'])
@jwt_required()
def update_tournament_instance(tournament_id):
    """更新赛事实例。"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': '请提供要更新的数据'}), 400
        
        tournament = TournamentService.update_tournament_instance(tournament_id, data)
        
        return jsonify({
            'status': 'success',
            'data': tournament.to_dict(),
            'message': '赛事实例更新成功'
        }), 200
        
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500


@tournaments_bp.route('/quick', methods=['POST'])
@jwt_required()
def create_tournament_quick():
    """快速创建/复用赛事实例。"""
    try:
        payload = TournamentQuickCreate(**(request.get_json() or {}))
        data = payload.model_dump(by_alias=True)
        
        result = TournamentService.create_tournament_quick(data)
        if result.get('dryRun'):
            msg = '试运行成功，将创建新赛事实例' if result['willCreate']['tournament'] else '试运行成功，赛事实例已存在'
            code = 200
        else:
            if result.get('created'):
                msg = '赛事实例创建成功'
                code = 201
            else:
                msg = '赛事实例已存在返回'
                code = 200
        return jsonify({
            'status': 'success',
            'data': result,
            'message': msg
        }), code
    except ValidationError as ve:
        return jsonify({'status': 'error', 'message': '参数验证失败', 'details': ve.errors()}), 400
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500