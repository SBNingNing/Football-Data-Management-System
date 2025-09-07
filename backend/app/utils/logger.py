"""
日志工具模块
"""
import logging
import sys
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取配置好的日志器
    
    Args:
        name: 日志器名称，通常使用 __name__
        
    Returns:
        配置好的日志器实例
    """
    logger = logging.getLogger(name or __name__)
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 设置日志级别
        logger.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # 添加处理器到日志器
        logger.addHandler(console_handler)
        
        # 防止日志传播到根日志器（避免重复输出）
        logger.propagate = False
    
    return logger


def setup_logging():
    """设置全局日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )