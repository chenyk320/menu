#!/usr/bin/env python3
"""
下载专业的过敏源图标
根据用户提供的图片样式创建图标
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_gluten_icon(size=(64, 64)):
    """创建含麸质谷物图标 - 橙色圆形，白色麦穗"""
    img = Image.new('RGBA', size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制橙色圆形
    margin = 4
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=(255, 140, 0, 255), outline=(255, 255, 255, 255), width=3)
    
    # 绘制白色麦穗
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # 左侧麦穗
    draw.ellipse([center_x-12, center_y-8, center_x-4, center_y+8], fill=(255, 255, 255, 255))
    draw.ellipse([center_x-10, center_y-6, center_x-6, center_y+6], fill=(255, 140, 0, 255))
    
    # 右侧麦穗
    draw.ellipse([center_x+4, center_y-8, center_x+12, center_y+8], fill=(255, 255, 255, 255))
    draw.ellipse([center_x+6, center_y-6, center_x+10, center_y+6], fill=(255, 140, 0, 255))
    
    # 麦穗茎
    draw.line([center_x-8, center_y+8, center_x-8, center_y+12], fill=(255, 255, 255, 255), width=2)
    draw.line([center_x+8, center_y+8, center_x+8, center_y+12], fill=(255, 255, 255, 255), width=2)
    
    return img

def create_crustaceans_icon(size=(64, 64)):
    """创建甲壳类图标 - 红棕色圆形，白色虾"""
    img = Image.new('RGBA', size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制红棕色圆形
    margin = 4
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=(139, 69, 19, 255), outline=(255, 255, 255, 255), width=3)
    
    # 绘制白色虾
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # 虾的身体（弯曲的椭圆形）
    draw.ellipse([center_x-8, center_y-4, center_x+8, center_y+4], fill=(255, 255, 255, 255))
    
    # 虾的头部
    draw.ellipse([center_x-10, center_y-2, center_x-6, center_y+2], fill=(255, 255, 255, 255))
    
    # 虾的尾巴
    draw.ellipse([center_x+6, center_y-3, center_x+10, center_y+3], fill=(255, 255, 255, 255))
    
    return img

def create_eggs_icon(size=(64, 64)):
    """创建鸡蛋图标 - 金黄色圆形，白色鸡蛋"""
    img = Image.new('RGBA', size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制金黄色圆形
    margin = 4
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=(255, 215, 0, 255), outline=(255, 255, 255, 255), width=3)
    
    # 绘制白色鸡蛋
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # 鸡蛋形状
    draw.ellipse([center_x-6, center_y-8, center_x+6, center_y+8], fill=(255, 255, 255, 255))
    
    # 鸡蛋上的裂纹
    draw.line([center_x-4, center_y-2, center_x+4, center_y-2], fill=(255, 215, 0, 255), width=2)
    
    return img

def create_fish_icon(size=(64, 64)):
    """创建鱼类图标 - 青色圆形，白色鱼"""
    img = Image.new('RGBA', size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制青色圆形
    margin = 4
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=(0, 191, 255, 255), outline=(255, 255, 255, 255), width=3)
    
    # 绘制白色鱼
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # 鱼的身体
    draw.ellipse([center_x-8, center_y-4, center_x+8, center_y+4], fill=(255, 255, 255, 255))
    
    # 鱼的头部
    draw.ellipse([center_x-10, center_y-3, center_x-6, center_y+3], fill=(255, 255, 255, 255))
    
    # 鱼的尾巴
    draw.polygon([(center_x+8, center_y-4), (center_x+12, center_y), (center_x+8, center_y+4)], 
                fill=(255, 255, 255, 255))
    
    return img

def create_peanuts_icon(size=(64, 64)):
    """创建花生图标 - 棕色圆形，白色花生"""
    img = Image.new('RGBA', size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制棕色圆形
    margin = 4
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=(139, 69, 19, 255), outline=(255, 255, 255, 255), width=3)
    
    # 绘制白色花生
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # 两个花生
    draw.ellipse([center_x-8, center_y-3, center_x-2, center_y+3], fill=(255, 255, 255, 255))
    draw.ellipse([center_x+2, center_y-3, center_x+8, center_y+3], fill=(255, 255, 255, 255))
    
    return img

def create_soy_icon(size=(64, 64)):
    """创建大豆图标 - 绿色圆形，白色豆子"""
    img = Image.new('RGBA', size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制绿色圆形
    margin = 4
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=(34, 139, 34, 255), outline=(255, 255, 255, 255), width=3)
    
    # 绘制白色豆子
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # 两个豆荚
    draw.ellipse([center_x-8, center_y-4, center_x-2, center_y+4], fill=(255, 255, 255, 255))
    draw.ellipse([center_x+2, center_y-4, center_x+8, center_y+4], fill=(255, 255, 255, 255))
    
    return img

def create_milk_icon(size=(64, 64)):
    """创建牛奶图标 - 紫色圆形，白色牛奶盒"""
    img = Image.new('RGBA', size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制紫色圆形
    margin = 4
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=(128, 0, 128, 255), outline=(255, 255, 255, 255), width=3)
    
    # 绘制白色牛奶盒
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # 牛奶盒主体
    draw.rectangle([center_x-6, center_y-6, center_x+6, center_y+6], fill=(255, 255, 255, 255))
    
    # 牛奶盒顶部
    draw.polygon([(center_x-6, center_y-6), (center_x, center_y-10), (center_x+6, center_y-6)], 
                fill=(255, 255, 255, 255))
    
    return img

def create_nuts_icon(size=(64, 64)):
    """创建坚果图标 - 棕色圆形，白色核桃"""
    img = Image.new('RGBA', size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制棕色圆形
    margin = 4
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=(139, 69, 19, 255), outline=(255, 255, 255, 255), width=3)
    
    # 绘制白色核桃
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # 核桃形状
    draw.ellipse([center_x-6, center_y-6, center_x+6, center_y+6], fill=(255, 255, 255, 255))
    
    # 核桃的纹理
    draw.line([center_x-4, center_y-4, center_x+4, center_y+4], fill=(139, 69, 19, 255), width=1)
    draw.line([center_x-4, center_y+4, center_x+4, center_y-4], fill=(139, 69, 19, 255), width=1)
    
    return img

def create_celery_icon(size=(64, 64)):
    """创建芹菜图标 - 绿色圆形，白色芹菜"""
    img = Image.new('RGBA', size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制绿色圆形
    margin = 4
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=(34, 139, 34, 255), outline=(255, 255, 255, 255), width=3)
    
    # 绘制白色芹菜
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # 芹菜茎
    draw.rectangle([center_x-2, center_y-8, center_x+2, center_y+8], fill=(255, 255, 255, 255))
    
    # 芹菜叶子
    draw.ellipse([center_x-4, center_y-8, center_x, center_y-4], fill=(255, 255, 255, 255))
    draw.ellipse([center_x, center_y-8, center_x+4, center_y-4], fill=(255, 255, 255, 255))
    
    return img

def create_mustard_icon(size=(64, 64)):
    """创建芥末图标 - 黄色圆形，白色挤压瓶"""
    img = Image.new('RGBA', size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制黄色圆形
    margin = 4
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=(255, 255, 0, 255), outline=(255, 255, 255, 255), width=3)
    
    # 绘制白色挤压瓶
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # 瓶子主体
    draw.rectangle([center_x-4, center_y-2, center_x+4, center_y+6], fill=(255, 255, 255, 255))
    
    # 瓶子顶部
    draw.rectangle([center_x-2, center_y-4, center_x+2, center_y-2], fill=(255, 255, 255, 255))
    
    return img

def create_sesame_icon(size=(64, 64)):
    """创建芝麻图标 - 金棕色圆形，白色芝麻"""
    img = Image.new('RGBA', size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制金棕色圆形
    margin = 4
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=(184, 134, 11, 255), outline=(255, 255, 255, 255), width=3)
    
    # 绘制白色芝麻
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # 四个芝麻
    draw.ellipse([center_x-6, center_y-6, center_x-4, center_y-4], fill=(255, 255, 255, 255))
    draw.ellipse([center_x+4, center_y-6, center_x+6, center_y-4], fill=(255, 255, 255, 255))
    draw.ellipse([center_x-6, center_y+4, center_x-4, center_y+6], fill=(255, 255, 255, 255))
    draw.ellipse([center_x+4, center_y+4, center_x+6, center_y+6], fill=(255, 255, 255, 255))
    
    return img

def create_sulfites_icon(size=(64, 64)):
    """创建二氧化硫图标 - 蓝色圆形，白色化学瓶"""
    img = Image.new('RGBA', size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制蓝色圆形
    margin = 4
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=(0, 0, 255, 255), outline=(255, 255, 255, 255), width=3)
    
    # 绘制白色化学瓶
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # 瓶子主体
    draw.rectangle([center_x-4, center_y-2, center_x+4, center_y+6], fill=(255, 255, 255, 255))
    
    # 瓶子颈部
    draw.rectangle([center_x-2, center_y-4, center_x+2, center_y-2], fill=(255, 255, 255, 255))
    
    # SO2文字
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 8)
        draw.text((center_x-6, center_y-1), "SO₂", fill=(0, 0, 255, 255), font=font)
    except:
        pass
    
    return img

def create_lupin_icon(size=(64, 64)):
    """创建羽扇豆图标 - 橙色圆形，白色豆子"""
    img = Image.new('RGBA', size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制橙色圆形
    margin = 4
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=(255, 140, 0, 255), outline=(255, 255, 255, 255), width=3)
    
    # 绘制白色豆子
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # 三个豆子
    draw.ellipse([center_x-6, center_y-4, center_x-2, center_y], fill=(255, 255, 255, 255))
    draw.ellipse([center_x-2, center_y-4, center_x+2, center_y], fill=(255, 255, 255, 255))
    draw.ellipse([center_x+2, center_y-4, center_x+6, center_y], fill=(255, 255, 255, 255))
    
    return img

def create_molluscs_icon(size=(64, 64)):
    """创建软体动物图标 - 灰色圆形，白色贝壳"""
    img = Image.new('RGBA', size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制灰色圆形
    margin = 4
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=(128, 128, 128, 255), outline=(255, 255, 255, 255), width=3)
    
    # 绘制白色贝壳
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # 贝壳形状
    draw.ellipse([center_x-6, center_y-6, center_x+6, center_y+6], fill=(255, 255, 255, 255))
    
    # 贝壳纹理
    for i in range(3):
        y = center_y - 4 + i * 4
        draw.arc([center_x-6, y-2, center_x+6, y+2], 0, 180, fill=(128, 128, 128, 255), width=1)
    
    return img

def main():
    # 确保目录存在
    os.makedirs('static/images/allergens', exist_ok=True)
    
    # 创建所有专业图标
    icons = [
        (create_gluten_icon, 'gluten.png'),
        (create_crustaceans_icon, 'crustaceans.png'),
        (create_eggs_icon, 'eggs.png'),
        (create_fish_icon, 'fish.png'),
        (create_peanuts_icon, 'peanuts.png'),
        (create_soy_icon, 'soy.png'),
        (create_milk_icon, 'milk.png'),
        (create_nuts_icon, 'nuts.png'),
        (create_celery_icon, 'celery.png'),
        (create_mustard_icon, 'mustard.png'),
        (create_sesame_icon, 'sesame.png'),
        (create_sulfites_icon, 'sulfites.png'),
        (create_lupin_icon, 'lupin.png'),
        (create_molluscs_icon, 'molluscs.png')
    ]
    
    for create_func, filename in icons:
        img = create_func()
        img.save(f'static/images/allergens/{filename}', 'PNG')
        print(f"创建专业图标: {filename}")
    
    print("所有专业过敏源图标已创建完成！")

if __name__ == "__main__":
    main()