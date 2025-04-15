"""主窗口"""
import tkinter as tk
from tkinter import ttk, filedialog
from src.config.settings import WINDOW_TITLE, WINDOW_SIZE
from src.gui.network_frame import NetworkFrame
from src.gui.file_frame import FileFrame
from src.gui.widgets import StatusBar

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建主界面
        self.create_widgets()

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开目录", command=self.browse_directory)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit)

        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="刷新", command=self.refresh_current)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)

    def create_widgets(self):
        """创建主界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)
        
        # 创建网络工具区域
        self.network_frame = NetworkFrame(main_frame)
        self.network_frame.pack(fill="x", padx=5, pady=5)
        
        # 创建文件浏览区域
        self.file_frame = FileFrame(main_frame)
        self.file_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 创建状态栏
        self.status_bar = StatusBar(main_frame)
        self.status_bar.pack(fill="x", padx=5, pady=2)

    def browse_directory(self):
        """打开目录"""
        directory = filedialog.askdirectory(title="选择目录")
        if directory:
            self.file_frame.show_directory_contents(directory)
            self.status_bar.set(f"当前目录: {directory}")

    def refresh_current(self):
        """刷新当前目录"""
        self.file_frame.refresh_current_directory()

    def show_about(self):
        """显示关于对话框"""
        from tkinter import messagebox
        messagebox.showinfo(
            "关于",
            "网络工具集合 v1.0\n\n"
            "功能包括：\n"
            "- Ping测试\n"
            "- DNS解析\n"
            "- 端口探测\n"
            "- 文件浏览\n"
            "- 目录大小统计"
        ) 