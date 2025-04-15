#!/bin/bash
# Unix系统构建脚本

# 确保Python环境正确
python -m pip install --upgrade pip
pip install -r requirements.txt

# 运行构建脚本
python build_script.py 