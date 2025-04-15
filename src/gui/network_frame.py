"""网络工具框架"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from src.core.network import NetworkOperations

class NetworkFrame(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, text="网络工具", padding="5", **kwargs)
        self.create_widgets()

    def create_widgets(self):
        # 创建输入框架
        self.create_input_frame()
        
        # 创建输出区域
        self.create_output_area()

    def create_input_frame(self):
        input_frame = ttk.Frame(self)
        input_frame.pack(fill="x", padx=5, pady=5)

        # IP输入
        ttk.Label(input_frame, text="IP地址/域名:").pack(side="left", padx=5)
        self.ip_entry = ttk.Entry(input_frame, width=30)
        self.ip_entry.pack(side="left", padx=5)

        # 端口输入
        ttk.Label(input_frame, text="端口:").pack(side="left", padx=5)
        self.port_entry = ttk.Entry(input_frame, width=10)
        self.port_entry.pack(side="left", padx=5)

        # 协议选择
        self.protocol_var = tk.StringVar(value="TCP")
        ttk.Radiobutton(input_frame, text="TCP", 
                       variable=self.protocol_var, 
                       value="TCP").pack(side="left", padx=2)
        ttk.Radiobutton(input_frame, text="UDP", 
                       variable=self.protocol_var, 
                       value="UDP").pack(side="left", padx=2)

        # 按钮
        self.create_buttons(input_frame)

    def create_buttons(self, parent):
        button_frame = ttk.Frame(parent)
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

    def create_output_area(self):
        self.output = scrolledtext.ScrolledText(self, height=10, width=70)
        self.output.pack(fill="x", padx=5, pady=5)

    def clear_output(self):
        """清除输出区域"""
        self.output.delete(1.0, tk.END)

    def append_output(self, text: str):
        """添加输出文本"""
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)  # 滚动到最后

    def start_ping(self):
        """开始ping操作"""
        host = self.ip_entry.get().strip()
        if not host:
            messagebox.showerror("错误", "请输入IP地址或域名")
            return

        self.ping_button.config(state="disabled")
        self.clear_output()
        self.append_output(f"正在Ping {host}...")
        
        def ping_thread():
            success, result = NetworkOperations.ping(host)
            self.append_output(result)
            self.ping_button.config(state="normal")

        threading.Thread(target=ping_thread, daemon=True).start()

    def start_dns(self):
        """开始DNS解析"""
        domain = self.ip_entry.get().strip()
        if not domain:
            messagebox.showerror("错误", "请输入域名")
            return

        self.dns_button.config(state="disabled")
        self.clear_output()
        self.append_output(f"正在解析域名 {domain}...")
        
        def dns_thread():
            success, result = NetworkOperations.resolve_dns(domain)
            if success:
                self.append_output(f"主机名: {result['hostname']}")
                self.append_output(f"别名列表: {', '.join(result['aliases']) if result['aliases'] else '无'}")
                self.append_output(f"IP地址列表: {', '.join(result['addresses'])}")
            else:
                self.append_output(f"DNS解析失败: {result['error']}")
            self.dns_button.config(state="normal")

        threading.Thread(target=dns_thread, daemon=True).start()

    def start_port_scan(self):
        """开始端口扫描"""
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
        self.clear_output()
        self.append_output(f"正在扫描 {host}:{port} ({protocol})...")
        
        def scan_thread():
            success, result = NetworkOperations.scan_port(host, port, protocol)
            self.append_output(result)
            self.port_scan_button.config(state="normal")

        threading.Thread(target=scan_thread, daemon=True).start()

    def disable_controls(self):
        """禁用所有控件"""
        self.ip_entry.config(state="disabled")
        self.port_entry.config(state="disabled")
        self.ping_button.config(state="disabled")
        self.dns_button.config(state="disabled")
        self.port_scan_button.config(state="disabled")

    def enable_controls(self):
        """启用所有控件"""
        self.ip_entry.config(state="normal")
        self.port_entry.config(state="normal")
        self.ping_button.config(state="normal")
        self.dns_button.config(state="normal")
        self.port_scan_button.config(state="normal") 