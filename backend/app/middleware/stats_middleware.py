"""
统计中间件 - 处理统计相关的验证和预处理
"""

from functools import wraps
from typing import Optional
from flask import request, jsonify

from app.utils.logger import get_logger

logger = get_logger(__name__)


def validate_tournament_id(f):
    """
    验证赛事ID的装饰器
    
    验证：
    - ID为正整数
    - ID在合理范围内
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 从路径参数获取tournament_id
            tournament_id = kwargs.get('tournament_id')
            
            if tournament_id is None:
                return jsonify({
                    'status': 'error',
                    'message': '赛事ID不能为空'
                }), 400
            
            # 验证ID类型和范围
            if not isinstance(tournament_id, int) or tournament_id <= 0:
                return jsonify({
                    'status': 'error',
                    'message': '赛事ID必须是正整数'
                }), 400
            
            # 验证ID范围（防止异常大的ID）
            if tournament_id > 999999:
                return jsonify({
                    'status': 'error',
                    'message': '赛事ID超出有效范围'
                }), 400
            
            logger.debug(f"赛事ID验证通过: {tournament_id}")
            
        except Exception as e:
            logger.error(f"赛事ID验证失败: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'ID验证失败: {str(e)}'
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_stats_query_params(f):
    """
    验证统计查询参数的装饰器
    
    验证：
    - 分页参数的有效性
    - 排序参数的有效性
    - 筛选参数的格式
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 验证分页参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            if page < 1:
                return jsonify({
                    'status': 'error',
                    'message': '页码必须大于0'
                }), 400
            
            if per_page < 1 or per_page > 100:
                return jsonify({
                    'status': 'error',
                    'message': '每页数量必须在1-100之间'
                }), 400
            
            # 验证排序参数
            sort_by = request.args.get('sort_by', 'points')
            valid_sort_fields = ['points', 'goals', 'matches', 'goal_difference']
            
            if sort_by not in valid_sort_fields:
                return jsonify({
                    'status': 'error',
                    'message': f'排序字段必须是: {", ".join(valid_sort_fields)}'
                }), 400
            
            # 验证排序方向
            sort_order = request.args.get('sort_order', 'desc')
            if sort_order not in ['asc', 'desc']:
                return jsonify({
                    'status': 'error',
                    'message': '排序方向必须是 asc 或 desc'
                }), 400
            
            logger.debug(f"统计查询参数验证通过: page={page}, per_page={per_page}, sort_by={sort_by}")
            
        except Exception as e:
            logger.error(f"统计查询参数验证失败: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'参数验证失败: {str(e)}'
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_ranking_type(f):
    """
    验证排行榜类型的装饰器
    
    验证：
    - 排行榜类型的有效性
    - 统计类型参数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 从路径参数获取ranking_type
            ranking_type = kwargs.get('ranking_type')
            
            if ranking_type:
                valid_types = ['scorers', 'cards', 'points', 'assists', 'saves']
                
                if ranking_type not in valid_types:
                    return jsonify({
                        'status': 'error',
                        'message': f'排行榜类型必须是: {", ".join(valid_types)}'
                    }), 400
            
            # 验证统计范围参数
            scope = request.args.get('scope', 'tournament')
            valid_scopes = ['tournament', 'season', 'all']
            
            if scope not in valid_scopes:
                return jsonify({
                    'status': 'error',
                    'message': f'统计范围必须是: {", ".join(valid_scopes)}'
                }), 400
            
            logger.debug(f"排行榜类型验证通过: type={ranking_type}, scope={scope}")
            
        except Exception as e:
            logger.error(f"排行榜类型验证失败: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'类型验证失败: {str(e)}'
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_date_range_stats(f):
    """
    验证统计日期范围的装饰器
    
    验证：
    - 日期格式正确性
    - 日期范围合理性
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
                        'message': '开始日期格式无效，请使用ISO格式'
                    }), 400
            
            if end_date:
                try:
                    from datetime import datetime
                    datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({
                        'status': 'error',
                        'message': '结束日期格式无效，请使用ISO格式'
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
                
                # 验证日期范围不超过1年
                if (end - start).days > 365:
                    return jsonify({
                        'status': 'error',
                        'message': '日期范围不能超过1年'
                    }), 400
            
            logger.debug(f"统计日期范围验证通过: {start_date} - {end_date}")
            
        except Exception as e:
            logger.error(f"统计日期范围验证失败: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'日期参数验证失败: {str(e)}'
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function


def log_stats_operation(operation_type: str):
    """
    记录统计操作的装饰器工厂
    
    Args:
        operation_type (str): 操作类型（如 'query', 'calculate', 'export'）
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # 记录操作开始
                logger.info(f"开始执行统计{operation_type}操作")
                
                # 记录请求参数
                if request.args:
                    logger.debug(f"请求参数: {dict(request.args)}")
                
                # 执行原函数
                result = f(*args, **kwargs)
                
                # 记录操作成功
                logger.info(f"统计{operation_type}操作成功")
                
                return result
                
            except Exception as e:
                # 记录操作失败
                logger.error(f"统计{operation_type}操作失败: {str(e)}")
                raise
        
        return decorated_function
    return decorator


def cache_stats_result(cache_timeout: int = 300):
    """
    缓存统计结果的装饰器工厂
    
    Args:
        cache_timeout (int): 缓存超时时间（秒），默认5分钟
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # 生成缓存键
                cache_key = f"stats_{f.__name__}_{hash(str(kwargs))}"
                
                # 这里可以集成Redis或其他缓存系统
                # 目前只是记录日志，实际缓存逻辑需要根据项目需求实现
                logger.debug(f"统计缓存键: {cache_key}")
                
                # 执行原函数
                result = f(*args, **kwargs)
                
                # 记录缓存操作
                logger.debug(f"统计结果已缓存: {cache_key}")
                
                return result
                
            except Exception as e:
                logger.warning(f"统计缓存操作失败: {str(e)}")
                # 缓存失败不影响主要功能
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_export_format(f):
    """
    验证统计数据导出格式的装饰器
    
    验证：
    - 导出格式的有效性
    - 导出参数的正确性
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            export_format = request.args.get('format', 'json')
            valid_formats = ['json', 'csv', 'xlsx', 'pdf']
            
            if export_format not in valid_formats:
                return jsonify({
                    'status': 'error',
                    'message': f'导出格式必须是: {", ".join(valid_formats)}'
                }), 400
            
            # 验证导出字段
            fields = request.args.get('fields', '')
            if fields:
                field_list = [f.strip() for f in fields.split(',')]
                # 这里可以添加字段有效性验证
                logger.debug(f"导出字段: {field_list}")
            
            logger.debug(f"导出格式验证通过: {export_format}")
            
        except Exception as e:
            logger.error(f"导出格式验证失败: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'导出参数验证失败: {str(e)}'
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function


def handle_stats_errors(f):
    """
    统计错误处理装饰器
    
    统一处理统计相关的异常
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
            
        except ValueError as e:
            logger.warning(f"统计数据验证错误: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
            
        except PermissionError as e:
            logger.warning(f"统计权限错误: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': '没有权限访问此统计数据'
            }), 403
            
        except Exception as e:
            logger.error(f"统计系统错误: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': '统计服务暂时不可用，请稍后重试'
            }), 500
    
    return decorated_function
