"""
统计中间件 - 处理统计相关的验证和预处理
"""

from functools import wraps
from flask import request, jsonify
from app.utils.logger import get_logger

logger = get_logger(__name__)

def log_stats_operation(operation_type: str):
    """
    记录统计操作的装饰器工厂
    
    Args:
        operation_type (str): 操作类型（如 "query", "calculate", "export"）
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
                "status": "error",
                "message": str(e)
            }), 400
            
        except PermissionError as e:
            logger.warning(f"统计权限错误: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "没有权限访问此统计数据"
            }), 403
            
        except Exception as e:
            logger.error(f"统计系统错误: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "统计服务暂时不可用，请稍后重试"
            }), 500
    
    return decorated_function
