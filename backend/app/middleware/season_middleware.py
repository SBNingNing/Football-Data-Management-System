"""
赛季中间件 - 处理赛季相关的验证和预处理
"""

from functools import wraps
from typing import Dict, Any, Optional
from flask import request, jsonify

from app.utils.logger import get_logger

logger = get_logger(__name__)


def validate_season_creation_data(f):
    """
    验证赛季创建数据的装饰器
    
    验证：
    - 必填字段存在性
    - 数据类型正确性
    - 基础格式验证
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            data = request.get_json()
            
            # 检查请求体
            if not data:
                return jsonify({
                    'status': 'error',
                    'message': '请求体不能为空'
                }), 400
            
            # 验证必填字段
            required_fields = ['name', 'start_time', 'end_time']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        'status': 'error',
                        'message': f'{field}不能为空'
                    }), 400
            
            # 验证赛季名称
            if not isinstance(data['name'], str) or len(data['name'].strip()) == 0:
                return jsonify({
                    'status': 'error',
                    'message': '赛季名称必须是非空字符串'
                }), 400
            
            # 验证时间字段格式
            for time_field in ['start_time', 'end_time']:
                if not isinstance(data[time_field], str):
                    return jsonify({
                        'status': 'error',
                        'message': f'{time_field}必须是字符串格式'
                    }), 400
            
            logger.info(f"赛季创建数据验证通过: {data['name']}")
            
        except Exception as e:
            logger.error(f"赛季创建数据验证失败: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'数据验证失败: {str(e)}'
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_season_update_data(f):
    """
    验证赛季更新数据的装饰器
    
    验证：
    - 至少有一个字段需要更新
    - 数据类型正确性
    - 基础格式验证
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            data = request.get_json()
            
            # 检查请求体
            if not data:
                return jsonify({
                    'status': 'error',
                    'message': '请提供要更新的数据'
                }), 400
            
            # 验证允许更新的字段
            allowed_fields = ['name', 'start_time', 'end_time']
            update_fields = [field for field in allowed_fields if field in data]
            
            if not update_fields:
                return jsonify({
                    'status': 'error',
                    'message': '请提供至少一个有效的更新字段'
                }), 400
            
            # 验证赛季名称（如果提供）
            if 'name' in data:
                if not isinstance(data['name'], str) or len(data['name'].strip()) == 0:
                    return jsonify({
                        'status': 'error',
                        'message': '赛季名称必须是非空字符串'
                    }), 400
            
            # 验证时间字段格式（如果提供）
            for time_field in ['start_time', 'end_time']:
                if time_field in data:
                    if not isinstance(data[time_field], str):
                        return jsonify({
                            'status': 'error',
                            'message': f'{time_field}必须是字符串格式'
                        }), 400
            
            logger.info(f"赛季更新数据验证通过，更新字段: {update_fields}")
            
        except Exception as e:
            logger.error(f"赛季更新数据验证失败: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'数据验证失败: {str(e)}'
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_season_id(f):
    """
    验证赛季ID的装饰器
    
    验证：
    - ID为正整数
    - ID在合理范围内
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 从路径参数获取season_id
            season_id = kwargs.get('season_id')
            
            if season_id is None:
                return jsonify({
                    'status': 'error',
                    'message': '赛季ID不能为空'
                }), 400
            
            # 验证ID类型和范围
            if not isinstance(season_id, int) or season_id <= 0:
                return jsonify({
                    'status': 'error',
                    'message': '赛季ID必须是正整数'
                }), 400
            
            # 验证ID范围（防止异常大的ID）
            if season_id > 999999:
                return jsonify({
                    'status': 'error',
                    'message': '赛季ID超出有效范围'
                }), 400
            
            logger.debug(f"赛季ID验证通过: {season_id}")
            
        except Exception as e:
            logger.error(f"赛季ID验证失败: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'ID验证失败: {str(e)}'
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_date_range_query(f):
    """
    验证日期范围查询参数的装饰器
    
    验证：
    - 日期格式正确性
    - 开始日期早于结束日期
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            # 如果提供了日期参数，验证格式
            if start_date:
                try:
                    from datetime import datetime
                    datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({
                        'status': 'error',
                        'message': '开始日期格式无效'
                    }), 400
            
            if end_date:
                try:
                    from datetime import datetime
                    datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({
                        'status': 'error',
                        'message': '结束日期格式无效'
                    }), 400
            
            # 如果两个日期都提供，验证逻辑关系
            if start_date and end_date:
                from datetime import datetime
                start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                
                if start >= end:
                    return jsonify({
                        'status': 'error',
                        'message': '开始日期必须早于结束日期'
                    }), 400
            
            logger.debug(f"日期范围查询参数验证通过: {start_date} - {end_date}")
            
        except Exception as e:
            logger.error(f"日期范围查询参数验证失败: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'日期参数验证失败: {str(e)}'
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function


def log_season_operation(operation_type: str):
    """
    记录赛季操作的装饰器工厂
    
    Args:
        operation_type (str): 操作类型（如 'create', 'update', 'delete'）
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # 记录操作开始
                season_id = kwargs.get('season_id', 'N/A')
                logger.info(f"开始执行赛季{operation_type}操作 - ID: {season_id}")
                
                # 执行原函数
                result = f(*args, **kwargs)
                
                # 记录操作成功
                logger.info(f"赛季{operation_type}操作成功 - ID: {season_id}")
                
                return result
                
            except Exception as e:
                # 记录操作失败
                season_id = kwargs.get('season_id', 'N/A')
                logger.error(f"赛季{operation_type}操作失败 - ID: {season_id}, 错误: {str(e)}")
                raise
        
        return decorated_function
    return decorator


def preprocess_season_data(f):
    """
    预处理赛季数据的装饰器
    
    处理：
    - 去除字符串首尾空格
    - 标准化数据格式
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            data = request.get_json()
            
            if data:
                # 处理赛季名称
                if 'name' in data and isinstance(data['name'], str):
                    data['name'] = data['name'].strip()
                
                # 处理时间字段格式标准化
                for time_field in ['start_time', 'end_time']:
                    if time_field in data and isinstance(data[time_field], str):
                        data[time_field] = data[time_field].strip()
                
                # 将处理后的数据重新设置到request中
                request._cached_json = data
                
                logger.debug("赛季数据预处理完成")
            
        except Exception as e:
            logger.warning(f"赛季数据预处理失败: {str(e)}")
            # 预处理失败不阻断请求，继续执行
        
        return f(*args, **kwargs)
    
    return decorated_function
