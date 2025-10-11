#!/usr/bin/env python3
"""
演示有图片和无图片的菜品显示
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Dish

def create_mixed_dishes():
    """创建有图片和无图片的菜品混合示例"""
    print("🍽️  创建有图片和无图片的菜品示例...")
    
    with app.app_context():
        try:
            # 先清理现有菜品
            Dish.query.delete()
            db.session.commit()
            print("🗑️  清理了现有菜品")
            
            # 创建有图片的菜品
            dishes_with_images = [
                {
                    'dish_number': 'A1',
                    'name_cn': '美味开胃菜',
                    'name_it': 'Antipasto Delizioso',
                    'price': 8.50,
                    'image': 'images/fea015ac-7472-4301-8705-12241d4221fc_FullRes_1_BBB08287-1024x683.jpg',
                    'category_id': 1,
                    'is_popular': True
                },
                {
                    'dish_number': 'A2',
                    'name_cn': '特色沙拉',
                    'name_it': 'Insalata Speciale',
                    'price': 12.00,
                    'image': 'images/placeholder.jpg',
                    'category_id': 1,
                    'is_new': True
                }
            ]
            
            # 创建无图片的菜品
            dishes_without_images = [
                {
                    'dish_number': 'B1',
                    'name_cn': '经典意面',
                    'name_it': 'Pasta Classica',
                    'price': 15.50,
                    'image': None,
                    'category_id': 2
                },
                {
                    'dish_number': 'B2',
                    'name_cn': '传统披萨',
                    'name_it': 'Pizza Tradizionale',
                    'price': 18.00,
                    'image': None,
                    'category_id': 2,
                    'is_popular': True
                },
                {
                    'dish_number': 'C1',
                    'name_cn': '新鲜果汁',
                    'name_it': 'Succo Fresco',
                    'price': 5.50,
                    'image': None,
                    'category_id': 3,
                    'is_new': True
                }
            ]
            
            # 添加所有菜品
            all_dishes = dishes_with_images + dishes_without_images
            
            for dish_data in all_dishes:
                dish = Dish(**dish_data)
                db.session.add(dish)
            
            db.session.commit()
            
            print(f"✅ 成功创建 {len(all_dishes)} 个菜品:")
            print(f"   - 有图片: {len(dishes_with_images)} 个")
            print(f"   - 无图片: {len(dishes_without_images)} 个")
            
            # 显示创建的菜品
            print("\n📋 创建的菜品:")
            for dish in Dish.query.all():
                image_status = "有图片" if dish.image else "无图片"
                print(f"   {dish.dish_number}: {dish.name_cn} - {image_status}")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建菜品失败: {e}")
            return False

def main():
    """主函数"""
    create_mixed_dishes()

if __name__ == '__main__':
    main()
