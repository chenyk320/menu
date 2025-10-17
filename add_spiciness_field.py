#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库迁移：添加辣度字段
为 Dish 表添加 spiciness_level 字段
"""

from app import app, db, Dish
import sqlite3

def add_spiciness_field():
    """为菜品表添加辣度字段"""
    
    with app.app_context():
        # 获取数据库连接
        db_path = 'instance/menu.db'
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 检查字段是否已存在
            cursor.execute("PRAGMA table_info(dish)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'spiciness_level' in columns:
                print("⚠️  辣度字段已存在，无需添加")
                conn.close()
                return
            
            # 添加新字段
            print("📝 正在添加辣度字段...")
            cursor.execute("ALTER TABLE dish ADD COLUMN spiciness_level INTEGER DEFAULT 0")
            conn.commit()
            
            print("✅ 辣度字段添加成功！")
            print("   字段名: spiciness_level")
            print("   类型: INTEGER")
            print("   默认值: 0 (不辣)")
            print("")
            print("辣度等级说明:")
            print("  0 = 不辣")
            print("  1 = 微辣 🔥")
            print("  2 = 中辣 🔥🔥")
            print("  3 = 特辣 🔥🔥🔥")
            
            conn.close()
            
            # 验证
            print("\n验证更新...")
            dishes = Dish.query.all()
            print(f"✅ 成功！数据库中有 {len(dishes)} 道菜品，所有菜品的辣度默认为 0")
            
        except Exception as e:
            print(f"❌ 添加字段失败: {e}")
            if conn:
                conn.close()

if __name__ == '__main__':
    add_spiciness_field()

