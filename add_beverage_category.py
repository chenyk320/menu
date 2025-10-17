#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
添加饮品分类
"""

from app import app, db, Category

def add_beverage_category():
    with app.app_context():
        # 检查是否已经存在饮品分类
        existing = Category.query.filter_by(name_cn='饮品').first()
        
        if existing:
            print(f"⚠️ 饮品分类已存在: {existing.name_cn} ({existing.name_it})")
            return
        
        # 获取当前最大的 sort_order
        max_sort = db.session.query(db.func.max(Category.sort_order)).scalar() or 0
        
        # 创建新的饮品分类
        beverage = Category(
            name_cn='饮品',
            name_it='Bevande',
            sort_order=max_sort + 1,
            prefix_letter='H'  # 使用 H 作为前缀字母
        )
        
        db.session.add(beverage)
        db.session.commit()
        
        print(f"✅ 成功添加饮品分类: {beverage.name_cn} ({beverage.name_it})")
        print(f"   前缀字母: {beverage.prefix_letter}")
        print(f"   排序: {beverage.sort_order}")
        
        # 显示所有分类
        print("\n当前所有分类:")
        all_categories = Category.query.order_by(Category.sort_order).all()
        for cat in all_categories:
            print(f"  {cat.prefix_letter} - {cat.name_cn} ({cat.name_it}) - 排序: {cat.sort_order}")

if __name__ == '__main__':
    add_beverage_category()

