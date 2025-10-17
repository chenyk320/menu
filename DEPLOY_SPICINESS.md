# 辣度功能部署说明

本文档说明如何在服务器上部署辣度功能。

## 📋 功能概述

添加了菜品辣度等级功能：
- **辣度等级**：0=不辣，1=微辣🔥，2=中辣🔥🔥，3=特辣🔥🔥🔥
- **显示位置**：菜品图片右侧，带动画效果
- **语言支持**：中文和意大利语
- **后台管理**：添加/编辑菜品时可选择辣度等级

## 🚀 服务器部署步骤

### 方法一：一键部署（推荐）

在服务器上运行以下命令：

```bash
# 进入项目目录
cd /home/chenyk/menu

# 拉取最新代码
git pull origin main

# 激活虚拟环境
source venv/bin/activate

# 运行数据库迁移（添加辣度字段）
python3 add_spiciness_field.py

# 重启服务
sudo systemctl restart menu
```

### 方法二：使用单行命令

```bash
cd /home/chenyk/menu && git pull origin main && source venv/bin/activate && python3 add_spiciness_field.py && sudo systemctl restart menu
```

## 📝 详细步骤说明

### 1. 停止服务（可选）

```bash
sudo systemctl stop menu
```

### 2. 备份数据库（强烈推荐）

```bash
cd /home/chenyk/menu
cp instance/menu.db instance/menu.db.backup_$(date +%Y%m%d_%H%M%S)
```

### 3. 拉取最新代码

```bash
git pull origin main
```

预期输出：
```
Updating 927c5fe..6299f8b
Fast-forward
 add_spiciness_field.py      | 56 ++++++++++++++++++++++++++++++++
 app.py                      |  6 ++--
 static/css/style.css        | 33 +++++++++++++++++++
 static/js/admin.js          |  1 +
 static/js/menu.js           | 28 ++++++++++++----
 templates/admin.html        | 18 +++++++++++
 6 files changed, 132 insertions(+), 8 deletions(-)
 create mode 100644 add_spiciness_field.py
```

### 4. 激活虚拟环境

```bash
source venv/bin/activate
```

### 5. 运行数据库迁移

```bash
python3 add_spiciness_field.py
```

预期输出：
```
📝 正在添加辣度字段...
✅ 辣度字段添加成功！
   字段名: spiciness_level
   类型: INTEGER
   默认值: 0 (不辣)

辣度等级说明:
  0 = 不辣
  1 = 微辣 🔥
  2 = 中辣 🔥🔥
  3 = 特辣 🔥🔥🔥

验证更新...
✅ 成功！数据库中有 X 道菜品，所有菜品的辣度默认为 0
```

### 6. 清理缓存（可选但推荐）

```bash
# 清理Python缓存
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
```

### 7. 重启服务

```bash
sudo systemctl restart menu
```

### 8. 检查服务状态

```bash
sudo systemctl status menu
```

预期显示 `active (running)`

## ✅ 验证部署

### 1. 检查后台管理

访问：`http://your-server-ip:8081/admin`

- 点击"添加菜品"或"编辑菜品"
- 应该看到"辣度等级 (Piccante)"下拉框
- 选项：不辣、微辣🔥、中辣🔥🔥、特辣🔥🔥🔥

### 2. 测试添加辣度

1. 编辑一道菜品
2. 选择辣度等级（例如：中辣🔥🔥）
3. 保存

### 3. 检查前端显示

访问：`http://your-server-ip:8081`

- 找到设置了辣度的菜品
- 菜品图片右侧应该显示相应数量的🔥图标
- 图标应该有轻微的脉动动画效果

### 4. 测试多语言

- 切换到意大利语界面
- 辣度图标应该正常显示

### 5. 清除浏览器缓存

使用以下方法之一：
- **硬刷新**：Ctrl+F5 (Windows) 或 Cmd+Shift+R (Mac)
- **清除缓存**：Ctrl+Shift+Delete
- **无痕模式**：打开无痕窗口访问

## 🔍 故障排除

### 问题1：辣度字段已存在

