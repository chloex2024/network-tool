# 网络工具大师 (Network Tool Master)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

一款功能强大的网络诊断和文件管理工具，为网络管理员和普通用户提供一站式解决方案。

## ✨ 主要特性

- 🌐 **网络诊断**
  - Ping测试：支持批量测试和持续监控
  - DNS解析：快速域名解析和IP查询
  - 端口扫描：检测指定范围端口状态

- 📂 **文件管理**
  - 文件浏览：直观的树形结构显示
  - 批量操作：支持多文件处理
  - 图片预览：支持多种图片格式
  - 文件删除：安全的文件删除机制

- 🎯 **用户界面**
  - 现代化界面设计
  - 简洁直观的操作逻辑
  - 实时状态反馈
  - 深色/浅色主题支持

## 🚀 快速开始

### 系统要求
- Python 3.8 或更高版本
- Windows 10/11
- 最小内存：2GB RAM
- 磁盘空间：50MB

### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/chloex2024/network-tool.git
cd network-tool-master
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行程序：
```bash
python run.py
```

## 📚 使用指南

### 网络诊断
```python
# 执行Ping测试
输入目标主机地址，点击"开始"按钮
# DNS解析
输入域名，点击"解析"按钮
# 端口扫描
输入目标IP和端口范围，点击"扫描"按钮
```

### 文件管理
```python
# 浏览文件
点击左侧目录树浏览文件系统
# 图片预览
双击图片文件查看预览
# 文件操作
右键点击文件/文件夹进行操作
```

## 🛠 技术栈

- GUI框架：tkinter
- 图像处理：Pillow
- 网络功能：内置socket库
- 日志系统：logging

## 📋 更新日志

### v1.0.0 (2024-01)
- 首次发布
- 基础网络诊断功能
- 文件管理系统
- 图片预览功能

## 🤝 贡献指南

欢迎提交问题和改进建议！提交代码前请确保：

1. 代码风格符合PEP 8规范
2. 添加必要的单元测试
3. 更新相关文档

## 📄 开源协议

本项目采用 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

## 👥 联系方式

- 项目主页：https://github.com/chloex2024/network-tool
- 问题反馈：https://github.com/chloex2024/network-tool/issues
- 邮件联系：support@networkmaster.com

## 🙏 致谢

感谢所有为本项目做出贡献的开发者！

## 📊 项目状态

![Stars](https://img.shields.io/github/stars/chloex2024/network-tool.svg)
![Forks](https://img.shields.io/github/forks/chloex2024/network-tool.svg)
![Issues](https://img.shields.io/github/issues/chloex2024/network-tool.svg)

---

如果觉得这个项目有帮助，欢迎 star ⭐️ 支持一下！

```bash
# 快速体验
git clone https://github.com/chloex2024/network-tool.git
cd network-tool
pip install -r requirements.txt
python run.py
```

让网络管理变得更简单！🚀
