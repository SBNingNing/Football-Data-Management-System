"""
事件路由层 - 专注于HTTP请求处理和响应
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from pydantic import ValidationError
from app.services.event_service import EventService
from app.schemas import EventCreate, EventUpdate, EventOut
from app.utils.logger import get_logger

events_bp = Blueprint('events', __name__)
logger = get_logger(__name__)


@events_bp.route('', methods=['POST'])
@jwt_required()
def create_event():
    """创建事件"""
    try:
        payload = EventCreate(**(request.get_json() or {}))
        data = payload.model_dump(by_alias=True)
        logger.info(f"创建事件请求数据: {data}")
        
        # 调用服务层创建事件
        new_event = EventService.create_event(data)
        
        # 格式化返回数据
        event_dict = EventService._format_event_data(new_event)
        event_dict['matchName'] = data.get('matchName') or event_dict.get('matchName')
        
        return jsonify({
            'status': 'success',
            'message': '事件创建成功，统计数据已自动更新',
            'data': event_dict
        }), 201
        
    except ValueError as e:
        # 业务逻辑错误
        logger.error(f"创建事件失败: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

    except ValidationError as e:
        # 参数验证错误
        logger.error(f"创建事件参数验证失败: {e.errors()}")
        return jsonify({'status': 'error', 'message': '参数验证失败', 'details': e.errors()}), 400
        
    except Exception as e:
        # 系统错误
        logger.error(f"创建事件失败: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500


@events_bp.route('', methods=['GET'])
@jwt_required()
def get_events():
    """获取所有事件"""
    try:
        # 记录请求信息
        logger.info(f"获取事件列表请求 - Headers: {dict(request.headers)}")
        
        # 调用服务层获取事件列表
        events_data = EventService.get_all_events()
        
        logger.info(f"成功获取事件列表，共 {len(events_data)} 条记录")
        return jsonify({'status': 'success', 'data': events_data}), 200
        
    except Exception as e:
        logger.error(f"获取事件列表失败: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500


@events_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """更新事件信息"""
    try:
        payload = EventUpdate(**(request.get_json() or {}))
        data = payload.model_dump(exclude_unset=True, by_alias=True)
        logger.info(f"更新事件 {event_id} 请求数据: {data}")
        
        # 调用服务层更新事件
        updated_event = EventService.update_event(event_id, data)
        
        return jsonify({'status': 'success', 'message': '更新成功，统计数据已自动调整'}), 200
        
    except ValueError as e:
        # 业务逻辑错误
        logger.error(f"更新事件 {event_id} 失败: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

    except ValidationError as e:
        # 参数验证错误
        logger.error(f"更新事件 {event_id} 参数验证失败: {e.errors()}")
        return jsonify({'status': 'error', 'message': '参数验证失败', 'details': e.errors()}), 400
        
    except Exception as e:
        # 系统错误
        logger.error(f"更新事件 {event_id} 失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500


@events_bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    """删除事件"""
    try:
        # 调用服务层删除事件
        EventService.delete_event(event_id)
        
        return jsonify({'status': 'success', 'message': '删除成功，统计数据已自动回滚'}), 200
        
    except ValueError as e:
        # 业务逻辑错误
        logger.error(f"删除事件 {event_id} 失败: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 404
        
    except Exception as e:
        # 系统错误
        logger.error(f"删除事件 {event_id} 失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500