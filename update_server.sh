#!/bin/bash

# 服务器更新脚本
# 用于从GitHub拉取更新并重启服务

echo "开始更新服务器..."

# 停止服务
echo "停止Flask服务..."
sudo systemctl stop menu-app

# 拉取最新代码
echo "从GitHub拉取最新代码..."
cd /home/chenyk/menu
git pull origin main

# 清理缓存
echo "清理缓存..."
python3 clear_cache.py

# 重启服务
echo "重启Flask服务..."
sudo systemctl start menu-app

# 检查服务状态
echo "检查服务状态..."
sudo systemctl status menu-app --no-pager

echo "更新完成！"
echo "请清除浏览器缓存或使用Ctrl+F5强制刷新页面"
