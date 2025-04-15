"""文件浏览框架"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from src.gui.widgets import ScrolledTreeview
from src.core.file_system import FileSystemOperations
from src.core.utils import format_size, format_timestamp, logger
from PIL import Image, ImageTk
from src.gui.text_viewer import TextViewer
from src.gui.image_viewer import ImageViewer

class FileFrame(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, text="文件浏览器", padding="5", **kwargs)
        self.current_path = None
        self.scanning = False
        self.thumbnail_size = (32, 32)  # 缩略图大小
        self.image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico'}
        self.thumbnail_cache = {}  # 缩略图缓存
        # 初始化状态变量
        self.status_var = tk.StringVar(value="就绪")
        self.path_var = tk.StringVar()
        self.file_system = FileSystemOperations
        self.file_system.initialize()  # 初始化文件系统操作
        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        # 创建状态栏
        self.create_status_bar()
        
        # 路径显示
        self.create_path_frame()
        
        # 工具栏
        self.create_toolbar()
        
        # 文件树形视图
        self.create_tree_view()
        
        # 创建右键菜单
        self.create_context_menu()

    def create_status_bar(self):
        """创建状态栏"""
        self.status_label = ttk.Label(self, textvariable=self.status_var, 
                                    relief="sunken")
        self.status_label.pack(side="bottom", fill="x", padx=5, pady=2)

    def create_path_frame(self):
        """创建路径显示框架"""
        path_frame = ttk.Frame(self)
        path_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(path_frame, text="当前路径:").pack(side="left")
        self.path_label = ttk.Label(path_frame, textvariable=self.path_var)
        self.path_label.pack(side="left", fill="x", expand=True)

    def create_toolbar(self):
        """创建工具栏"""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=5, pady=2)
        
        self.refresh_button = ttk.Button(toolbar, text="刷新", 
                                       command=self.refresh_current_directory)
        self.refresh_button.pack(side="left", padx=2)
        
        self.up_button = ttk.Button(toolbar, text="上级目录", 
                                  command=self.go_to_parent)
        self.up_button.pack(side="left", padx=2)

    def create_tree_view(self):
        """创建树形视图"""
        # 创建框架来容纳树形视图和滚动条
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 创建树形视图
        self.tree = ttk.Treeview(tree_frame, columns=("icon", "size", "modified"), 
                                show="tree headings")
        
        # 设置列头
        self.tree.heading("size", text="大小", command=lambda: self.sort_tree("size"))
        self.tree.heading("modified", text="修改时间", 
                         command=lambda: self.sort_tree("modified"))
        
        # 设置列宽
        self.tree.column("size", width=120, anchor="e")
        self.tree.column("modified", width=150, anchor="w")
        
        # 创建滚动条
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", 
                           command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", 
                           command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # 布局
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)
        
        # 绑定事件
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="打开", command=self.open_selected)
        self.context_menu.add_command(label="查看", command=self.view_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="删除", command=self.delete_selected)
        self.context_menu.add_command(label="批量删除", command=self.delete_multiple)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="刷新", command=self.refresh_current_directory)

    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def view_selected(self):
        """查看选中的文件内容"""
        selected = self.tree.selection()
        if not selected:
            self.status_var.set("请先选择要查看的文件")
            return

        item = selected[0]
        item_path = self.get_full_path(item)
        
        if not item_path or not os.path.isfile(item_path):
            self.status_var.set("只能查看文件内容")
            return

        # 检查文件扩展名
        file_ext = os.path.splitext(item_path)[1].lower()
        text_extensions = {'.txt', '.log', '.ini', '.conf', '.xml', '.json', 
                         '.yml', '.yaml', '.md', '.py', '.java', '.cpp', '.c', 
                         '.h', '.css', '.html', '.js', '.sql', '.sh', '.bat'}
        
        if file_ext not in text_extensions:
            if not messagebox.askyesno("确认",
                "这可能不是文本文件，是否继续查看？"):
                return

        try:
            # 创建文本查看器窗口
            viewer = TextViewer(self, item_path)
            self.status_var.set(f"正在查看: {os.path.basename(item_path)}")
            
        except Exception as e:
            self.show_error("查看文件错误", e, "查看文件")

    def open_selected(self):
        """打开选中的文件或目录"""
        selected = self.tree.selection()
        if not selected:
            return

        item = selected[0]
        item_path = self.get_full_path(item)
        if not item_path:
            return

        try:
            if os.path.isdir(item_path):
                self.show_directory_contents(item_path)
            else:
                ext = os.path.splitext(item_path)[1].lower()
                if ext in self.image_extensions:
                    # 打开图片查看器
                    ImageViewer(self, item_path)
                else:
                    # 处理其他类型文件
                    super().open_selected()
        except Exception as e:
            self.show_error("打开文件错误", e, "打开文件")

    def delete_selected(self):
        """删除选中的文件或目录"""
        try:
            selected = self.tree.selection()
            if not selected:
                self.status_var.set("请先选择要删除的文件或目录")
                return

            item = selected[0]
            item_text = self.tree.item(item)["text"]
            
            # 不允许删除上级目录项
            if item_text == "📁 ..":
                self.status_var.set("不能删除上级目录")
                return

            # 获取完整路径
            item_path = self.get_full_path(item)
            if not item_path:
                return

            # 确认删除
            is_dir = os.path.isdir(item_path)
            msg = f"确定要删除{'目录' if is_dir else '文件'} {os.path.basename(item_path)} 吗？"
            if not messagebox.askyesno("确认删除", msg):
                return

            if is_dir:
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
            
            self.tree.delete(item)
            self.status_var.set(f"已删除: {os.path.basename(item_path)}")
            logger.info(f"成功删除: {item_path}")

        except Exception as e:
            self.show_error("删除错误", e, "删除文件/目录")

    def delete_multiple(self):
        """删除选中的多个文件或目录"""
        selected_items = self.tree.selection()
        if not selected_items:
            self.status_var.set("未选择任何项目")
            return

        # 获取所有选中项的路径
        items_to_delete = []
        for item in selected_items:
            item_text = self.tree.item(item)['text']
            # 跳过 ".." 返回上级目录的项
            if item_text.endswith(".."):
                continue
            # 移除图标前缀（"📁 " 或 "📄 "）
            name = item_text[2:]
            full_path = os.path.join(self.current_path, name)
            items_to_delete.append(full_path)

        if not items_to_delete:
            self.status_var.set("没有可删除的项目")
            return

        # 确认删除
        count = len(items_to_delete)
        if not messagebox.askyesno("确认删除",
                                 f"确定要删除选中的 {count} 个项目吗？\n此操作不可撤销！"):
            return

        # 执行删除
        success_count = 0
        for path in items_to_delete:
            try:
                if os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                success_count += 1
            except Exception as e:
                logger.error(f"删除失败 {path}: {str(e)}")
                messagebox.showerror("错误", f"删除 {path} 失败：\n{str(e)}")

        # 刷新目录
        self.show_directory_contents(self.current_path)
        self.status_var.set(f"成功删除 {success_count} 个项目")

    def get_full_path(self, item):
        """获取树形视图项目的完整路径"""
        if not self.current_path:
            return None

        item_text = self.tree.item(item)["text"]
        # 移除文件夹/文件图标
        if item_text.startswith("📁 "):
            item_text = item_text[2:]
        elif item_text.startswith("📄 "):
            item_text = item_text[2:]
            
        return os.path.join(self.current_path, item_text)

    def update_file_size(self, path, size):
        """更新文件大小的回调函数"""
        try:
            for item in self.tree.get_children():
                if self.tree.item(item)['values'][0] == path:
                    # 更新大小，清除状态
                    self.tree.set(item, 'size', self.file_system.format_size(size))
                    break
        except Exception as e:
            logger.error(f"更新文件大小失败: {str(e)}")

    def show_directory_contents(self, directory):
        """显示目录内容"""
        try:
            self.current_path = directory
            self.path_var.set(directory)
            self.status_var.set("正在加载目录...")
            self.tree.delete(*self.tree.get_children())

            contents = self.file_system.get_directory_contents(
                directory, 
                size_callback=self.update_file_size
            )

            # 按名称排序，目录在前
            contents.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

            for item in contents:
                # 使用状态信息格式化大小显示
                size_str = self.file_system.format_size(item['size'], item['size_status'])
                modified_str = format_timestamp(item['modified'])
                
                values = (item['path'], size_str, modified_str)
                icon = "📁 " if item['is_dir'] else "📄 "
                
                # 如果是正在计算大小的目录，使用斜体显示
                tags = ('calculating',) if item['size_status'] == self.file_system.SIZE_CALCULATING else ()
                
                self.tree.insert("", "end", text=icon + item['name'], 
                               values=values, tags=tags)

            self.status_var.set("就绪")

        except Exception as e:
            error_msg = f"读取目录失败: {str(e)}"
            logger.error(error_msg)
            self.status_var.set(error_msg)
            messagebox.showerror("错误", error_msg)

    def load_thumbnail(self, file_path):
        """加载文件缩略图"""
        try:
            if file_path in self.thumbnail_cache:
                return self.thumbnail_cache[file_path]

            # 只处理基本图片格式
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in self.image_extensions:
                return None

            image = Image.open(file_path)
            image.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.thumbnail_cache[file_path] = photo
            return photo
        except Exception as e:
            logger.error(f"加载缩略图失败 {file_path}: {str(e)}")
            return None

    def refresh_current_directory(self):
        """刷新当前目录"""
        if self.current_path and os.path.exists(self.current_path):
            self.show_directory_contents(self.current_path)
        else:
            self.status_var.set("当前目录不存在")

    def go_to_parent(self):
        """转到上级目录"""
        if self.current_path:
            parent = os.path.dirname(self.current_path)
            if os.path.exists(parent):
                self.show_directory_contents(parent)

    def sort_tree(self, column):
        """排序树形视图"""
        items = [(self.tree.set(item, column), item) 
                for item in self.tree.get_children("")]
        items.sort(reverse=True)
        for index, (_, item) in enumerate(items):
            self.tree.move(item, "", index)

    def on_double_click(self, event):
        """处理双击事件"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.open_selected()

    def show_error(self, title: str, error: Exception, operation: str = "操作"):
        """显示错误信息"""
        error_message = str(error)
        # 记录错误日志
        logger.error(f"{operation}失败: {error_message}")
        
        # 创建可复制的错误消息对话框
        error_dialog = tk.Toplevel(self)
        error_dialog.title(title)
        error_dialog.geometry("500x200")
        
        # 添加错误信息文本框
        text_widget = tk.Text(error_dialog, wrap=tk.WORD, width=60, height=8)
        text_widget.insert("1.0", f"{operation}失败:\n{error_message}")
        text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # 使文本框只读
        text_widget.configure(state="disabled")
        
        # 添加复制按钮
        def copy_error():
            self.clipboard_clear()
            self.clipboard_append(f"{operation}失败: {error_message}")
            self.status_var.set("错误信息已复制到剪贴板")
        
        copy_button = ttk.Button(error_dialog, text="复制错误信息", 
                                command=copy_error)
        copy_button.pack(pady=5)
        
        # 添加确定按钮
        ok_button = ttk.Button(error_dialog, text="确定", 
                              command=error_dialog.destroy)
        ok_button.pack(pady=5)
        
        # 设置对话框模态
        error_dialog.transient(self)
        error_dialog.grab_set()

    def clear_thumbnail_cache(self):
        """清除缩略图缓存"""
        self.thumbnail_cache.clear()

    def __del__(self):
        """清理资源"""
        self.file_system.cleanup()
        
    def setup_ui(self):
        # ... 其他UI设置代码 ...
        
        # 添加计算中状态的样式
        self.tree.tag_configure('calculating', font=('', 9, 'italic'))
        