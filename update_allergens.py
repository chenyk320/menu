#!/usr/bin/env python3
"""
更新过敏源数据脚本
根据欧盟法规 (Regolamento UE n. 1169/2011) 更新过敏源信息
"""

import sys
import os
sys.path.append('.')

from app import app, db, Allergen, Dish

def update_allergens():
    """更新过敏源数据以符合欧盟法规"""
    with app.app_context():
        print("正在更新过敏源数据以符合欧盟法规 (Regolamento UE n. 1169/2011)...")
        
        # 删除所有现有过敏源
        Allergen.query.delete()
        db.session.commit()
        print("已清除现有过敏源数据")
        
        # 创建符合欧盟法规的14类过敏源
        allergens = [
            # 1. Cereali contenenti glutine
            Allergen(name_cn='含麸质谷物', name_it='Cereali contenenti glutine', icon='GL', 
                    description_cn='小麦、大麦、黑麦、燕麦等', 
                    description_it='Grano, orzo, segale, avena, ecc.'),
            
            # 2. Crostacei
            Allergen(name_cn='甲壳类', name_it='Crostacei', icon='CR', 
                    description_cn='虾、蟹、龙虾等', 
                    description_it='Gamberi, granchi, aragoste, ecc.'),
            
            # 3. Uova
            Allergen(name_cn='鸡蛋', name_it='Uova', icon='OV', 
                    description_cn='鸡蛋及其制品', 
                    description_it='Uova e derivati'),
            
            # 4. Pesce
            Allergen(name_cn='鱼类', name_it='Pesce', icon='PS', 
                    description_cn='各种鱼类', 
                    description_it='Tutti i tipi di pesce'),
            
            # 5. Arachidi
            Allergen(name_cn='花生', name_it='Arachidi', icon='AR', 
                    description_cn='花生及其制品', 
                    description_it='Arachidi e derivati'),
            
            # 6. Soia
            Allergen(name_cn='大豆', name_it='Soia', icon='SO', 
                    description_cn='大豆及其制品', 
                    description_it='Soia e derivati'),
            
            # 7. Latte
            Allergen(name_cn='牛奶', name_it='Latte', icon='LT', 
                    description_cn='牛奶及乳制品', 
                    description_it='Latte e latticini'),
            
            # 8. Frutta a guscio
            Allergen(name_cn='坚果', name_it='Frutta a guscio', icon='FR', 
                    description_cn='杏仁、榛子、核桃等', 
                    description_it='Mandorle, nocciole, noci, ecc.'),
            
            # 9. Sedano
            Allergen(name_cn='芹菜', name_it='Sedano', icon='SE', 
                    description_cn='芹菜及其制品', 
                    description_it='Sedano e derivati'),
            
            # 10. Senape
            Allergen(name_cn='芥末', name_it='Senape', icon='SN', 
                    description_cn='芥末籽及其制品', 
                    description_it='Semi di senape e derivati'),
            
            # 11. Semi di sesamo
            Allergen(name_cn='芝麻', name_it='Semi di sesamo', icon='SS', 
                    description_cn='芝麻籽及其制品', 
                    description_it='Semi di sesamo e derivati'),
            
            # 12. Anidride solforosa e solfiti
            Allergen(name_cn='二氧化硫和亚硫酸盐', name_it='Anidride solforosa e solfiti', icon='SU', 
                    description_cn='含量超过10 mg/kg', 
                    description_it='Concentrazione > 10 mg/kg'),
            
            # 13. Lupini
            Allergen(name_cn='羽扇豆', name_it='Lupini', icon='LU', 
                    description_cn='羽扇豆及其制品', 
                    description_it='Lupini e derivati'),
            
            # 14. Molluschi
            Allergen(name_cn='软体动物', name_it='Molluschi', icon='MO', 
                    description_cn='贝类、鱿鱼、章鱼等', 
                    description_it='Cozze, vongole, calamari, ecc.')
        ]
        
        # 添加到数据库
        for allergen in allergens:
            db.session.add(allergen)
        
        db.session.commit()
        print(f"成功添加 {len(allergens)} 个符合欧盟法规的过敏源:")
        
        for i, allergen in enumerate(allergens, 1):
            print(f"{i:2d}. {allergen.name_cn} / {allergen.name_it}")
        
        # 清除所有菜品的过敏源关联（需要重新设置）
        print("\n注意：所有菜品的过敏源关联已被清除，请重新设置菜品的过敏源信息。")
        
        # 检查是否有菜品数据
        dish_count = Dish.query.count()
        if dish_count > 0:
            print(f"发现 {dish_count} 个菜品，建议重新运行 demo_data.py 来更新菜品过敏源信息。")

if __name__ == "__main__":
    update_allergens()