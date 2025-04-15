"""图片查看器"""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from src.core.utils import format_size, logger

class ImageViewer(tk.Toplevel):
    def __init__(self, parent, image_path):
        super().__init__(parent)
        self.image_path = image_path
        self.current_image = None
        self.photo_image = None
        self.zoom_level = 100  # 缩放百分比
        self.is_svg = image_path.lower().endswith('.svg')
        self.setup_window()
        self.create_widgets()
        self.load_image()

    def setup_window(self):
        """设置窗口"""
        self.title(f"图片查看: {os.path.basename(self.image_path)}")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # 绑定键盘事件
        self.bind('<Left>', lambda e: self.rotate_image(-90))
        self.bind('<Right>', lambda e: self.rotate_image(90))
        self.bind('<plus>', lambda e: self.zoom_image(10))
        self.bind('<minus>', lambda e: self.zoom_image(-10))

    def create_widgets(self):
        """创建界面组件"""
        # 工具栏
        self.create_toolbar()
        
        # 图片显示区域
        self.create_image_area()
        
        # 状态栏
        self.create_status_bar()

    def create_toolbar(self):
        """创建工具栏"""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=5, pady=2)

        # 旋转按钮
        ttk.Button(toolbar, text="向左旋转", 
                  command=lambda: self.rotate_image(-90)).pack(side="left", padx=2)
        ttk.Button(toolbar, text="向右旋转", 
                  command=lambda: self.rotate_image(90)).pack(side="left", padx=2)

        # 缩放控制
        ttk.Label(toolbar, text="缩放:").pack(side="left", padx=5)
        self.zoom_var = tk.StringVar(value="100%")
        zoom_values = ["25%", "50%", "75%", "100%", "150%", "200%"]
        zoom_combo = ttk.Combobox(toolbar, textvariable=self.zoom_var, 
                                 values=zoom_values, width=5)
        zoom_combo.pack(side="left", padx=2)
        zoom_combo.bind('<<ComboboxSelected>>', self.on_zoom_changed)

        # 适应窗口按钮
        ttk.Button(toolbar, text="适应窗口", 
                  command=self.fit_to_window).pack(side="left", padx=2)

    def create_image_area(self):
        """创建图片显示区域"""
        # 创建带滚动条的画布
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill="both", expand=True, padx=5, pady=2)

        self.canvas = tk.Canvas(self.canvas_frame, bg='gray90')
        
        # 滚动条
        self.scrollbar_y = ttk.Scrollbar(self.canvas_frame, orient="vertical", 
                                       command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", 
                                       command=self.canvas.xview)
        
        # 配置画布滚动
        self.canvas.configure(xscrollcommand=self.scrollbar_x.set, 
                            yscrollcommand=self.scrollbar_y.set)
        
        # 布局
        self.scrollbar_y.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar_x.pack(fill="x")

        # 绑定鼠标滚轮事件
        self.canvas.bind('<MouseWheel>', self.on_mousewheel)
        self.canvas.bind('<Button-4>', self.on_mousewheel)
        self.canvas.bind('<Button-5>', self.on_mousewheel)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self, textvariable=self.status_var, 
                              relief="sunken")
        status_bar.pack(fill="x", padx=5, pady=2)

    def load_image(self):
        """加载图片"""
        try:
            # 处理基本图片格式
            self.current_image = Image.open(self.image_path)
            
            # 获取原始尺寸
            width, height = self.current_image.size
            
            # 更新状态栏
            self.status_var.set(
                f"图片尺寸: {width}x{height} | "
                f"格式: {self.current_image.format} | "
                f"文件大小: {format_size(os.path.getsize(self.image_path))}")
            
            # 显示图片
            self.update_image()
            
        except Exception as e:
            error_msg = f"加载图片失败: {str(e)}"
            logger.error(error_msg)
            self.status_var.set(error_msg)
            raise

    def update_image(self):
        """更新图片显示"""
        if not self.current_image:
            return

        # 获取缩放比例
        zoom = int(self.zoom_var.get().rstrip('%')) / 100

        # 计算新尺寸
        width, height = self.current_image.size
        new_width = int(width * zoom)
        new_height = int(height * zoom)

        # 调整图片大小
        resized = self.current_image.resize((new_width, new_height), 
                                          Image.Resampling.LANCZOS)
        
        # 创建PhotoImage
        self.photo_image = ImageTk.PhotoImage(resized)
        
        # 更新画布
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo_image)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def rotate_image(self, angle):
        """旋转图片"""
        if self.current_image:
            self.current_image = self.current_image.rotate(angle, 
                                                         expand=True)
            self.update_image()

    def zoom_image(self, delta):
        """缩放图片"""
        current = int(self.zoom_var.get().rstrip('%'))
        new_zoom = max(25, min(200, current + delta))
        self.zoom_var.set(f"{new_zoom}%")
        self.update_image()

    def on_zoom_changed(self, event):
        """缩放值改变时更新图片"""
        self.update_image()

    def fit_to_window(self):
        """适应窗口大小"""
        if not self.current_image:
            return

        # 获取窗口大小
        window_width = self.canvas.winfo_width()
        window_height = self.canvas.winfo_height()
        
        # 获取图片大小
        image_width, image_height = self.current_image.size
        
        # 计算缩放比例
        width_ratio = window_width / image_width
        height_ratio = window_height / image_height
        zoom = min(width_ratio, height_ratio) * 100
        
        # 更新缩放值
        self.zoom_var.set(f"{int(zoom)}%")
        self.update_image()

    def on_mousewheel(self, event):
        """鼠标滚轮事件处理"""
        if event.num == 4 or event.delta > 0:
            self.zoom_image(10)
        elif event.num == 5 or event.delta < 0:
            self.zoom_image(-10)

    @staticmethod
    def format_size(size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} GB" 