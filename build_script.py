import os
import sys
import shutil
from pathlib import Path
from PIL import Image
import base64
import io

def clean_build():
    """清理构建目录"""
    print("正在清理旧的构建文件...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    # 清理spec文件
    for spec_file in Path('.').glob('*.spec'):
        os.remove(spec_file)

def create_resources():
    """创建资源目录"""
    print("正在创建资源目录...")
    os.makedirs('resources/icons', exist_ok=True)

def check_python():
    """检查Python环境"""
    print("正在检查Python环境...")
    if sys.version_info < (3, 8):
        print("错误：需要Python 3.8或更高版本")
        return False
    return True

def install_dependencies():
    """安装依赖"""
    print("正在更新pip...")
    os.system(f"{sys.executable} -m pip install --upgrade pip")
    
    print("正在安装依赖...")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")
    os.system(f"{sys.executable} -m pip install pyinstaller")

def create_default_icon():
    """创建默认图标文件"""
    print("正在创建默认图标文件...")
    
    # 创建一个简单的图标
    icon_size = 256
    icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    
    # 绘制一个简单的网络图标
    from PIL import ImageDraw
    draw = ImageDraw.Draw(icon)
    
    # 绘制一个圆形作为主体
    margin = 20
    draw.ellipse([margin, margin, icon_size-margin, icon_size-margin], 
                 fill=(65, 105, 225))  # 蓝色
    
    # 保存不同格式的图标
    icons_dir = Path('resources/icons')
    icons_dir.mkdir(parents=True, exist_ok=True)
    
    # Windows ICO
    ico_path = icons_dir / 'app.ico'
    if not ico_path.exists():
        # 创建不同尺寸的图标
        sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
        icons = []
        for size in sizes:
            resized = icon.resize(size, Image.Resampling.LANCZOS)
            icons.append(resized)
        
        # 保存为ICO文件
        icons[0].save(ico_path, format='ICO', sizes=sizes, append_images=icons[1:])
        print(f"已创建Windows图标: {ico_path}")
    
    # macOS ICNS
    icns_path = icons_dir / 'app.icns'
    if not icns_path.exists() and sys.platform == 'darwin':
        icon.save(icns_path, format='ICNS')
        print(f"已创建macOS图标: {icns_path}")
    
    # Linux PNG
    png_path = icons_dir / 'app.png'
    if not png_path.exists():
        icon.save(png_path, format='PNG')
        print(f"已创建Linux图标: {png_path}")

def check_icon_files():
    """检查图标文件是否存在"""
    icons_dir = Path('resources/icons')
    if sys.platform.startswith('win'):
        icon_path = icons_dir / 'app.ico'
    elif sys.platform.startswith('darwin'):
        icon_path = icons_dir / 'app.icns'
    else:
        icon_path = icons_dir / 'app.png'
        
    if not icon_path.exists():
        print(f"未找到图标文件: {icon_path}")
        create_default_icon()
    
    return icon_path

def build_windows():
    """Windows平台打包命令"""
    icon_path = check_icon_files()
    cmd = (
        f"{sys.executable} -m PyInstaller "
        "--name NetworkTools "
        "--clean "
        "--windowed "
        f"--icon={icon_path} "
        "--add-data src/config;src/config "
        "--add-data src/core;src/core "
        "--add-data src/gui;src/gui "
        "--add-data requirements.txt;. "
        "--hidden-import PIL._tkinter_finder "
        "--noconfirm "
        "run.py"
    )
    return cmd

def build_macos():
    """macOS平台打包命令"""
    icon_path = check_icon_files()
    cmd = (
        f"{sys.executable} -m PyInstaller "
        "--name NetworkTools "
        "--clean "
        "--windowed "
        f"--icon={icon_path} "
        "--add-data src/config:src/config "
        "--add-data src/core:src/core "
        "--add-data src/gui:src/gui "
        "--add-data requirements.txt:. "
        "--hidden-import PIL._tkinter_finder "
        "--target-arch universal2 "
        "--noconfirm "
        "run.py"
    )
    return cmd

def build_linux():
    """Linux平台打包命令"""
    icon_path = check_icon_files()
    cmd = (
        f"{sys.executable} -m PyInstaller "
        "--name NetworkTools "
        "--clean "
        "--windowed "
        f"--icon={icon_path} "
        "--add-data src/config:src/config "
        "--add-data src/core:src/core "
        "--add-data src/gui:src/gui "
        "--add-data requirements.txt:. "
        "--hidden-import PIL._tkinter_finder "
        "--noconfirm "
        "run.py"
    )
    return cmd

def main():
    """主函数"""
    try:
        # 检查Python环境
        if not check_python():
            sys.exit(1)

        # 安装依赖
        install_dependencies()

        # 清理旧的构建文件
        clean_build()

        # 检查并创建图标文件
        check_icon_files()

        # 根据操作系统选择打包命令
        if sys.platform.startswith('win'):
            cmd = build_windows()
            separator = ';'
        elif sys.platform.startswith('darwin'):
            cmd = build_macos()
            separator = ':'
        else:
            cmd = build_linux()
            separator = ':'

        print("正在使用PyInstaller打包应用...")
        print(f"执行命令: {cmd}")
        result = os.system(cmd)

        if result == 0:
            print("\n构建成功！")
            if sys.platform.startswith('win'):
                print("可执行文件位置: dist\\NetworkTools\\NetworkTools.exe")
            elif sys.platform.startswith('darwin'):
                print("应用程序位置: dist/NetworkTools.app")
            else:
                print("可执行文件位置: dist/NetworkTools/NetworkTools")
        else:
            print("\n构建失败！")
            sys.exit(1)

    except Exception as e:
        print(f"\n构建过程中出现错误: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 