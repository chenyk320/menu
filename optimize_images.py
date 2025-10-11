#!/usr/bin/env python3
"""
图片优化脚本
用于压缩和优化菜品图片，提高网站加载速度
"""

import os
import sys
from PIL import Image
import uuid
from pathlib import Path

def optimize_image(input_path, output_path, max_width=800, quality=85):
    """
    优化单张图片
    :param input_path: 输入图片路径
    :param output_path: 输出图片路径
    :param max_width: 最大宽度
    :param quality: JPEG质量 (1-100)
    """
    try:
        with Image.open(input_path) as img:
            # 转换为RGB模式（如果是RGBA）
            if img.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 计算新尺寸
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # 保存优化后的图片
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            # 获取文件大小
            original_size = os.path.getsize(input_path)
            optimized_size = os.path.getsize(output_path)
            compression_ratio = (1 - optimized_size / original_size) * 100
            
            print(f"✅ {os.path.basename(input_path)}: {original_size/1024:.1f}KB → {optimized_size/1024:.1f}KB (压缩 {compression_ratio:.1f}%)")
            
            return True
            
    except Exception as e:
        print(f"❌ 优化失败 {input_path}: {e}")
        return False

def batch_optimize_images(input_dir, output_dir=None, max_width=800, quality=85):
    """
    批量优化图片
    :param input_dir: 输入目录
    :param output_dir: 输出目录（如果为None，则覆盖原文件）
    :param max_width: 最大宽度
    :param quality: JPEG质量
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        return
    
    # 支持的图片格式
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    # 获取所有图片文件
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_path.glob(f'*{ext}'))
        image_files.extend(input_path.glob(f'*{ext.upper()}'))
    
    if not image_files:
        print(f"❌ 在 {input_dir} 中没有找到图片文件")
        return
    
    print(f"🔍 找到 {len(image_files)} 张图片")
    
    # 创建输出目录
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = input_path
    
    # 备份原文件
    backup_dir = input_path / 'backup'
    backup_dir.mkdir(exist_ok=True)
    
    success_count = 0
    total_original_size = 0
    total_optimized_size = 0
    
    for img_file in image_files:
        # 备份原文件
        backup_file = backup_dir / img_file.name
        if not backup_file.exists():
            import shutil
            shutil.copy2(img_file, backup_file)
        
        # 确定输出路径
        if output_dir:
            output_file = output_path / f"{img_file.stem}_optimized.jpg"
        else:
            output_file = img_file.with_suffix('.jpg')
        
        # 优化图片
        original_size = os.path.getsize(img_file)
        total_original_size += original_size
        
        if optimize_image(img_file, output_file, max_width, quality):
            success_count += 1
            total_optimized_size += os.path.getsize(output_file)
            
            # 如果输出到原位置，删除原文件
            if not output_dir and img_file != output_file:
                img_file.unlink()
    
    # 统计信息
    print(f"\n📊 优化完成:")
    print(f"   成功: {success_count}/{len(image_files)}")
    print(f"   总大小: {total_original_size/1024/1024:.1f}MB → {total_optimized_size/1024/1024:.1f}MB")
    print(f"   节省: {(1 - total_optimized_size/total_original_size)*100:.1f}%")
    print(f"   备份位置: {backup_dir}")

def create_webp_versions(input_dir, quality=80):
    """
    创建WebP格式的图片（更小的文件大小）
    """
    input_path = Path(input_dir)
    webp_dir = input_path / 'webp'
    webp_dir.mkdir(exist_ok=True)
    
    image_extensions = {'.jpg', '.jpeg', '.png'}
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_path.glob(f'*{ext}'))
        image_files.extend(input_path.glob(f'*{ext.upper()}'))
    
    print(f"🔄 创建WebP版本...")
    
    for img_file in image_files:
        try:
            with Image.open(img_file) as img:
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                webp_file = webp_dir / f"{img_file.stem}.webp"
                img.save(webp_file, 'WebP', quality=quality, optimize=True)
                
                original_size = os.path.getsize(img_file)
                webp_size = os.path.getsize(webp_file)
                compression_ratio = (1 - webp_size / original_size) * 100
                
                print(f"✅ {img_file.name} → {webp_file.name}: {original_size/1024:.1f}KB → {webp_size/1024:.1f}KB (压缩 {compression_ratio:.1f}%)")
                
        except Exception as e:
            print(f"❌ WebP转换失败 {img_file}: {e}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python optimize_images.py <图片目录> [输出目录] [最大宽度] [质量]")
        print("  python optimize_images.py static/images")
        print("  python optimize_images.py static/images optimized 600 80")
        return
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    max_width = int(sys.argv[3]) if len(sys.argv) > 3 else 800
    quality = int(sys.argv[4]) if len(sys.argv) > 4 else 85
    
    print(f"🚀 开始优化图片...")
    print(f"   输入目录: {input_dir}")
    print(f"   输出目录: {output_dir or '覆盖原文件'}")
    print(f"   最大宽度: {max_width}px")
    print(f"   JPEG质量: {quality}")
    print()
    
    # 优化图片
    batch_optimize_images(input_dir, output_dir, max_width, quality)
    
    # 创建WebP版本
    print(f"\n🔄 创建WebP版本...")
    create_webp_versions(input_dir if not output_dir else output_dir, quality)

if __name__ == '__main__':
    main()
