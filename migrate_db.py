#!/usr/bin/env python3
"""
数据库迁移脚本
用于添加CDN相关字段到现有数据库
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def migrate_database():
    """迁移数据库，添加CDN字段和纯素字段"""
    print("🔄 开始数据库迁移...")
    
    with app.app_context():
        try:
            # 检查是否需要添加新字段
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('dish')
            column_names = [col['name'] for col in columns]
            
            if 'image_cdn_url' not in column_names:
                print("📝 添加 image_cdn_url 字段...")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE dish ADD COLUMN image_cdn_url VARCHAR(500)'))
                    conn.commit()
                print("✅ image_cdn_url 字段添加成功")
            else:
                print("ℹ️  image_cdn_url 字段已存在")
            
            if 'is_vegan' not in column_names:
                print("📝 添加 is_vegan 字段...")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE dish ADD COLUMN is_vegan BOOLEAN DEFAULT 0'))
                    conn.commit()
                print("✅ is_vegan 字段添加成功")
            else:
                print("ℹ️  is_vegan 字段已存在")
            
            print("✅ 数据库迁移完成")
            
        except Exception as e:
            print(f"❌ 数据库迁移失败: {e}")
            return False
    
    return True

def rollback_migration():
    """回滚迁移"""
    print("🔄 开始回滚数据库迁移...")
    
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('dish')
            column_names = [col['name'] for col in columns]
            
            if 'image_cdn_url' in column_names:
                print("📝 删除 image_cdn_url 字段...")
                # 注意：SQLite不支持DROP COLUMN，需要重建表
                print("⚠️  SQLite不支持直接删除字段，需要手动处理")
                print("   建议备份数据后重新创建数据库")
            else:
                print("ℹ️  image_cdn_url 字段不存在")
            
            print("✅ 数据库回滚完成")
            
        except Exception as e:
            print(f"❌ 数据库回滚失败: {e}")
            return False
    
    return True

def check_migration_status():
    """检查迁移状态"""
    print("🔍 检查数据库迁移状态...")
    
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('dish')
            column_names = [col['name'] for col in columns]
            
            print("📋 Dish表字段:")
            for col in columns:
                print(f"   - {col['name']}: {col['type']}")
            
            if 'image_cdn_url' in column_names:
                print("✅ CDN字段已存在")
            else:
                print("❌ CDN字段不存在，需要迁移")
            
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            return False
    
    return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python migrate_db.py migrate    # 执行迁移")
        print("  python migrate_db.py rollback   # 回滚迁移")
        print("  python migrate_db.py status     # 检查状态")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'migrate':
        migrate_database()
    elif command == 'rollback':
        rollback_migration()
    elif command == 'status':
        check_migration_status()
    else:
        print(f"❌ 未知命令: {command}")
        print("可用命令: migrate, rollback, status")

if __name__ == '__main__':
    main()
