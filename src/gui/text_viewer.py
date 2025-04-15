"""文本查看器窗口"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
from src.core.utils import logger

class TextViewer(tk.Toplevel):
    def __init__(self, parent, file_path):
        super().__init__(parent)
        self.file_path = file_path
        self.setup_window()
        self.create_widgets()
        self.load_file()

    def setup_window(self):
        """设置窗口"""
        # 设置窗口标题
        self.title(f"查看文件: {os.path.basename(self.file_path)}")
        
        # 设置窗口大小
        self.geometry("800x600")
        
        # 使窗口可调整大小
        self.resizable(True, True)
        
        # 设置窗口模态
        self.transient(self.master)
        self.grab_set()

    def create_widgets(self):
        """创建界面组件"""
        # 创建工具栏
        self.create_toolbar()
        
        # 创建文本区域
        self.create_text_area()
        
        # 创建状态栏
        self.create_status_bar()

    def create_toolbar(self):
        """创建工具栏"""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=5, pady=2)

        # 字体大小调整
        ttk.Label(toolbar, text="字体大小:").pack(side="left", padx=5)
        self.font_size = tk.StringVar(value="12")
        font_spin = ttk.Spinbox(toolbar, from_=8, to=72, width=3,
                               textvariable=self.font_size,
                               command=self.change_font_size)
        font_spin.pack(side="left", padx=5)

        # 自动换行选项
        self.wrap_var = tk.BooleanVar(value=True)
        wrap_check = ttk.Checkbutton(toolbar, text="自动换行",
                                   variable=self.wrap_var,
                                   command=self.toggle_wrap)
        wrap_check.pack(side="left", padx=5)

        # 刷新按钮
        refresh_btn = ttk.Button(toolbar, text="刷新",
                               command=self.load_file)
        refresh_btn.pack(side="left", padx=5)

    def create_text_area(self):
        """创建文本区域"""
        # 创建文本框和滚动条的容器
        text_frame = ttk.Frame(self)
        text_frame.pack(fill="both", expand=True, padx=5, pady=2)

        # 创建文本框
        self.text_area = tk.Text(text_frame, wrap="word",
                               font=("Courier New", 12))
        
        # 创建滚动条
        scrollbar_y = ttk.Scrollbar(text_frame, orient="vertical",
                                  command=self.text_area.yview)
        scrollbar_x = ttk.Scrollbar(self, orient="horizontal",
                                  command=self.text_area.xview)
        
        # 配置文本框的滚动
        self.text_area.configure(yscrollcommand=scrollbar_y.set,
                               xscrollcommand=scrollbar_x.set)
        
        # 布局
        scrollbar_y.pack(side="right", fill="y")
        self.text_area.pack(side="left", fill="both", expand=True)
        scrollbar_x.pack(fill="x")

        # 设置文本框只读
        self.text_area.configure(state="disabled")

    def create_status_bar(self):
        """创建状态栏"""
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self, textvariable=self.status_var,
                              relief="sunken")
        status_bar.pack(fill="x", padx=5, pady=2)

    def load_file(self):
        """加载文件内容"""
        try:
            # 获取文件大小
            file_size = os.path.getsize(self.file_path)
            
            # 如果文件大于10MB，显示警告
            if file_size > 10 * 1024 * 1024:  # 10MB
                if not messagebox.askyesno("警告",
                    "文件大小超过10MB，加载可能需要一些时间。是否继续？"):
                    self.destroy()
                    return

            # 设置文本框可编辑
            self.text_area.configure(state="normal")
            
            # 清除当前内容
            self.text_area.delete(1.0, tk.END)
            
            # 读取文件内容
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_area.insert(1.0, content)
            
            # 设置文本框只读
            self.text_area.configure(state="disabled")
            
            # 更新状态
            self.status_var.set(f"文件大小: {self.format_size(file_size)} | "
                              f"字符数: {len(content)}")
            
            logger.info(f"成功加载文件: {self.file_path}")

        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            try:
                with open(self.file_path, 'r', encoding='gbk') as file:
                    content = file.read()
                    self.text_area.insert(1.0, content)
                self.status_var.set("使用GBK编码打开文件")
            except Exception as e:
                self.status_var.set("无法读取文件：可能是二进制文件")
                logger.error(f"文件编码错误: {str(e)}")
                messagebox.showerror("错误",
                    "无法读取文件内容：可能是二进制文件或使用了不支持的编码。")
        
        except Exception as e:
            self.status_var.set("读取文件失败")
            logger.error(f"读取文件失败: {str(e)}")
            messagebox.showerror("错误", f"读取文件失败：{str(e)}")

    def change_font_size(self):
        """改变字体大小"""
        try:
            size = int(self.font_size.get())
            self.text_area.configure(font=("Courier New", size))
        except ValueError:
            self.font_size.set("12")

    def toggle_wrap(self):
        """切换自动换行"""
        wrap_mode = "word" if self.wrap_var.get() else "none"
        self.text_area.configure(wrap=wrap_mode)

    @staticmethod
    def format_size(size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} GB" 