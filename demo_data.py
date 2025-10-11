#!/usr/bin/env python3
"""
演示数据脚本
添加一些示例菜品数据用于测试
"""

import sys
import os
sys.path.append('.')

from app import app, db, Dish, Category, Allergen

def add_demo_data():
    """添加演示数据"""
    with app.app_context():
        # 检查是否已有数据
        if Dish.query.first():
            print("数据库中已有菜品数据，正在更新为符合欧盟法规的演示数据...")
            # 清除现有菜品数据
            # 首先清除关联表数据
            db.session.execute(db.text("DELETE FROM dish_allergen"))
            Dish.query.delete()
            db.session.commit()
            print("已清除现有菜品数据")
        
        # 获取分类和过敏源
        categories = Category.query.all()
        allergens = Allergen.query.all()
        
        if not categories or not allergens:
            print("请先运行主应用初始化数据库")
            return
        
        # 创建演示菜品（符合欧盟过敏原标准）
        demo_dishes = [
            {
                'dish_number': 'A001',
                'name_cn': '意大利开胃拼盘',
                'name_it': 'Antipasto Italiano',
                'description_it': 'Una selezione di salumi, formaggi e verdure sott\'olio',
                'price': 18.50,
                'category_id': next((c.id for c in categories if c.name_cn == '开胃菜'), None),
                'allergen_ids': [a.id for a in allergens if a.name_cn in ['牛奶']]
            },
            {
                'dish_number': 'P001',
                'name_cn': '经典意大利面',
                'name_it': 'Spaghetti Classici',
                'description_it': 'Spaghetti con pomodoro fresco, basilico e parmigiano',
                'price': 14.00,
                'category_id': next((c.id for c in categories if c.name_cn == '第一道菜'), None),
                'allergen_ids': [a.id for a in allergens if a.name_cn in ['含麸质谷物', '牛奶']]
            },
            {
                'dish_number': 'P002',
                'name_cn': '海鲜意面',
                'name_it': 'Spaghetti ai Frutti di Mare',
                'description_it': 'Spaghetti con cozze, vongole e gamberi in salsa di pomodoro',
                'price': 22.00,
                'category_id': next((c.id for c in categories if c.name_cn == '第一道菜'), None),
                'allergen_ids': [a.id for a in allergens if a.name_cn in ['含麸质谷物', '甲壳类', '软体动物']]
            },
            {
                'dish_number': 'P003',
                'name_cn': '芝麻意面',
                'name_it': 'Spaghetti al Sesamo',
                'description_it': 'Spaghetti con salsa di sesamo e verdure croccanti',
                'price': 16.00,
                'category_id': next((c.id for c in categories if c.name_cn == '第一道菜'), None),
                'allergen_ids': [a.id for a in allergens if a.name_cn in ['含麸质谷物', '芝麻']]
            },
            {
                'dish_number': 'S001',
                'name_cn': '烤三文鱼',
                'name_it': 'Salmone Grigliato',
                'description_it': 'Filetto di salmone con verdure di stagione e patate arrosto',
                'price': 26.00,
                'category_id': next((c.id for c in categories if c.name_cn == '第二道菜'), None),
                'allergen_ids': [a.id for a in allergens if a.name_cn in ['鱼类']]
            },
            {
                'dish_number': 'S002',
                'name_cn': '意式烤鸡',
                'name_it': 'Pollo Arrosto',
                'description_it': 'Pollo intero arrosto con erbe aromatiche e contorni',
                'price': 20.00,
                'category_id': next((c.id for c in categories if c.name_cn == '第二道菜'), None),
                'allergen_ids': []
            },
            {
                'dish_number': 'S003',
                'name_cn': '坚果烤鸡',
                'name_it': 'Pollo alle Noci',
                'description_it': 'Pollo arrosto con salsa alle noci e mandorle',
                'price': 22.00,
                'category_id': next((c.id for c in categories if c.name_cn == '第二道菜'), None),
                'allergen_ids': [a.id for a in allergens if a.name_cn in ['坚果']]
            },
            {
                'dish_number': 'D001',
                'name_cn': '提拉米苏',
                'name_it': 'Tiramisù',
                'description_it': 'Il classico dolce al caffè con mascarpone e cacao',
                'price': 8.50,
                'category_id': next((c.id for c in categories if c.name_cn == '甜点'), None),
                'allergen_ids': [a.id for a in allergens if a.name_cn in ['牛奶', '鸡蛋', '含麸质谷物']]
            },
            {
                'dish_number': 'D002',
                'name_cn': '意式冰淇淋',
                'name_it': 'Gelato Italiano',
                'description_it': 'Gelato artigianale in tre gusti: vaniglia, cioccolato e fragola',
                'price': 6.00,
                'category_id': next((c.id for c in categories if c.name_cn == '甜点'), None),
                'allergen_ids': [a.id for a in allergens if a.name_cn in ['牛奶']]
            },
            {
                'dish_number': 'D003',
                'name_cn': '花生酱蛋糕',
                'name_it': 'Torta al Burro di Arachidi',
                'description_it': 'Torta morbida con burro di arachidi e cioccolato',
                'price': 7.50,
                'category_id': next((c.id for c in categories if c.name_cn == '甜点'), None),
                'allergen_ids': [a.id for a in allergens if a.name_cn in ['花生', '鸡蛋', '含麸质谷物', '牛奶']]
            },
            {
                'dish_number': 'B001',
                'name_cn': '意大利咖啡',
                'name_it': 'Caffè Italiano',
                'description_it': 'Espresso o cappuccino preparato con caffè italiano',
                'price': 3.50,
                'category_id': next((c.id for c in categories if c.name_cn == '饮品'), None),
                'allergen_ids': [a.id for a in allergens if a.name_cn in ['牛奶']]
            },
            {
                'dish_number': 'B002',
                'name_cn': '意式柠檬水',
                'name_it': 'Limonata Italiana',
                'description_it': 'Acqua frizzante con limone fresco e menta',
                'price': 4.50,
                'category_id': next((c.id for c in categories if c.name_cn == '饮品'), None),
                'allergen_ids': []
            },
            {
                'dish_number': 'B003',
                'name_cn': '豆浆拿铁',
                'name_it': 'Latte di Soia',
                'description_it': 'Caffè con latte di soia e sciroppo di vaniglia',
                'price': 4.00,
                'category_id': next((c.id for c in categories if c.name_cn == '饮品'), None),
                'allergen_ids': [a.id for a in allergens if a.name_cn in ['大豆']]
            }
        ]
        
        # 添加菜品到数据库
        for dish_data in demo_dishes:
            dish = Dish(
                dish_number=dish_data['dish_number'],
                name_cn=dish_data['name_cn'],
                name_it=dish_data['name_it'],
                description_it=dish_data['description_it'],
                price=dish_data['price'],
                category_id=dish_data['category_id']
            )
            
            db.session.add(dish)
            db.session.flush()  # 获取ID
            
            # 添加过敏源关联
            for allergen_id in dish_data['allergen_ids']:
                allergen = Allergen.query.get(allergen_id)
                if allergen:
                    dish.allergens.append(allergen)
        
        db.session.commit()
        print(f"成功添加 {len(demo_dishes)} 个演示菜品")
        print("演示菜品包括:")
        for dish_data in demo_dishes:
            print(f"- {dish_data['dish_number']}: {dish_data['name_cn']} / {dish_data['name_it']} (€{dish_data['price']})")

if __name__ == "__main__":
    add_demo_data()