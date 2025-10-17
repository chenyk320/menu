#!/bin/bash

# 综合数据库更新脚本
# 包含：更新分类名称和添加新分类

echo "🚀 开始更新数据库..."
echo "=================================="

# 进入项目目录
cd /home/chenyk/menu

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 1. 更新鱼类为海鲜
echo ""
echo "1️⃣ 更新分类名称: 鱼类 -> 海鲜..."
python3 update_category_name.py

# 2. 添加饮品分类
echo ""
echo "2️⃣ 添加饮品分类..."
python3 add_beverage_category.py

echo ""
echo "=================================="
echo "✅ 数据库更新完成！"
echo ""
echo "💡 接下来需要重启服务:"
echo "   sudo systemctl restart menu"

