import bcrypt
import re
from typing import Tuple
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SecurityUtils:
    """安全工具类 - 提供密码处理和验证功能"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """对密码进行哈希处理"""
        try:
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        except Exception as e:
            logger.error(f"密码哈希处理失败: {str(e)}")
            raise
    
    @staticmethod
    def check_password(password_hash: str, password: str) -> bool:
        """验证密码"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"密码验证失败: {str(e)}")
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """验证密码强度"""
        if not password:
            return False, "密码不能为空"
        
        if len(password) < 8:
            return False, "密码长度需至少8个字符"
        
        if len(password) > 128:
            return False, "密码长度不能超过128个字符"
        
        if not re.search(r'[0-9]', password):
            return False, "密码需包含至少一个数字"
        
        if not re.search(r'[a-zA-Z]', password):
            return False, "密码需包含至少一个字母"
        
        return True, ""
    
    @staticmethod
    def validate_password_complexity(password: str) -> Tuple[bool, str]:
        """验证密码复杂度（更严格的规则）"""
        basic_valid, basic_msg = SecurityUtils.validate_password_strength(password)
        if not basic_valid:
            return basic_valid, basic_msg
        
        # 检查是否包含特殊字符
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "密码需包含至少一个特殊字符"
        
        # 检查是否包含大小写字母
        if not re.search(r'[a-z]', password):
            return False, "密码需包含至少一个小写字母"
        
        if not re.search(r'[A-Z]', password):
            return False, "密码需包含至少一个大写字母"
        
        return True, ""
    
    @staticmethod
    def generate_salt() -> bytes:
        """生成随机盐值"""
        try:
            return bcrypt.gensalt()
        except Exception as e:
            logger.error(f"盐值生成失败: {str(e)}")
            raise
    
    @staticmethod
    def sanitize_input(input_string: str, max_length: int = 255) -> str:
        """清理输入字符串，防止注入攻击"""
        if not input_string:
            return ""
        
        # 移除危险字符
        sanitized = re.sub(r'[<>"\']', '', input_string)
        
        # 限制长度
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """验证邮箱格式"""
        if not email:
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))


# 保持向后兼容的函数接口
def hash_password(password):
    """对密码进行哈希处理（向后兼容接口）"""
    return SecurityUtils.hash_password(password)

def check_password(password_hash, password):
    """验证密码（向后兼容接口）"""
    return SecurityUtils.check_password(password_hash, password)

def validate_password_strength(password):
    """验证密码强度（向后兼容接口）"""
    return SecurityUtils.validate_password_strength(password)
