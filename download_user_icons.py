#!/usr/bin/env python3
"""
下载用户提供的专业过敏源图标
请将用户提供的图片保存到对应的文件名
"""

import os
import shutil

def setup_icon_directory():
    """设置图标目录"""
    os.makedirs('static/images/allergens', exist_ok=True)
    print("图标目录已准备就绪：static/images/allergens/")
    print("\n请将以下图片保存到对应位置：")
    print("1. 含麸质谷物 (橙色圆形，白色麦穗) → static/images/allergens/gluten.png")
    print("2. 甲壳类 (红棕色圆形，白色虾) → static/images/allergens/crustaceans.png")
    print("3. 鸡蛋 (金黄色圆形，白色鸡蛋) → static/images/allergens/eggs.png")
    print("4. 鱼类 (青色圆形，白色鱼) → static/images/allergens/fish.png")
    print("5. 花生 (棕色圆形，白色花生) → static/images/allergens/peanuts.png")
    print("6. 大豆 (绿色圆形，白色豆子) → static/images/allergens/soy.png")
    print("7. 牛奶 (紫色圆形，白色牛奶盒) → static/images/allergens/milk.png")
    print("8. 坚果 (棕色圆形，白色核桃) → static/images/allergens/nuts.png")
    print("9. 芹菜 (绿色圆形，白色芹菜) → static/images/allergens/celery.png")
    print("10. 芥末 (黄色圆形，白色挤压瓶) → static/images/allergens/mustard.png")
    print("11. 芝麻 (金棕色圆形，白色芝麻) → static/images/allergens/sesame.png")
    print("12. 二氧化硫 (蓝色圆形，白色化学瓶) → static/images/allergens/sulfites.png")
    print("13. 羽扇豆 (橙色圆形，白色豆子) → static/images/allergens/lupin.png")
    print("14. 软体动物 (灰色圆形，白色贝壳) → static/images/allergens/molluscs.png")
    print("\n保存完成后，运行 python check_icons.py 来验证图标")

def check_icons():
    """检查图标文件是否存在"""
    icons = [
        'gluten.png', 'crustaceans.png', 'eggs.png', 'fish.png',
        'peanuts.png', 'soy.png', 'milk.png', 'nuts.png',
        'celery.png', 'mustard.png', 'sesame.png', 'sulfites.png',
        'lupin.png', 'molluscs.png'
    ]
    
    missing_icons = []
    existing_icons = []
    
    for icon in icons:
        path = f'static/images/allergens/{icon}'
        if os.path.exists(path):
            existing_icons.append(icon)
            print(f"✅ {icon} - 已存在")
        else:
            missing_icons.append(icon)
            print(f"❌ {icon} - 缺失")
    
    print(f"\n总计：{len(existing_icons)}/{len(icons)} 个图标已准备就绪")
    
    if missing_icons:
        print(f"\n缺失的图标：{', '.join(missing_icons)}")
        return False
    else:
        print("\n🎉 所有图标都已准备就绪！")
        return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_icons()
    else:
        setup_icon_directory()