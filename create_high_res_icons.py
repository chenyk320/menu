#!/usr/bin/env python3
"""
创建高分辨率过敏源图标
使用更高的分辨率和更好的图像质量
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_high_res_icon(text, color, filename, size=(128, 128)):
    """创建高分辨率图标"""
    # 创建高分辨率图像
    img = Image.new('RGBA', size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆形背景
    margin = 8
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=color, outline=(255, 255, 255, 255), width=6)
    
    # 绘制文字
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Arial Bold.ttf', 32)
    except:
        font = ImageFont.load_default()
    
    # 计算文字位置（居中）
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # 绘制文字
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # 保存为高质量PNG
    img.save(f'static/images/allergens/{filename}', 'PNG', optimize=True)
    print(f"创建高分辨率图标: {filename}")

def create_emoji_high_res_icon(emoji, filename, size=(128, 128)):
    """创建高分辨率emoji图标"""
    img = Image.new('RGBA', size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        # 尝试使用Apple Color Emoji字体
        font = ImageFont.truetype('/System/Library/Fonts/Apple Color Emoji.ttc', 80)
    except:
        try:
            # 尝试使用Helvetica字体
            font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 80)
        except:
            font = ImageFont.load_default()
    
    # 计算文字位置（居中）
    bbox = draw.textbbox((0, 0), emoji, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # 绘制emoji
    draw.text((x, y), emoji, font=font)
    
    # 保存为高质量PNG
    img.save(f'static/images/allergens/{filename}', 'PNG', optimize=True)
    print(f"创建高分辨率emoji图标: {filename}")

def main():
    # 确保目录存在
    os.makedirs('static/images/allergens', exist_ok=True)
    
    # 创建高分辨率emoji图标
    emoji_icons = [
        ('🌾', 'gluten.png'),           # 含麸质谷物
        ('🦐', 'crustaceans.png'),      # 甲壳类
        ('🥚', 'eggs.png'),             # 鸡蛋
        ('🐟', 'fish.png'),             # 鱼类
        ('🥜', 'peanuts.png'),          # 花生
        ('🫘', 'soy.png'),              # 大豆
        ('🥛', 'milk.png'),             # 牛奶
        ('🌰', 'nuts.png'),             # 坚果
        ('🥬', 'celery.png'),           # 芹菜
        ('🌶️', 'mustard.png'),          # 芥末
        ('🫘', 'sesame.png'),           # 芝麻
        ('⚗️', 'sulfites.png'),         # 二氧化硫
        ('🫘', 'lupin.png'),            # 羽扇豆
        ('🐚', 'molluscs.png')          # 软体动物
    ]
    
    # 创建高分辨率emoji图标
    for emoji, filename in emoji_icons:
        create_emoji_high_res_icon(emoji, filename)
    
    print("所有高分辨率emoji图标已创建完成！")

if __name__ == "__main__":
    main()