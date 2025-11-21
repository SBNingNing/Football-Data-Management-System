"""
比赛模块中间件
提供验证、错误处理和请求预处理功能
"""

from functools import wraps
from flask import request, jsonify
from typing import Callable, Any, Dict
from app.utils.logger import get_logger
from app.utils.match_utils import MatchUtils

logger = get_logger(__name__)


class MatchMiddleware:
    """比赛中间件类"""

    @staticmethod
    def validate_match_id(f: Callable) -> Callable:
        """
        验证比赛ID装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            match_id = kwargs.get('match_id') or request.view_args.get('match_id')
            
            if not match_id or not match_id.strip():
                logger.warning(f"比赛ID验证失败: match_id为空")
                return jsonify({
                    'status': 'error', 
                    'message': '比赛ID不能为空'
                }), 400
            
            kwargs['match_id'] = match_id.strip()
            return f(*args, **kwargs)
        
        return decorated_function

    @staticmethod
    def validate_match_data(f: Callable) -> Callable:
        """
        验证比赛数据装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            
            if not data:
                logger.warning("比赛数据验证失败: 请求体为空")
                return jsonify({
                    'status': 'error', 
                    'message': '请求数据不能为空'
                }), 400
            
            # 使用工具类验证数据
            errors = MatchUtils.validate_match_data(data)
            if errors:
                logger.warning(f"比赛数据验证失败: {errors}")
                return jsonify({
                    'status': 'error', 
                    'message': '数据验证失败: ' + '; '.join(errors)
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function

    @staticmethod
    def validate_date_format(f: Callable) -> Callable:
        """
        验证日期格式装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            
            # Check both 'date' and 'matchTime'
            date_str = data.get('date') or data.get('matchTime')
            
            if data and date_str:
                try:
                    MatchUtils.parse_date_from_frontend(date_str)
                except ValueError as e:
                    logger.warning(f"日期格式验证失败: {str(e)}")
                    return jsonify({
                        'status': 'error', 
                        'message': str(e)
                    }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function

    @staticmethod
    def validate_pagination(f: Callable) -> Callable:
        """
        验证分页参数装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                page = int(request.args.get('page', 1))
                page_size = int(request.args.get('pageSize', 10))
                
                if page < 1:
                    page = 1
                if page_size < 1 or page_size > 100:
                    page_size = 10
                
                kwargs['page'] = page
                kwargs['page_size'] = page_size
                
            except (ValueError, TypeError):
                logger.warning("分页参数验证失败: 参数格式错误")
                return jsonify({
                    'status': 'error', 
                    'message': '分页参数格式错误'
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function

    @staticmethod
    def handle_match_errors(f: Callable) -> Callable:
        """
        比赛操作错误处理装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except ValueError as e:
                logger.error(f"比赛操作参数错误: {str(e)}")
                return jsonify({
                    'status': 'error', 
                    'message': f'参数错误: {str(e)}'
                }), 400
            except Exception as e:
                logger.error(f"比赛操作内部错误: {str(e)}", exc_info=True)
                return jsonify({
                    'status': 'error', 
                    'message': f'操作失败: {str(e)}'
                }), 500
        
        return decorated_function

    @staticmethod
    def log_match_request(f: Callable) -> Callable:
        """
        记录比赛请求日志装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            endpoint = request.endpoint
            method = request.method
            match_id = kwargs.get('match_id', 'N/A')
            
            logger.info(f"比赛请求 - {method} {endpoint}: match_id={match_id}")
            
            result = f(*args, **kwargs)
            
            # 记录响应状态
            if hasattr(result, '__len__') and len(result) > 1:
                status_code = result[1]
                logger.info(f"比赛响应 - {method} {endpoint}: status={status_code}")
            
            return result
        
        return decorated_function

    @staticmethod
    def validate_team_exists(f: Callable) -> Callable:
        """
        验证球队存在性装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            
            if data:
                # 这里可以添加球队存在性验证逻辑
                # 由于需要数据库查询，实际验证会在服务层进行
                # 这里主要做基础数据格式验证
                
                team1 = data.get('team1', '').strip()
                team2 = data.get('team2', '').strip()
                
                if team1 and team2 and team1 == team2:
                    logger.warning("球队验证失败: 主队和客队不能相同")
                    return jsonify({
                        'status': 'error', 
                        'message': '主队和客队不能相同'
                    }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function

    @staticmethod
    def validate_score_format(f: Callable) -> Callable:
        """
        验证比分格式装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            
            if data:
                home_score = data.get('home_score')
                away_score = data.get('away_score')
                
                # 验证比分格式
                if home_score is not None:
                    try:
                        score = int(home_score)
                        if score < 0:
                            raise ValueError("比分不能为负数")
                    except (ValueError, TypeError):
                        logger.warning(f"主队比分格式错误: {home_score}")
                        return jsonify({
                            'status': 'error', 
                            'message': '主队比分格式错误'
                        }), 400
                
                if away_score is not None:
                    try:
                        score = int(away_score)
                        if score < 0:
                            raise ValueError("比分不能为负数")
                    except (ValueError, TypeError):
                        logger.warning(f"客队比分格式错误: {away_score}")
                        return jsonify({
                            'status': 'error', 
                            'message': '客队比分格式错误'
                        }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function

    @staticmethod
    def validate_search_params(f: Callable) -> Callable:
        """
        验证搜索参数装饰器
        
        Args:
            f: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取搜索参数
            match_type = request.args.get('type', '').strip()
            status_filter = request.args.get('status', '').strip()
            keyword = request.args.get('keyword', '').strip()
            
            # 验证比赛类型
            # 移除硬编码验证，支持动态赛事名称
            # if match_type and match_type not in MatchUtils.TOURNAMENT_MAP:
            #     logger.warning(f"无效的比赛类型: {match_type}")
            #     return jsonify({
            #         'status': 'error', 
            #         'message': f'无效的比赛类型: {match_type}'
            #     }), 400
            
            # 验证状态
            if status_filter and status_filter not in MatchUtils.REVERSE_STATUS_MAP:
                logger.warning(f"无效的比赛状态: {status_filter}")
                return jsonify({
                    'status': 'error', 
                    'message': f'无效的比赛状态: {status_filter}'
                }), 400
            
            # 限制关键字长度
            if keyword and len(keyword) > 100:
                logger.warning(f"搜索关键字过长: {len(keyword)}")
                return jsonify({
                    'status': 'error', 
                    'message': '搜索关键字过长'
                }), 400
            
            kwargs['match_type'] = match_type
            kwargs['status_filter'] = status_filter
            kwargs['keyword'] = keyword.lower() if keyword else ''
            
            return f(*args, **kwargs)
        
        return decorated_function


# 组合装饰器 - 常用组合
def validate_create_match(f: Callable) -> Callable:
    """创建比赛验证组合装饰器"""
    return MatchMiddleware.handle_match_errors(
        MatchMiddleware.log_match_request(
            MatchMiddleware.validate_team_exists(
                MatchMiddleware.validate_date_format(
                    MatchMiddleware.validate_match_data(f)
                )
            )
        )
    )


def validate_update_match(f: Callable) -> Callable:
    """更新比赛验证组合装饰器"""
    return MatchMiddleware.handle_match_errors(
        MatchMiddleware.log_match_request(
            MatchMiddleware.validate_score_format(
                MatchMiddleware.validate_date_format(
                    MatchMiddleware.validate_match_id(f)
                )
            )
        )
    )


def validate_get_match(f: Callable) -> Callable:
    """获取比赛验证组合装饰器"""
    return MatchMiddleware.handle_match_errors(
        MatchMiddleware.log_match_request(
            MatchMiddleware.validate_match_id(f)
        )
    )


def validate_delete_match(f: Callable) -> Callable:
    """删除比赛验证组合装饰器"""
    return MatchMiddleware.handle_match_errors(
        MatchMiddleware.log_match_request(
            MatchMiddleware.validate_match_id(f)
        )
    )


def validate_search_matches(f: Callable) -> Callable:
    """搜索比赛验证组合装饰器"""
    return MatchMiddleware.handle_match_errors(
        MatchMiddleware.log_match_request(
            MatchMiddleware.validate_pagination(
                MatchMiddleware.validate_search_params(f)
            )
        )
    )
