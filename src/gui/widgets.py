"""自定义控件"""
import tkinter as tk
from tkinter import ttk

class StatusBar(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.label = ttk.Label(self, relief="sunken")
        self.label.pack(fill="x", expand=True)

    def set(self, text: str):
        self.label["text"] = text

class ScrolledTreeview(ttk.Treeview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # 创建滚动条
        self.vsb = ttk.Scrollbar(master, orient="vertical", 
                                command=self.yview)
        self.hsb = ttk.Scrollbar(master, orient="horizontal", 
                                command=self.xview)
        
        # 配置滚动
        self.configure(yscrollcommand=self.vsb.set, 
                      xscrollcommand=self.hsb.set)
        
        # 布局
        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        self.pack(side="left", fill="both", expand=True) 