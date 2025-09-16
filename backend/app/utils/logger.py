"""日志工具模块

本模块仅提供一个轻量的 get_logger，返回命名 logger，
不在此处添加 handler 或修改传播设置，避免与 app.utils.logging_config.setup_logging 冲突。
"""
import logging
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取命名日志器；handlers/level 由 setup_logging(app) 统一配置。

    提示：切勿在此函数中添加 handler 或修改 propagate，
    以免造成重复输出或与全局配置不一致。
    """
    return logging.getLogger(name or __name__)


# 兼容旧调用：保留空实现，鼓励使用 app.utils.logging_config.setup_logging(app)
def setup_logging():  # pragma: no cover
    pass