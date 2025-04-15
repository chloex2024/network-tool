"""文件系统操作"""
import os
import stat
import json
import time
import psutil
import gc
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from src.core.utils import format_size, format_timestamp, logger
from src.config.settings import FileSystemSettings as Settings
from threading import Lock, Thread
from queue import Queue, Empty
import sys

class FileSystemOperations:
    # 将状态常量定义为类属性
    SIZE_CALCULATING = Settings.SIZE_CALCULATING
    SIZE_UNKNOWN = Settings.SIZE_UNKNOWN
    
    # 其他类属性
    _size_cache = {}
    _cache_lock = Lock()
    _size_calc_queue = Queue(maxsize=Settings.MAX_QUEUE_SIZE)
    _background_thread = None
    _is_running = False
    _current_directory = None
    _last_save_time = 0
    _cache_modified = False

    @classmethod
    def _check_memory_usage(cls):
        """检查内存使用情况"""
        try:
            process = psutil.Process()
            sys_memory = psutil.virtual_memory()
            process_memory = process.memory_info()
            memory_percent = process_memory.rss / sys_memory.total
            
            if sys_memory.available > 1024 * 1024 * 1024:  # 1GB
                return True
                
            return memory_percent < Settings.MEMORY_THRESHOLD
            
        except Exception as e:
            logger.error(f"检查内存使用失败: {str(e)}")
            return True

    @classmethod
    def _scan_directory(cls, directory):
        """使用生成器方式扫描目录"""
        batch = []
        file_count = 0
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    try:
                        file_count += 1
                        
                        if file_count % Settings.MEMORY_CHECK_INTERVAL == 0:
                            if not cls._check_memory_usage():
                                logger.warning("内存使用较高，进行垃圾回收")
                                gc.collect()
                                time.sleep(0.1)

                        info = {
                            'name': entry.name,
                            'path': entry.path,
                            'is_dir': entry.is_dir(),
                            'modified': entry.stat().st_mtime,
                            'size': 0,
                            'size_status': ''
                        }

                        if not info['is_dir']:
                            try:
                                info['size'] = entry.stat().st_size
                            except (OSError, PermissionError):
                                info['size'] = 0
                                info['size_status'] = cls.SIZE_UNKNOWN
                        else:
                            cached_size = cls._get_cached_size(entry.path)
                            if cached_size is not None:
                                info['size'] = cached_size
                            else:
                                info['size'] = 0
                                info['size_status'] = cls.SIZE_CALCULATING
                                if cls._size_calc_queue.qsize() < Settings.MAX_QUEUE_SIZE:
                                    cls._size_calc_queue.put((directory, info, None))

                        batch.append(info)
                        
                        if len(batch) >= Settings.BATCH_SIZE:
                            yield batch
                            batch = []
                            gc.collect()
                            
                    except (PermissionError, OSError) as e:
                        logger.warning(f"无法获取文件信息 {entry.path}: {str(e)}")
                        batch.append({
                            'name': entry.name,
                            'path': entry.path,
                            'is_dir': False,
                            'modified': 0,
                            'size': 0,
                            'size_status': cls.SIZE_UNKNOWN
                        })

            if batch:
                yield batch

        except Exception as e:
            logger.error(f"扫描目录失败 {directory}: {str(e)}")
            raise

    @classmethod
    def _load_cache(cls):
        """从文件加载缓存"""
        try:
            cache_path = os.path.join(os.path.dirname(__file__), Settings.CACHE_FILE)
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    with cls._cache_lock:
                        cls._size_cache = cache_data
                    logger.info("已加载目录大小缓存")
        except Exception as e:
            logger.error(f"加载缓存失败: {str(e)}")
            cls._size_cache = {}

    @classmethod
    def _save_cache(cls, force=False):
        """保存缓存到文件"""
        try:
            current_time = time.time()
            # 检查是否需要保存（避免频繁写入）
            if not force and (current_time - cls._last_save_time < 60):  # 至少间隔60秒
                return

            if cls._cache_modified or force:
                cache_path = os.path.join(os.path.dirname(__file__), Settings.CACHE_FILE)
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(cls._size_cache, f, indent=2)
                cls._last_save_time = current_time
                cls._cache_modified = False
                logger.info("已保存目录大小缓存")
        except Exception as e:
            logger.error(f"保存缓存失败: {str(e)}")

    @classmethod
    def _get_dir_modification_time(cls, path):
        """获取目录的最新修改时间"""
        try:
            latest_time = os.path.getmtime(path)
            for root, dirs, files in os.walk(path):
                for name in files + dirs:
                    try:
                        file_path = os.path.join(root, name)
                        mtime = os.path.getmtime(file_path)
                        latest_time = max(latest_time, mtime)
                    except (OSError, PermissionError):
                        continue
            return latest_time
        except (OSError, PermissionError):
            return 0

    @classmethod
    def _is_cache_valid(cls, path):
        """检查缓存是否有效"""
        try:
            with cls._cache_lock:
                if path not in cls._size_cache:
                    return False
                
                cache_data = cls._size_cache[path]
                cache_time = cache_data.get('time', 0)
                cache_mtime = cache_data.get('mtime', 0)
                current_time = time.time()
                
                # 检查缓存是否过期
                if current_time - cache_time > Settings.CACHE_EXPIRE_TIME:
                    return False
                
                # 检查目录是否被修改
                current_mtime = cls._get_dir_modification_time(path)
                if current_mtime > cache_mtime:
                    return False
                
                return True
        except Exception:
            return False

    @classmethod
    def _get_cached_size(cls, path):
        """获取缓存的大小"""
        try:
            if cls._is_cache_valid(path):
                with cls._cache_lock:
                    return cls._size_cache[path]['size']
            return None
        except Exception:
            return None

    @classmethod
    def _set_cached_size(cls, path, size):
        """设置缓存的大小"""
        try:
            with cls._cache_lock:
                cls._size_cache[path] = {
                    'size': size,
                    'time': time.time(),
                    'mtime': cls._get_dir_modification_time(path)
                }
                cls._cache_modified = True
            
            # 定期保存缓存
            if cls._cache_modified:
                cls._save_cache()
        except Exception as e:
            logger.error(f"设置缓存失败 {path}: {str(e)}")

    @classmethod
    def _start_background_thread(cls):
        """启动后台计算线程"""
        if not cls._is_running:
            cls._is_running = True
            cls._background_thread = Thread(target=cls._process_size_calc_queue, daemon=True)
            cls._background_thread.start()

    @classmethod
    def _process_size_calc_queue(cls):
        """处理大小计算队列的后台线程"""
        while cls._is_running:
            try:
                directory, item, callback = cls._size_calc_queue.get(timeout=1)
                if item is None:  # 退出信号
                    break
                
                # 检查是否仍在当前目录
                if directory != cls._current_directory:
                    cls._size_calc_queue.task_done()
                    continue

                # 计算大小
                size = cls.get_file_size(item['path'])
                cls._set_cached_size(item['path'], size)
                
                if callback and directory == cls._current_directory:
                    callback(item['path'], size)
                
                cls._size_calc_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                logger.error(f"后台计算文件大小时出错: {str(e)}")

    @classmethod
    def get_directory_contents(cls, directory, size_callback=None):
        """获取目录内容"""
        if not directory:
            raise ValueError("目录路径不能为空")

        cls._current_directory = directory
        cls._start_background_thread()
        
        # 清空计算队列
        while not cls._size_calc_queue.empty():
            try:
                cls._size_calc_queue.get_nowait()
                cls._size_calc_queue.task_done()
            except Empty:
                break

        contents = []
        try:
            if not os.path.exists(directory):
                raise FileNotFoundError(f"目录不存在: {directory}")

            if not os.path.isdir(directory):
                raise NotADirectoryError(f"不是目录: {directory}")

            # 添加上级目录项
            parent = os.path.dirname(directory)
            if parent != directory:
                contents.append({
                    'name': '..',
                    'path': parent,
                    'is_dir': True,
                    'modified': 0,
                    'size': 0,
                    'size_status': ''
                })

            # 使用生成器方式获取目录内容
            for batch in cls._scan_directory(directory):
                contents.extend(batch)
                gc.collect()

        except Exception as e:
            logger.error(f"读取目录失败 {directory}: {str(e)}")
            raise

        return contents

    @classmethod
    def get_file_size(cls, path, depth=0):
        """获取文件或目录的大小"""
        try:
            if depth == 0 and not cls._check_memory_usage():
                logger.warning(f"内存使用较高，使用缓存或估算大小: {path}")
                cached_size = cls._get_cached_size(path)
                if cached_size is not None:
                    return cached_size
                try:
                    return os.path.getsize(path)
                except:
                    return 0

            if depth > Settings.MAX_DEPTH:
                logger.warning(f"目录递归深度超过 {Settings.MAX_DEPTH} 层: {path}")
                return 0

            # 检查缓存
            cached_size = cls._get_cached_size(path)
            if cached_size is not None:
                return cached_size

            if not os.path.exists(path):
                return 0

            try:
                st = os.lstat(path)
            except (OSError, PermissionError) as e:
                logger.error(f"无法获取文件状态 {path}: {str(e)}")
                return 0

            size = 0
            try:
                if stat.S_ISLNK(st.st_mode):
                    size = st.st_size
                elif stat.S_ISREG(st.st_mode):
                    size = st.st_size
                elif stat.S_ISDIR(st.st_mode):
                    size = st.st_size
                    try:
                        for entry in os.scandir(path):
                            # 定期检查内存使用情况
                            if not cls._check_memory_usage():
                                logger.warning(f"内存使用过高，停止计算目录大小: {path}")
                                return size
                            
                            try:
                                size += cls.get_file_size(entry.path, depth + 1)
                            except (OSError, PermissionError) as e:
                                logger.warning(f"计算文件大小失败 {entry.path}: {str(e)}")
                                continue
                            
                            # 强制垃圾回收
                            gc.collect()
                            
                    except (OSError, PermissionError) as e:
                        logger.warning(f"无法访问目录 {path}: {str(e)}")

                # 更新缓存
                if size > 0:
                    cls._set_cached_size(path, size)
                return size

            except Exception as e:
                logger.error(f"计算大小时发生错误 {path}: {str(e)}")
                return 0

        except Exception as e:
            logger.error(f"计算文件大小时发生未知错误 {path}: {str(e)}")
            return 0

    @classmethod
    def stop_background_thread(cls):
        """停止后台计算线程"""
        cls._is_running = False
        cls._size_calc_queue.put((None, None, None))  # 发送退出信号
        if cls._background_thread:
            cls._background_thread.join()

    @staticmethod
    def format_size(size, status=''):
        """格式化文件大小显示，添加状态显示"""
        try:
            if status:  # 如果有状态信息，直接返回
                return status
                
            if size < 0:
                return "0B"
                
            units = ['B', 'K', 'M', 'G', 'T', 'P']
            size = float(size)
            unit_index = 0
            
            while size >= 1024.0 and unit_index < len(units) - 1:
                size /= 1024.0
                unit_index += 1
                
            return f"{size:.1f}{units[unit_index]}"
            
        except Exception as e:
            logger.error(f"格式化文件大小失败: {str(e)}")
            return "0B"

    @staticmethod
    def get_size(entry) -> int:
        """获取文件或目录大小"""
        try:
            if entry.is_file():
                return entry.stat().st_size
            elif entry.is_dir():
                return FileSystemOperations.calculate_dir_size(entry.path)
            return 0
        except Exception:
            return 0

    @staticmethod
    def calculate_dir_size(path: str, depth: int = 0) -> int:
        """递归计算目录大小"""
        if depth >= Settings.MAX_DEPTH:
            return 0
            
        total = 0
        try:
            with os.scandir(path) as it:
                for entry in it:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            total += entry.stat().st_size
                        elif entry.is_dir(follow_symlinks=False):
                            total += FileSystemOperations.calculate_dir_size(
                                entry.path, depth + 1)
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            pass
        return total

    @staticmethod
    def delete_item(path: str) -> Tuple[bool, str]:
        """删除文件或目录"""
        try:
            if os.path.isdir(path):
                os.rmdir(path)
            else:
                os.remove(path)
            return True, "删除成功"
        except Exception as e:
            return False, str(e)

    @classmethod
    def initialize(cls):
        """初始化类，加载缓存"""
        cls._load_cache()

    @classmethod
    def cleanup(cls):
        """清理类，保存缓存"""
        cls._save_cache(force=True)
        cls.stop_background_thread() 