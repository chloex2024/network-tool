import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import socket
import platform
import subprocess
import threading
from datetime import datetime
import os
from pathlib import Path
import shutil

class NetworkTools:
    def __init__(self, root):
        self.root = root
        self.root.title("网络工具集合")
        self.root.geometry("900x700")
        
        # 初始化状态变量
        self.status_var = tk.StringVar(value="就绪")
        self.path_var = tk.StringVar()
        self.current_path = None
        self.scanning = False
        self.total_dirs = 0
        self.total_files = 0
        self.total_size = 0

        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建网络工具区域
        self.create_network_tools()
        
        # 创建文件浏览区域
        self.create_file_browser()
        
        # 创建状态栏
        self.create_status_bar()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开目录", command=self.browse_directory)
        file_menu.add_command(label="清除", command=self.clear_output)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)

        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="Ping", command=self.show_ping_frame)
        tools_menu.add_command(label="DNS解析", command=self.show_dns_frame)
        tools_menu.add_command(label="端口探测", command=self.show_port_scan_frame)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)

    def create_network_tools(self):
        """创建网络工具区域"""
        # 网络工具框架
        network_frame = ttk.LabelFrame(self.main_frame, text="网络工具", padding="5")
        network_frame.pack(fill="x", padx=5, pady=5)

        # 输入区域
        input_frame = ttk.Frame(network_frame)
        input_frame.pack(fill="x", padx=5, pady=5)

        # IP地址输入
        ttk.Label(input_frame, text="IP地址/域名:").pack(side="left", padx=5)
        self.ip_entry = ttk.Entry(input_frame, width=30)
        self.ip_entry.pack(side="left", padx=5)

        # 端口输入
        ttk.Label(input_frame, text="端口:").pack(side="left", padx=5)
        self.port_entry = ttk.Entry(input_frame, width=10)
        self.port_entry.pack(side="left", padx=5)

        # 协议选择
        self.protocol_var = tk.StringVar(value="TCP")
        ttk.Radiobutton(input_frame, text="TCP", variable=self.protocol_var, 
                       value="TCP").pack(side="left", padx=2)
        ttk.Radiobutton(input_frame, text="UDP", variable=self.protocol_var, 
                       value="UDP").pack(side="left", padx=2)

        # 按钮区域
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(side="left", padx=5)

        self.ping_button = ttk.Button(button_frame, text="Ping", 
                                    command=self.start_ping)
        self.ping_button.pack(side="left", padx=2)

        self.dns_button = ttk.Button(button_frame, text="DNS解析", 
                                   command=self.start_dns)
        self.dns_button.pack(side="left", padx=2)

        self.port_scan_button = ttk.Button(button_frame, text="端口探测", 
                                         command=self.start_port_scan)
        self.port_scan_button.pack(side="left", padx=2)

        # 网络工具输出区域
        self.network_output = scrolledtext.ScrolledText(network_frame, 
                                                      height=10, width=70)
        self.network_output.pack(fill="x", padx=5, pady=5)

    def create_file_browser(self):
        """创建文件浏览区域"""
        # 文件浏览框架
        browser_frame = ttk.LabelFrame(self.main_frame, text="文件浏览器", padding="5")
        browser_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 路径显示
        path_frame = ttk.Frame(browser_frame)
        path_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(path_frame, text="当前路径:").pack(side="left")
        self.path_label = ttk.Label(path_frame, textvariable=self.path_var)
        self.path_label.pack(side="left", fill="x", expand=True)

        # 创建一个框架来容纳树形视图和滚动条
        tree_frame = ttk.Frame(browser_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 文件树形视图
        self.tree = ttk.Treeview(tree_frame, columns=("size", "modified"), 
                                show="tree headings")
        self.tree.heading("size", text="大小")
        self.tree.heading("modified", text="修改时间")
        
        # 设置列宽
        self.tree.column("size", width=120, anchor="e")
        self.tree.column("modified", width=150, anchor="w")
        
        # 滚动条
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", 
                            command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", 
                            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # 使用pack布局管理器
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        # 绑定事件
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # 创建右键菜单
        self.create_context_menu()

    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="打开", command=self.open_selected)
        self.context_menu.add_command(label="删除", command=self.delete_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="刷新", command=self.refresh_current_directory)

    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def delete_selected(self):
        """删除选中的文件或目录"""
        selected = self.tree.selection()
        if not selected:
            return

        item = selected[0]
        item_path = self.get_full_path(item)
        
        if not os.path.exists(item_path):
            messagebox.showerror("错误", "文件或目录不存在")
            return

        # 确认删除
        is_dir = os.path.isdir(item_path)
        msg = f"确定要删除{'目录' if is_dir else '文件'} {os.path.basename(item_path)} 吗？"
        if not messagebox.askyesno("确认删除", msg):
            return

        try:
            if is_dir:
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
            self.tree.delete(item)
            self.status_var.set(f"已删除: {os.path.basename(item_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {str(e)}")

    def open_selected(self):
        """打开选中的文件或目录"""
        selected = self.tree.selection()
        if not selected:
            return

        item = selected[0]
        item_path = self.get_full_path(item)
        
        if not os.path.exists(item_path):
            messagebox.showerror("错误", "文件或目录不存在")
            return

        try:
            if os.path.isdir(item_path):
                # 如果是目录，显示目录内容
                self.show_directory_contents(item_path)
            else:
                # 如果是文件，使用系统默认程序打开
                if platform.system() == 'Windows':
                    os.startfile(item_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', item_path])
                else:  # Linux
                    subprocess.run(['xdg-open', item_path])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开: {str(e)}")

    def get_full_path(self, item):
        """获取树形项目的完整路径"""
        path_parts = []
        while item:
            path_parts.append(self.tree.item(item)["text"])
            item = self.tree.parent(item)
        return os.path.join(self.current_path, *reversed(path_parts))

    def on_double_click(self, event):
        """处理双击事件"""
        item = self.tree.identify_row(event.y)
        if not item:
            return

        # 获取完整路径
        if self.tree.item(item)['text'] == "📁 ..":
            # 处理返回上级目录
            parent = self.get_parent_directory()
            if parent:
                self.show_directory_contents(parent)
        else:
            item_path = self.get_full_path(item)
            if os.path.isdir(item_path):
                self.show_directory_contents(item_path)
            else:
                self.open_selected()

    def refresh_current_directory(self):
        """刷新当前目录"""
        if self.current_path:
            self.show_directory_contents(self.current_path)

    def show_directory_contents(self, directory):
        """显示目录内容"""
        self.current_path = directory
        self.path_var.set(directory)
        
        # 在主线程中更新界面
        self.root.after(0, lambda: self.status_var.set("正在扫描..."))
        
        try:
            # 清空树形视图
            self.root.after(0, lambda: self.tree.delete(*self.tree.get_children()))

            # 添加返回上级目录的项目
            parent = self.get_parent_directory()
            if parent:
                self.root.after(0, lambda: self.tree.insert("", "0", 
                    text="📁 ..", values=("", ""), tags=('parent_dir',)))

            # 获取目录内容
            items = []
            with os.scandir(directory) as it:
                for entry in it:
                    try:
                        stats = entry.stat()
                        if entry.is_dir():
                            size = self.calculate_dir_size(entry.path)
                        else:
                            size = stats.st_size
                        
                        items.append({
                            'name': entry.name,
                            'path': entry.path,
                            'size': size,
                            'is_dir': entry.is_dir(),
                            'modified': datetime.fromtimestamp(stats.st_mtime)
                        })
                    except Exception as e:
                        print(f"Error processing {entry.path}: {e}")

            # 按名称排序，目录在前
            items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

            # 在主线程中更新树形视图
            def update_tree():
                for item in items:
                    size_str = self.format_size(item['size'])
                    modified_str = item['modified'].strftime('%Y-%m-%d %H:%M:%S')
                    
                    values = (size_str, modified_str)
                    icon = "📁 " if item['is_dir'] else "📄 "
                    self.tree.insert("", "end", text=icon + item['name'], 
                                   values=values)

                # 更新状态
                total_size = sum(item['size'] for item in items)
                total_files = sum(1 for item in items if not item['is_dir'])
                total_dirs = sum(1 for item in items if item['is_dir'])
                
                status = f"总计: {total_files} 个文件, {total_dirs} 个目录, 总大小: {self.format_size(total_size)}"
                self.status_var.set(status)

            self.root.after(0, update_tree)

        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"错误: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("错误", 
                f"无法读取目录: {str(e)}"))

    def sort_tree(self, column):
        """排序树形视图"""
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children("")]
        items.sort(reverse=True)
        for index, (_, item) in enumerate(items):
            self.tree.move(item, "", index)

    def calculate_dir_size(self, path):
        """递归计算目录大小"""
        total = 0
        try:
            with os.scandir(path) as it:
                for entry in it:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            total += entry.stat().st_size
                        elif entry.is_dir(follow_symlinks=False):
                            total += self.calculate_dir_size(entry.path)
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            pass
        return total

    def format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:6.1f} {unit}"
            size /= 1024.0
        return f"{size:6.1f} PB"

    def get_parent_directory(self):
        """获取当前目录的父目录"""
        if self.current_path:
            parent = os.path.dirname(self.current_path)
            if os.path.exists(parent):
                return parent
        return None

    def browse_directory(self):
        """选择并显示目录内容"""
        directory = filedialog.askdirectory(title="选择目录")
        if directory:
            if self.scanning:
                return
            
            self.scanning = True
            self.disable_controls()
            self.status_var.set("正在扫描...")
            
            # 清空树形视图
            if hasattr(self, 'tree'):
                self.tree.delete(*self.tree.get_children())
            
            threading.Thread(
                target=self.scan_directory_thread,
                args=(directory,),
                daemon=True
            ).start()

    def scan_directory_thread(self, directory):
        """在新线程中执行目录扫描"""
        try:
            self.show_directory_contents(directory)
        except Exception as e:
            self.status_var.set(f"扫描出错: {str(e)}")
        finally:
            self.scanning = False
            self.root.after(0, self.enable_controls)

    def disable_controls(self):
        """禁用控件"""
        # 禁用网络工具按钮
        if hasattr(self, 'ping_button'):
            self.ping_button.configure(state='disabled')
        if hasattr(self, 'dns_button'):
            self.dns_button.configure(state='disabled')
        if hasattr(self, 'port_scan_button'):
            self.port_scan_button.configure(state='disabled')
        
        # 禁用输入框
        if hasattr(self, 'ip_entry'):
            self.ip_entry.configure(state='disabled')
        if hasattr(self, 'port_entry'):
            self.port_entry.configure(state='disabled')

    def enable_controls(self):
        """启用控件"""
        # 启用网络工具按钮
        if hasattr(self, 'ping_button'):
            self.ping_button.configure(state='normal')
        if hasattr(self, 'dns_button'):
            self.dns_button.configure(state='normal')
        if hasattr(self, 'port_scan_button'):
            self.port_scan_button.configure(state='normal')
        
        # 启用输入框
        if hasattr(self, 'ip_entry'):
            self.ip_entry.configure(state='normal')
        if hasattr(self, 'port_entry'):
            self.port_entry.configure(state='normal')

    def clear_output(self):
        """清除输出区域"""
        self.tree.delete(*self.tree.get_children())

    def show_port_scan_frame(self):
        self.clear_output()
        self.network_output.delete(1.0, tk.END)
        self.network_output.insert(tk.END, "请输入要探测的IP地址和端口，选择协议类型后点击端口探测按钮\n")

    def start_port_scan(self):
        host = self.ip_entry.get().strip()
        port_str = self.port_entry.get().strip()
        protocol = self.protocol_var.get()

        if not host or not port_str:
            messagebox.showerror("错误", "请输入IP地址和端口")
            return

        try:
            port = int(port_str)
            if not (0 <= port <= 65535):
                raise ValueError("端口号必须在0-65535之间")
        except ValueError as e:
            messagebox.showerror("错误", f"无效的端口号: {str(e)}")
            return

        self.port_scan_button.config(state="disabled")
        self.network_output.delete(1.0, tk.END)
        self.network_output.insert(tk.END, f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                                      f"正在扫描 {host}:{port} ({protocol})...\n")
        
        threading.Thread(target=self.scan_port, 
                       args=(host, port, protocol), 
                       daemon=True).start()

    def scan_port(self, host, port, protocol):
        try:
            start_time = datetime.now()
            self.network_output.insert(tk.END, f"\n开始端口扫描...\n")
            self.network_output.insert(tk.END, f"目标: {host}:{port}\n")
            self.network_output.insert(tk.END, f"协议: {protocol}\n")
            self.network_output.insert(tk.END, "-" * 50 + "\n")

            if protocol == "TCP":
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                if result == 0:
                    self.network_output.insert(tk.END, f"TCP 端口 {port} 状态: 开放\n")
                else:
                    self.network_output.insert(tk.END, f"TCP 端口 {port} 状态: 关闭 (错误代码: {result})\n")
            else:  # UDP
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2)
                try:
                    sock.sendto(b"", (host, port))
                    data, addr = sock.recvfrom(1024)
                    self.network_output.insert(tk.END, f"UDP 端口 {port} 状态: 开放 (收到响应)\n")
                except socket.timeout:
                    self.network_output.insert(tk.END, f"UDP 端口 {port} 状态: 可能开放 (无响应)\n")
                except Exception as e:
                    self.network_output.insert(tk.END, f"UDP 端口 {port} 状态: 可能关闭 ({str(e)})\n")

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            self.network_output.insert(tk.END, "-" * 50 + "\n")
            self.network_output.insert(tk.END, f"扫描完成，耗时: {duration:.2f} 秒\n")

        except Exception as e:
            self.network_output.insert(tk.END, f"扫描过程中发生错误: {str(e)}\n")
        finally:
            try:
                sock.close()
            except:
                pass
            self.port_scan_button.config(state="normal")

    def show_ping_frame(self):
        self.clear_output()
        self.network_output.delete(1.0, tk.END)
        self.network_output.insert(tk.END, "请输入IP地址或域名，然后点击Ping按钮\n")

    def show_dns_frame(self):
        self.clear_output()
        self.network_output.delete(1.0, tk.END)
        self.network_output.insert(tk.END, "请输入域名，然后点击DNS解析按钮\n")

    def show_about(self):
        messagebox.showinfo("关于", "网络工具集合 v1.0\n\n一个简单的网络工具集合，包含Ping和DNS解析功能。")

    def start_ping(self):
        """开始ping操作"""
        host = self.ip_entry.get().strip()
        if not host:
            messagebox.showerror("错误", "请输入IP地址或域名")
            return

        self.ping_button.config(state="disabled")
        self.network_output.delete(1.0, tk.END)
        self.network_output.insert(tk.END, f"正在Ping {host}...\n")
        
        threading.Thread(target=self.ping, args=(host,), daemon=True).start()

    def ping(self, host):
        """执行ping操作"""
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '4', host]
            
            process = subprocess.Popen(command, stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
            output, error = process.communicate()
            
            if error:
                self.network_output.insert(tk.END, error.decode('gbk', 'ignore'))
            else:
                self.network_output.insert(tk.END, 
                    output.decode('gbk' if platform.system().lower() == 'windows' 
                                else 'utf-8'))
        except Exception as e:
            self.network_output.insert(tk.END, f"执行Ping时发生错误: {str(e)}\n")
        finally:
            self.ping_button.config(state="normal")

    def start_dns(self):
        """开始DNS解析"""
        domain = self.ip_entry.get().strip()
        if not domain:
            messagebox.showerror("错误", "请输入域名")
            return

        self.dns_button.config(state="disabled")
        self.network_output.delete(1.0, tk.END)
        self.network_output.insert(tk.END, f"正在解析域名 {domain}...\n")
        
        threading.Thread(target=self.resolve_dns, args=(domain,), 
                        daemon=True).start()

    def resolve_dns(self, domain):
        """执行DNS解析"""
        try:
            self.network_output.insert(tk.END, f"\n正在解析 {domain}...\n")
            ip_addresses = socket.gethostbyname_ex(domain)
            self.network_output.insert(tk.END, f"主机名: {ip_addresses[0]}\n")
            self.network_output.insert(tk.END, 
                f"别名列表: {', '.join(ip_addresses[1]) if ip_addresses[1] else '无'}\n")
            self.network_output.insert(tk.END, 
                f"IP地址列表: {', '.join(ip_addresses[2])}\n")
        except Exception as e:
            self.network_output.insert(tk.END, f"DNS解析失败: {str(e)}\n")
        finally:
            self.dns_button.config(state="normal")

    def create_status_bar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill="x", side="bottom", padx=5, pady=2)
        
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, relief="sunken")
        self.status_label.pack(fill="x", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkTools(root)
    root.mainloop() 