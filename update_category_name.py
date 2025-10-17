#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
更新分类名称：将"鱼类"改为"海鲜"
"""

from app import app, db, Category

def update_category():
    with app.app_context():
        # 查找名为"鱼类"的分类
        category = Category.query.filter_by(name_cn='鱼类').first()
        
        if category:
            print(f"找到分类: {category.name_cn} ({category.name_it})")
            
            # 更新名称
            category.name_cn = '海鲜'
            category.name_it = 'Frutti di Mare'
            
            db.session.commit()
            print(f"✅ 成功更新为: {category.name_cn} ({category.name_it})")
        else:
            print("⚠️ 未找到名为'鱼类'的分类")
            
            # 显示所有分类
            all_categories = Category.query.all()
            if all_categories:
                print("\n当前所有分类:")
                for cat in all_categories:
                    print(f"  - {cat.name_cn} ({cat.name_it})")
            else:
                print("数据库中没有任何分类")

if __name__ == '__main__':
    update_category()

