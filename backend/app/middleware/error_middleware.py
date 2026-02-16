from flask import current_app
from app.utils.logger import get_logger

logger = get_logger(__name__)


def log_error(error, context=None):
    """统一错误日志记录"""
    msg = f"Error: {error}"
    if context:
        msg += f" | Context: {context}"
    logger.error(msg, exc_info=True)


def log_security_event(event_type, details, user_id=None):
    """记录安全相关事件"""
    msg = f"Security - {event_type}: {details}"
    if user_id is not None:
        msg += f" | User: {user_id}"
    logger.warning(msg)
