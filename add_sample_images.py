#!/usr/bin/env python3
"""
为现有菜品添加示例图片
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Dish

def add_sample_images():
    """为现有菜品添加示例图片"""
    print("🖼️  为菜品添加示例图片...")
    
    with app.app_context():
        try:
            # 获取所有菜品
            dishes = Dish.query.all()
            
            if not dishes:
                print("ℹ️  没有找到菜品")
                return True
            
            print(f"📋 找到 {len(dishes)} 个菜品")
            
            # 示例图片映射
            sample_images = {
                'A1': 'fea015ac-7472-4301-8705-12241d4221fc_FullRes_1_BBB08287-1024x683.jpg',
                'B1': 'placeholder.jpg',
                'A999': 'placeholder.jpg',
                'A888': 'placeholder.jpg',
                'A777': 'placeholder.jpg'
            }
            
            updated_count = 0
            
            for dish in dishes:
                if dish.dish_number in sample_images:
                    # 检查图片文件是否存在
                    image_file = sample_images[dish.dish_number]
                    image_path = os.path.join('static/images', image_file)
                    
                    if os.path.exists(image_path):
                        dish.image = f"images/{image_file}"
                        updated_count += 1
                        print(f"✅ 为菜品 {dish.dish_number} 添加图片: {image_file}")
                    else:
                        print(f"⚠️  图片文件不存在: {image_path}")
                else:
                    print(f"ℹ️  菜品 {dish.dish_number} 没有对应的示例图片")
            
            if updated_count > 0:
                db.session.commit()
                print(f"✅ 成功为 {updated_count} 个菜品添加了图片")
            else:
                print("ℹ️  没有菜品被更新")
            
            return True
            
        except Exception as e:
            print(f"❌ 添加图片失败: {e}")
            return False

def remove_sample_images():
    """移除示例图片"""
    print("🗑️  移除示例图片...")
    
    with app.app_context():
        try:
            # 获取所有有图片的菜品
            dishes = Dish.query.filter(Dish.image.isnot(None)).all()
            
            if not dishes:
                print("ℹ️  没有找到有图片的菜品")
                return True
            
            print(f"📋 找到 {len(dishes)} 个有图片的菜品")
            
            for dish in dishes:
                dish.image = None
                print(f"🗑️  移除菜品 {dish.dish_number} 的图片")
            
            db.session.commit()
            print(f"✅ 成功移除 {len(dishes)} 个菜品的图片")
            
            return True
            
        except Exception as e:
            print(f"❌ 移除图片失败: {e}")
            return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python add_sample_images.py add     # 添加示例图片")
        print("  python add_sample_images.py remove  # 移除示例图片")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'add':
        add_sample_images()
    elif command == 'remove':
        remove_sample_images()
    else:
        print(f"❌ 未知命令: {command}")
        print("可用命令: add, remove")

if __name__ == '__main__':
    main()