**现象**：运行迁移脚本时显示"⚠️ 辣度字段已存在"

**解决**：这是正常的，说明字段已添加，可以直接重启服务

### 问题2：前端看不到辣度图标

**可能原因**：
1. 浏览器缓存

**解决方法**：
```bash
# 强制刷新页面（清除缓存）
Ctrl+F5 或 Cmd+Shift+R
```

2. CSS文件未更新

**解决方法**：
```bash
# 检查CSS文件是否最新
ls -l static/css/style.css

# 如果不是最新的，重新拉取
git pull origin main
sudo systemctl restart menu
```

### 问题3：后台看不到辣度选择框

**可能原因**：
1. HTML文件未更新
2. 浏览器缓存

**解决方法**：
```bash
# 检查文件
ls -l templates/admin.html

# 清除浏览器缓存并重新登录
```

### 问题4：服务无法启动

**检查日志**：
```bash
sudo journalctl -u menu -n 50
```

**常见错误**：
- 数据库迁移失败：检查 add_spiciness_field.py 是否正确运行
- 权限问题：确保数据库文件有正确的权限

**解决方法**：
```bash
# 检查数据库权限
ls -l instance/menu.db

# 如果需要，修复权限
chmod 644 instance/menu.db
```

### 问题5：辣度数据没有保存

**检查**：
1. 后台管理表单是否包含辣度字段
2. 浏览器控制台是否有错误

**解决方法**：
```bash
# 检查JavaScript文件
grep -n "spiciness_level" static/js/admin.js

# 应该看到相关代码
```

## 📊 数据库变更详情

### 新增字段

| 表名 | 字段名 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| dish | spiciness_level | INTEGER | 0 | 辣度等级 |

### 辣度等级对照表

| 值 | 中文 | 意大利语 | 显示 |
|----|------|----------|------|
| 0 | 不辣 | Non piccante | （不显示） |
| 1 | 微辣 | Leggermente piccante | 🔥 |
| 2 | 中辣 | Piccante | 🔥🔥 |
| 3 | 特辣 | Molto piccante | 🔥🔥🔥 |

## 📁 修改的文件列表

1. **app.py**
   - 添加 `spiciness_level` 字段到 Dish 模型
   - 更新添加/编辑菜品API
   - 更新获取菜品列表API

2. **add_spiciness_field.py**（新建）
   - 数据库迁移脚本
   - 为现有菜品添加辣度字段

3. **templates/admin.html**
   - 添加辣度选择下拉框（添加表单）
   - 添加辣度选择下拉框（编辑表单）

4. **static/js/admin.js**
   - 更新编辑菜品时加载辣度数据

5. **static/js/menu.js**
   - 在菜品卡片中渲染辣度标识

6. **static/css/style.css**
   - 添加辣度标识样式
   - 添加脉动动画效果

## 🔄 回滚步骤（如有需要）

如果需要回滚到之前的版本：

```bash
# 1. 恢复数据库备份
cd /home/chenyk/menu
cp instance/menu.db.backup_YYYYMMDD_HHMMSS instance/menu.db

# 2. 回滚Git
git reset --hard 927c5fe

# 3. 重启服务
sudo systemctl restart menu
```

## 💡 使用建议

1. **设置辣度**：建议为麻辣类菜品设置合适的辣度等级
2. **客户体验**：辣度图标可以帮助客人快速识别菜品的辣度
3. **更新菜单**：逐步为现有菜品添加辣度信息

## 🎯 后续维护

- 所有现有菜品默认辣度为0（不辣）
- 可以通过后台管理逐个编辑菜品，设置合适的辣度
- 新添加的菜品可以在创建时直接设置辣度

## 📞 技术支持

如有问题，请检查：
1. 服务器日志：`sudo journalctl -u menu -n 100`
2. 数据库状态：`sqlite3 instance/menu.db "PRAGMA table_info(dish)"`
3. 文件权限：`ls -la instance/menu.db`

---

**部署完成后，记得：**
✅ 测试添加/编辑菜品功能
✅ 测试前端显示效果
✅ 测试中英文切换
✅ 清除浏览器缓存查看最新效果

