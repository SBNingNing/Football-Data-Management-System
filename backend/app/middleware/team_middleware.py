"""球队中间件: 校验/日志/错误包装。"""
from functools import wraps
from flask import request, jsonify
from typing import Dict, Any
from app.utils.logger import get_logger
from app.utils.team_utils import TeamUtils

logger = get_logger(__name__)


def validate_team_data(f):
    """创建/更新球队数据校验。"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        if not data:
            logger.warning("请提供球队数据")
            return jsonify({'status': 'error', 'message': '请提供球队数据'}), 400
        
        # 验证球队名称
        if not data.get('teamName'):
            logger.warning("球队名称不能为空")
            return jsonify({'status': 'error', 'message': '球队名称不能为空'}), 400
        
        # 验证球队名称长度
        team_name = data['teamName'].strip()
        if len(team_name) < 2:
            return jsonify({'status': 'error', 'message': '球队名称至少需要2个字符'}), 400
        
        if len(team_name) > 50:
            return jsonify({'status': 'error', 'message': '球队名称不能超过50个字符'}), 400
        
        # 验证并归一化比赛类型（支持中文/别名，例如 巾帼杯、女子杯、八人制 等）
        raw_match_type = data.get('matchType', 'champions-cup')
        canonical_type, mt_error = TeamUtils.normalize_match_type(raw_match_type)
        if mt_error:
            return jsonify({'status': 'error', 'message': mt_error}), 400
        data['matchType'] = canonical_type  # 归一化覆盖
        
        # 验证球员数据
        players = data.get('players', [])
        if isinstance(players, list):
            for i, player in enumerate(players):
                if not isinstance(player, dict):
                    return jsonify({
                        'status': 'error', 
                        'message': f'第{i+1}个球员数据格式错误'
                    }), 400
                
                if not player.get('name'):
                    return jsonify({
                        'status': 'error', 
                        'message': f'第{i+1}个球员姓名不能为空'
                    }), 400
                
                if not player.get('studentId'):
                    return jsonify({
                        'status': 'error', 
                        'message': f'第{i+1}个球员学号不能为空'
                    }), 400
                
                # 验证球员号码
                try:
                    number = int(player.get('number', 1))
                    if number < 0:
                        return jsonify({
                            'status': 'error', 
                            'message': f'第{i+1}个球员号码必须大于等于0'
                        }), 400
                except (ValueError, TypeError):
                    return jsonify({
                        'status': 'error', 
                        'message': f'第{i+1}个球员号码格式错误'
                    }), 400
        
        return f(*args, **kwargs)
    return decorated_function


def validate_team_id(f):
    """校验 team_id 正整数。"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        team_id = kwargs.get('team_id')
        
        if not team_id or not isinstance(team_id, int) or team_id <= 0:
            logger.warning(f"无效的球队ID: {team_id}")
            return jsonify({'status': 'error', 'message': '无效的球队ID'}), 400
        
        return f(*args, **kwargs)
    return decorated_function


def validate_team_name(f):
    """校验路径球队名称。"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        team_name = kwargs.get('team_name')
        
        if not team_name or not isinstance(team_name, str):
            logger.warning(f"无效的球队名称: {team_name}")
            return jsonify({'status': 'error', 'message': '无效的球队名称'}), 400
        
        # 验证球队名称长度和字符
        team_name = team_name.strip()
        if len(team_name) < 1:
            return jsonify({'status': 'error', 'message': '球队名称不能为空'}), 400
        
        if len(team_name) > 50:
            return jsonify({'status': 'error', 'message': '球队名称不能超过50个字符'}), 400
        
        return f(*args, **kwargs)
    return decorated_function


def validate_query_params(f):
    """校验查询参数。"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 验证group_by_name参数
        group_by_name = request.args.get('group_by_name', 'false')
        if group_by_name.lower() not in ['true', 'false']:
            return jsonify({
                'status': 'error', 
                'message': 'group_by_name参数只能是true或false'
            }), 400
        
        return f(*args, **kwargs)
    return decorated_function


def handle_team_errors(f):
    """统一错误捕获。"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as ve:
            logger.warning(f"球队操作验证错误: {ve}")
            return jsonify({'status': 'error', 'message': str(ve)}), 400
        except Exception as e:
            logger.error(f"球队操作意外错误: {e}")
            return jsonify({'status': 'error', 'message': '服务器内部错误'}), 500
    return decorated_function


def log_team_operation(operation_type: str):
    """操作日志。"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 记录操作开始
            logger.info(f"球队{operation_type}操作开始")
            
            try:
                result = f(*args, **kwargs)
                logger.info(f"球队{operation_type}操作成功完成")
                return result
            except Exception as e:
                logger.error(f"球队{operation_type}操作失败: {e}")
                raise
                
        return decorated_function
    return decorator


class TeamMiddleware:
    """响应格式化与简易校验工具。"""
    
    @staticmethod
    def format_team_response(data: Any, message: str = None) -> Dict[str, Any]:
        """成功响应包装。"""
        response = {
            'status': 'success'
        }
        
        if message:
            response['message'] = message
        
        if data is not None:
            response['data'] = data
        
        return response
    
    @staticmethod
    def format_error_response(error_message: str, error_code: str = None) -> Dict[str, Any]:
        """错误响应包装。"""
        response = {
            'status': 'error',
            'message': error_message
        }
        
        if error_code:
            response['error_code'] = error_code
        
        return response
    
    @staticmethod
    def validate_query_params(args: Dict[str, str]) -> Dict[str, Any]:
        """解析查询参数。"""
        validated_params = {
            'group_by_name': args.get('group_by_name', 'false').lower() == 'true'
        }
        
        return validated_params
    
    
def validate_team_update_data(f):
    """局部更新校验: teamName 可选; 若提供 players 进行结构校验; matchType 若提供则归一化。"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json() or {}
        # 允许空 JSON -> 会在 service 层判断是否有实际更新字段
        if 'teamName' in data:
            name = str(data['teamName']).strip()
            if len(name) < 2:
                return jsonify({'status': 'error', 'message': '球队名称至少需要2个字符'}), 400
            if len(name) > 50:
                return jsonify({'status': 'error', 'message': '球队名称不能超过50个字符'}), 400
        if 'matchType' in data:
            canonical, mt_err = TeamUtils.normalize_match_type(data.get('matchType'))
            if mt_err:
                return jsonify({'status': 'error', 'message': mt_err}), 400
            data['matchType'] = canonical
        if 'players' in data:
            players = data['players']
            if not isinstance(players, list):
                return jsonify({'status': 'error', 'message': 'players 必须是列表'}), 400
            for i, p in enumerate(players):
                if not isinstance(p, dict):
                    return jsonify({'status': 'error', 'message': f'第{i+1}个球员数据格式错误'}), 400
                if not p.get('name'):
                    return jsonify({'status': 'error', 'message': f'第{i+1}个球员姓名不能为空'}), 400
                if not p.get('studentId') and not p.get('playerId'):
                    return jsonify({'status': 'error', 'message': f'第{i+1}个球员学号不能为空'}), 400
                number = p.get('number')
                if number is not None:
                    try:
                        num_int = int(number)
                        if num_int < 0:
                            return jsonify({'status': 'error', 'message': f'第{i+1}个球员号码必须大于等于0'}), 400
                    except (ValueError, TypeError):
                        return jsonify({'status': 'error', 'message': f'第{i+1}个球员号码格式错误'}), 400
        return f(*args, **kwargs)
    return decorated_function