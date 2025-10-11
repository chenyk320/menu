#!/usr/bin/env python3
"""
二维码生成脚本
用于生成菜单网站的二维码，供手机扫描访问
"""

import qrcode
import os
from PIL import Image

def generate_qr_code(url, filename='menu_qr.png'):
    """
    生成二维码图片
    
    Args:
        url (str): 要编码的URL
        filename (str): 保存的文件名
    """
    # 创建二维码实例
    qr = qrcode.QRCode(
        version=1,  # 控制二维码的大小
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 错误纠正级别
        box_size=10,  # 每个小方块的像素大小
        border=4,  # 边框大小
    )
    
    # 添加数据
    qr.add_data(url)
    qr.make(fit=True)
    
    # 创建二维码图片
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 保存图片
    img.save(filename)
    print(f"二维码已保存为: {filename}")
    return filename

def main():
    # 获取本机IP地址
    import socket
    
    try:
        # 获取本机IP地址
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # 生成URL
        url = f"http://{local_ip}:8081"
        
        print(f"本机IP地址: {local_ip}")
        print(f"菜单URL: {url}")
        print("正在生成二维码...")
        
        # 生成二维码
        qr_filename = generate_qr_code(url)
        
        print("\n使用方法:")
        print("1. 将生成的二维码图片打印出来")
        print("2. 放在餐厅桌子上供顾客扫描")
        print("3. 顾客扫描后可以直接访问菜单")
        print(f"4. 或者直接访问: {url}")
        
        # 尝试打开二维码图片
        try:
            img = Image.open(qr_filename)
            img.show()
            print("二维码图片已在默认图片查看器中打开")
        except Exception as e:
            print(f"无法自动打开图片: {e}")
            print(f"请手动打开文件: {qr_filename}")
            
    except Exception as e:
        print(f"生成二维码失败: {e}")
        print("请手动输入URL生成二维码")

if __name__ == "__main__":
    main()