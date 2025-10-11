#!/usr/bin/env python3
"""
批量迁移现有图片到CDN
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Dish
from cdn_service import cdn_service

def migrate_existing_images():
    """迁移现有图片到CDN"""
    print("🔄 开始迁移现有图片到CDN...")
    
    if not cdn_service.is_enabled():
        print("❌ CDN服务未配置，请先配置CDN")
        return False
    
    with app.app_context():
        try:
            # 获取所有有图片的菜品
            dishes = Dish.query.filter(Dish.image.isnot(None)).all()
            
            if not dishes:
                print("ℹ️  没有找到需要迁移的图片")
                return True
            
            print(f"📋 找到 {len(dishes)} 个菜品需要迁移")
            
            success_count = 0
            failed_count = 0
            
            for dish in dishes:
                print(f"🔄 迁移菜品 {dish.dish_number}: {dish.name_cn}")
                
                # 构建本地图片路径
                local_path = os.path.join('static', dish.image)
                
                if not os.path.exists(local_path):
                    print(f"❌ 本地图片不存在: {local_path}")
                    failed_count += 1
                    continue
                
                # 提取文件名
                filename = os.path.basename(dish.image)
                
                # 上传到CDN
                cdn_url = cdn_service.optimize_and_upload(local_path, filename)
                
                if cdn_url:
                    # 更新数据库
                    dish.image_cdn_url = cdn_url
                    db.session.commit()
                    
                    print(f"✅ 迁移成功: {cdn_url}")
                    success_count += 1
                    
                    # 如果不需要本地备份，删除本地文件
                    if not os.environ.get('LOCAL_BACKUP', 'true').lower() == 'true':
                        os.remove(local_path)
                        dish.image = None
                        db.session.commit()
                        print(f"🗑️  已删除本地文件: {local_path}")
                else:
                    print(f"❌ 迁移失败: {dish.image}")
                    failed_count += 1
            
            print(f"\n📊 迁移完成:")
            print(f"   成功: {success_count}")
            print(f"   失败: {failed_count}")
            print(f"   总计: {len(dishes)}")
            
            return True
            
        except Exception as e:
            print(f"❌ 迁移异常: {e}")
            return False

def check_migration_status():
    """检查迁移状态"""
    print("🔍 检查图片迁移状态...")
    
    with app.app_context():
        try:
            # 统计各种状态的菜品
            total_dishes = Dish.query.count()
            dishes_with_local = Dish.query.filter(Dish.image.isnot(None)).count()
            dishes_with_cdn = Dish.query.filter(Dish.image_cdn_url.isnot(None)).count()
            dishes_with_both = Dish.query.filter(
                Dish.image.isnot(None), 
                Dish.image_cdn_url.isnot(None)
            ).count()
            
            print(f"📊 迁移状态统计:")
            print(f"   总菜品数: {total_dishes}")
            print(f"   有本地图片: {dishes_with_local}")
            print(f"   有CDN图片: {dishes_with_cdn}")
            print(f"   同时有本地和CDN: {dishes_with_both}")
            print(f"   仅CDN: {dishes_with_cdn - dishes_with_both}")
            print(f"   仅本地: {dishes_with_local - dishes_with_both}")
            
            # 检查本地文件是否存在
            missing_files = 0
            dishes_with_local_only = Dish.query.filter(
                Dish.image.isnot(None), 
                Dish.image_cdn_url.is_(None)
            ).all()
            
            for dish in dishes_with_local_only:
                local_path = os.path.join('static', dish.image)
                if not os.path.exists(local_path):
                    missing_files += 1
                    print(f"⚠️  本地文件不存在: {dish.image}")
            
            if missing_files > 0:
                print(f"❌ 发现 {missing_files} 个缺失的本地文件")
            else:
                print("✅ 所有本地文件都存在")
            
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            return False
    
    return True

def cleanup_local_images():
    """清理本地图片（仅保留CDN版本）"""
    print("🗑️  开始清理本地图片...")
    
    with app.app_context():
        try:
            # 获取有CDN URL的菜品
            dishes = Dish.query.filter(
                Dish.image_cdn_url.isnot(None),
                Dish.image.isnot(None)
            ).all()
            
            if not dishes:
                print("ℹ️  没有需要清理的本地图片")
                return True
            
            print(f"📋 找到 {len(dishes)} 个菜品需要清理本地图片")
            
            cleaned_count = 0
            
            for dish in dishes:
                local_path = os.path.join('static', dish.image)
                
                if os.path.exists(local_path):
                    os.remove(local_path)
                    print(f"🗑️  已删除: {local_path}")
                
                # 清空数据库中的本地路径
                dish.image = None
                cleaned_count += 1
            
            db.session.commit()
            
            print(f"✅ 清理完成，共清理 {cleaned_count} 个本地图片")
            
        except Exception as e:
            print(f"❌ 清理失败: {e}")
            return False
    
    return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python migrate_images.py migrate    # 迁移图片到CDN")
        print("  python migrate_images.py status     # 检查迁移状态")
        print("  python migrate_images.py cleanup    # 清理本地图片")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'migrate':
        migrate_existing_images()
    elif command == 'status':
        check_migration_status()
    elif command == 'cleanup':
        cleanup_local_images()
    else:
        print(f"❌ 未知命令: {command}")
        print("可用命令: migrate, status, cleanup")

if __name__ == '__main__':
    main()
