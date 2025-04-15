"""
系统配置文件
"""

class FileSystemSettings:
    # 目录扫描配置
    MAX_DEPTH = 50  # 最大递归深度
    MAX_FILES_PER_DIR = 100000  # 单个目录最大文件数
    
    # 内存管理配置
    MEMORY_THRESHOLD = 0.95  # 内存使用阈值（95%）
    MEMORY_CHECK_INTERVAL = 100  # 内存检查间隔
    
    # 批处理配置
    BATCH_SIZE = 500  # 每批处理的文件数
    MAX_QUEUE_SIZE = 1000  # 最大队列大小
    
    # 缓存配置
    CACHE_FILE = "directory_size_cache.json"
    CACHE_EXPIRE_TIME = 3600  # 缓存过期时间（秒）
    
    # 状态显示文本
    SIZE_CALCULATING = "计算中..."
    SIZE_UNKNOWN = "未知"

# 窗口设置
WINDOW_TITLE = "网络工具集合"
WINDOW_SIZE = "900x700"

# 网络设置
PING_COUNT = 4
SOCKET_TIMEOUT = 2

# 文件系统设置
CHUNK_SIZE = 8192  # 文件读取块大小

# UI设置
TREEVIEW_COLUMNS = {
    "size": {"width": 120, "anchor": "e", "text": "大小"},
    "modified": {"width": 150, "anchor": "w", "text": "修改时间"}
} 