#!/bin/bash

# 增强版服务器更新脚本
# 用于从GitHub拉取更新并重启服务，包含缓存清理

echo "🚀 开始增强版服务器更新..."
echo "=================================="

# 停止服务
echo "⏹️  停止Flask服务..."
sudo systemctl stop menu

# 拉取最新代码
echo "📥 从GitHub拉取最新代码..."
cd /home/chenyk/menu
git pull origin main

# 检查拉取结果
if [ $? -eq 0 ]; then
    echo "✅ 代码拉取成功"
else
    echo "❌ 代码拉取失败"
    exit 1
fi

# 清理Python缓存
echo "🧹 清理Python缓存..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 清理浏览器缓存相关文件
echo "🧹 清理静态文件缓存..."
# 可以在这里添加清理CDN缓存的命令（如果有的话）

# 重启服务
echo "🔄 重启Flask服务..."
sudo systemctl start menu

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 3

# 检查服务状态
echo "📊 检查服务状态..."
if sudo systemctl is-active --quiet menu; then
    echo "✅ 服务启动成功"
else
    echo "❌ 服务启动失败"
    sudo systemctl status menu --no-pager
    exit 1
fi

echo "=================================="
echo "🎉 服务器更新完成！"
echo ""
echo "💡 重要提示："
echo "1. 请清除浏览器缓存 (Ctrl+Shift+Delete)"
echo "2. 强制刷新页面 (Ctrl+F5 或 Cmd+Shift+R)"
echo "3. 或使用无痕模式打开页面"
echo "4. 如果仍有问题，请检查服务器日志"
echo ""
echo "🔗 访问地址: http://your-server-ip:8081"
