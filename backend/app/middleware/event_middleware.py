"""
事件验证中间件
"""
from flask import request, jsonify
from functools import wraps
from app.utils.event_utils import validate_event_type, validate_event_time, get_valid_event_types
from app.utils.logger import get_logger
from typing import Dict, Any, List

logger = get_logger(__name__)


def validate_event_creation_data(f):
    """验证事件创建数据的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        # 验证请求数据是否存在
        if not data:
            logger.error("请求数据为空")
            return jsonify({'status': 'error', 'message': '请求数据为空'}), 400
        
        # 验证必要字段
        # required_fields = ['matchName', 'eventType', 'playerName', 'eventTime']
        # missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if not data.get('eventType'):
             logger.error(f"缺少必要信息: eventType, data: {data}")
             return jsonify({'status': 'error', 'message': '缺少必要信息: eventType'}), 400
             
        if not data.get('eventTime') and data.get('eventTime') != 0:
             logger.error(f"缺少必要信息: eventTime, data: {data}")
             return jsonify({'status': 'error', 'message': '缺少必要信息: eventTime'}), 400
             
        if not data.get('matchName') and not data.get('matchId'):
             logger.error(f"缺少必要信息: matchName 或 matchId, data: {data}")
             return jsonify({'status': 'error', 'message': '缺少必要信息: matchName 或 matchId'}), 400
             
        if not data.get('playerName') and not data.get('playerId'):
             logger.error(f"缺少必要信息: playerName 或 playerId, data: {data}")
             return jsonify({'status': 'error', 'message': '缺少必要信息: playerName 或 playerId'}), 400
        
        # 验证事件类型
        if not validate_event_type(data['eventType']):
            logger.error(f"事件类型无效: {data['eventType']}")
            return jsonify({
                'status': 'error', 
                'message': f'事件类型无效，支持的类型：{get_valid_event_types()}'
            }), 400
        
        # 验证事件时间
        is_valid_time, event_time_int = validate_event_time(data['eventTime'])
        if not is_valid_time:
            logger.error(f"事件时间无效: {data['eventTime']}")
            return jsonify({'status': 'error', 'message': '事件时间无效(0-120分钟)'}), 400
        
        # 将验证后的时间值添加到请求数据中
        data['eventTime'] = event_time_int
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_event_update_data(f):
    """验证事件更新数据的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': '请求数据为空'}), 400
        
        # 验证事件类型（如果提供）
        if data.get('eventType') and not validate_event_type(data['eventType']):
            return jsonify({
                'status': 'error', 
                'message': f'事件类型无效，支持的类型：{get_valid_event_types()}'
            }), 400
        
        # 验证事件时间（如果提供）
        if data.get('eventTime') is not None:
            is_valid_time, event_time_int = validate_event_time(data['eventTime'])
            if not is_valid_time:
                return jsonify({'status': 'error', 'message': '事件时间无效(0-120分钟)'}), 400
            data['eventTime'] = event_time_int
        
        return f(*args, **kwargs)
    
    return decorated_function


class EventValidationMiddleware:
    """事件验证中间件类"""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> tuple[bool, str]:
        """验证必要字段"""
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return False, f'缺少必要信息: {missing_fields}'
        
        return True, ''
    
    @staticmethod
    def validate_event_data(data: Dict[str, Any], is_update: bool = False) -> tuple[bool, str, Dict[str, Any]]:
        """验证事件数据
        
        Args:
            data: 要验证的数据
            is_update: 是否为更新操作
            
        Returns:
            tuple: (是否有效, 错误信息, 处理后的数据)
        """
        if not data:
            return False, '请求数据为空', {}
        
        processed_data = data.copy()
        
        # 如果不是更新操作，验证必要字段
        if not is_update:
            required_fields = ['matchName', 'eventType', 'playerName', 'eventTime']
            is_valid, error_msg = EventValidationMiddleware.validate_required_fields(data, required_fields)
            if not is_valid:
                return False, error_msg, {}
        
        # 验证事件类型
        if data.get('eventType') and not validate_event_type(data['eventType']):
            return False, f'事件类型无效，支持的类型：{get_valid_event_types()}', {}
        
        # 验证事件时间
        if data.get('eventTime') is not None:
            is_valid_time, event_time_int = validate_event_time(data['eventTime'])
            if not is_valid_time:
                return False, '事件时间无效(0-120分钟)', {}
            processed_data['eventTime'] = event_time_int
        
        return True, '', processed_data
