"""通用工具函数"""
from datetime import datetime
import logging
import os

def setup_logger():
    """设置日志"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# 创建logger实例
logger = setup_logger()

def format_size(size: int) -> str:
    """格式化文件大小"""
    try:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:6.1f} {unit}"
            size /= 1024.0
        return f"{size:6.1f} PB"
    except Exception as e:
        logger.error(f"格式化文件大小错误: {str(e)}")
        return "0 B"

def format_timestamp(timestamp: float) -> str:
    """格式化时间戳"""
    try:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logger.error(f"格式化时间戳错误: {str(e)}")
        return "未知时间" 