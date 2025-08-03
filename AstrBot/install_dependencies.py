#!/usr/bin/env python3
"""
安装批量PDF处理工具的依赖
"""

import subprocess
import sys

def install_package(package):
    """安装Python包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ 安装成功: {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ 安装失败: {package}")
        return False

def main():
    print("🔧 开始安装批量PDF处理工具依赖...")
    
    # 必需的包列表
    packages = [
        "aiofiles",
        "aiohttp", 
        "PyMuPDF",  # fitz模块
        "tqdm",
        "numpy"
    ]
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 安装结果: {success_count}/{len(packages)} 个包安装成功")
    
    if success_count == len(packages):
        print("🎉 所有依赖安装完成！")
        print("\n💡 使用方法:")
        print("1. 批量上传PDF: python batch_knowledge_processor.py /path/to/pdf/dir")
        print("2. 仅提取文本: python batch_knowledge_processor.py /path/to/pdf/dir --text-only")
        print("3. 自定义设置: python batch_knowledge_processor.py /path/to/pdf/dir --kb-name '我的知识库' --max-pages 100")
    else:
        print("⚠️  部分依赖安装失败，请手动安装")

if __name__ == "__main__":
    main() 