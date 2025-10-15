#!/usr/bin/env python3
"""
缓存清理脚本
用于清理服务器上的静态文件缓存
"""

import os
import shutil
import glob

def clear_cache():
    """清理缓存文件"""
    print("开始清理缓存...")
    
    # 清理Python缓存
    pycache_dirs = glob.glob("**/__pycache__", recursive=True)
    for pycache_dir in pycache_dirs:
        if os.path.exists(pycache_dir):
            shutil.rmtree(pycache_dir)
            print(f"删除: {pycache_dir}")
    
    # 清理.pyc文件
    pyc_files = glob.glob("**/*.pyc", recursive=True)
    for pyc_file in pyc_files:
        if os.path.exists(pyc_file):
            os.remove(pyc_file)
            print(f"删除: {pyc_file}")
    
    print("缓存清理完成！")

if __name__ == "__main__":
    clear_cache()
