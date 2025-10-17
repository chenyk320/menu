# 部署更新说明

本文档说明如何在服务器上部署最新的数据库更新。

## 📋 更新内容

1. **分类名称更新**：将"鱼类"改为"海鲜" (Frutti di Mare)
2. **新增分类**：添加"饮品"分类 (Bevande)

## 🚀 部署步骤

### 方法一：使用一键脚本（推荐）

在服务器上运行以下命令：

```bash
# 进入项目目录
cd /home/chenyk/menu

# 拉取最新代码
git pull origin main

# 运行数据库更新脚本
bash update_database.sh

# 重启服务
sudo systemctl restart menu
```

### 方法二：手动执行

```bash
# 1. 进入项目目录
cd /home/chenyk/menu

# 2. 拉取最新代码
git pull origin main

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 更新分类名称（鱼类 -> 海鲜）
python3 update_category_name.py

# 5. 添加饮品分类
python3 add_beverage_category.py

# 6. 重启服务
sudo systemctl restart menu
```

## ✅ 验证更新

更新完成后，检查以下内容：

1. **前端菜单页面**
   - 侧边栏应该显示"海鲜"分类（不再是"鱼类"）
   - 侧边栏应该显示新的"饮品"分类
   - 意大利语版本应该显示 "Frutti di Mare" 和 "Bevande"

2. **后台管理页面**
   - 分类管理中应该看到"海鲜"和"饮品"分类
   - 添加菜品时的分类下拉框应该包含"海鲜"和"饮品"

3. **清除浏览器缓存**
   - 使用 Ctrl+Shift+Delete (Windows) 或 Cmd+Shift+Delete (Mac)
   - 或者使用硬刷新：Ctrl+F5 (Windows) 或 Cmd+Shift+R (Mac)
   - 或者使用无痕模式访问

## 🔍 故障排除

### 问题：网页没有显示更新

**解决方法**：
1. 确认数据库更新脚本运行成功
2. 检查服务是否成功重启：`sudo systemctl status menu`
3. 清除浏览器缓存
4. 检查服务器日志：`sudo journalctl -u menu -n 50`

### 问题：分类已存在

如果运行脚本时提示"饮品分类已存在"，说明分类已经添加成功，无需重复执行。

### 问题：找不到"鱼类"分类

如果更新脚本提示"未找到名为'鱼类'的分类"，可能是：
1. 已经更新过了
2. 数据库中没有这个分类
3. 分类名称不同

可以在后台管理页面的"分类管理"中手动检查和编辑。

## 📝 脚本说明

- **update_category_name.py**: 更新现有分类名称
- **add_beverage_category.py**: 添加新的饮品分类
- **update_database.sh**: 综合更新脚本，一次执行所有更新

## 🌍 多语言支持

所有分类都支持中文和意大利语：

| 中文 | 意大利语 | 前缀 |
|------|----------|------|
| 主食 | Piatti Principali | A |
| 凉菜 | Piatti Freddi | B |
| 小吃 | Spuntini | C |
| 汤类 | Zuppe | D |
| 海鲜 | Frutti di Mare | E |
| 肉类 | Piatti di Carne | F |
| 素菜 | Piatti Vegetariani | G |
| 饮品 | Bevande | H |

## 💡 提示

- 数据库更新脚本是**幂等的**，可以安全地重复执行
- 更新前建议备份数据库：`cp instance/menu.db instance/menu.db.backup`
- 如有问题，可以从备份恢复：`cp instance/menu.db.backup instance/menu.db`

