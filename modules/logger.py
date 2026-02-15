"""
日志配置模块
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from config import LOG_FILE, LOG_LEVEL, LOG_FORMAT

def setup_logger(name=None):
    """
    配置日志记录器
    支持文件和控制台双输出
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 文件处理器 - 自动轮转
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(LOG_LEVEL)
    file_formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # 控制台只显示警告及以上
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
