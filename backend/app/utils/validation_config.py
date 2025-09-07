from flask import current_app
import re


class ValidationConfig:
    """验证配置工具类"""
    
    @staticmethod
    def _get_config():
        """获取验证配置"""
        return current_app.config['USER_VALIDATION']
    
    @staticmethod
    def validate_username(username):
        """验证用户名"""
        if not username:
            return False, '用户名不能为空'
        
        config = ValidationConfig._get_config()
        username = username.strip()
        
        if len(username) < config['USERNAME_MIN_LENGTH']:
            return False, f'用户名至少{config["USERNAME_MIN_LENGTH"]}个字符'
        
        if len(username) > config['USERNAME_MAX_LENGTH']:
            return False, f'用户名不能超过{config["USERNAME_MAX_LENGTH"]}个字符'
        
        if not re.match(r'^[\w\u4e00-\u9fff]+$', username):
            return False, '用户名只能包含字母、数字、下划线和中文'
        
        return True, None
    
    @staticmethod
    def validate_password(password):
        """验证密码"""
        if not password:
            return False, '密码不能为空'
        
        config = ValidationConfig._get_config()
        
        if len(password) < config['PASSWORD_MIN_LENGTH']:
            return False, f'密码至少{config["PASSWORD_MIN_LENGTH"]}个字符'
        
        if len(password) > config['PASSWORD_MAX_LENGTH']:
            return False, f'密码不能超过{config["PASSWORD_MAX_LENGTH"]}个字符'
        
        # 密码复杂性验证
        if config['REQUIRE_PASSWORD_COMPLEXITY']:
            patterns = [
                (r'[A-Z]', '至少一个大写字母'),
                (r'[a-z]', '至少一个小写字母'),
                (r'\d', '至少一个数字'),
                (r'[!@#$%^&*(),.?":{}|<>]', '至少一个特殊字符')
            ]
            
            for pattern, desc in patterns:
                if not re.search(pattern, password):
                    return False, f'密码必须包含{desc}'
        
        return True, None
    
    @staticmethod
    def validate_email(email):
        """验证邮箱格式"""
        if not email:
            return False, '邮箱不能为空'
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, '邮箱格式无效'
        
        return True, None
    
    @staticmethod
    def validate_competition_name(name):
        """验证竞赛名称"""
        if not name:
            return False, '赛事名称不能为空'
        
        name = name.strip()
        if len(name) < 2:
            return False, '赛事名称至少2个字符'
        
        if len(name) > 100:
            return False, '赛事名称不能超过100个字符'
        
        return True, None
