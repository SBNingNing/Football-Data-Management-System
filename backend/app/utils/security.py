import bcrypt
import re

def hash_password(password):
    """对密码进行哈希处理"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def check_password(password_hash, password):
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def validate_password_strength(password):
    """验证密码强度，返回(是否有效, 错误消息)"""
    if len(password) < 8:
        return False, "密码长度需至少8个字符"
    
    if not re.search(r'[0-9]', password):
        return False, "密码需包含至少一个数字"
    
    if not re.search(r'[a-zA-Z]', password):
        return False, "密码需包含至少一个字母"
    
    return True, ""
