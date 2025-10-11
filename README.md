# 意大利餐厅菜单网站

一个支持中意双语的手机扫描二维码菜单网站，具有后台管理功能。

## 功能特性

- 🍽️ **双语支持**: 中文和意大利语切换
- 📱 **移动端优化**: 响应式设计，完美适配手机浏览
- 🏷️ **分类管理**: 菜品按分类展示（开胃菜、第一道菜、第二道菜、甜点、饮品）
- ⚠️ **过敏源标识**: 符合欧盟法规 (Regolamento UE n. 1169/2011) 的14类主要过敏原标识
- 🖼️ **图片支持**: 菜品图片上传和展示
- 🔧 **后台管理**: 简单的添加、删除菜品功能
- 📊 **数据库**: SQLite数据库存储

## 数据库字段

### 菜品表 (Dish)
- `id`: 主键
- `dish_number`: 菜品序号
- `name_cn`: 中文菜品名
- `name_it`: 意大利语菜品名
- `description_it`: 意大利语菜品描述
- `price`: 价格
- `image`: 图片路径
- `category_id`: 分类ID
- `allergens`: 过敏源关联

### 分类表 (Category)
- `id`: 主键
- `name_cn`: 中文分类名
- `name_it`: 意大利语分类名
- `sort_order`: 排序

### 过敏源表 (Allergen)
- `id`: 主键
- `name_cn`: 中文过敏源名
- `name_it`: 意大利语过敏源名
- `icon`: 图标 (emoji)
- `description_cn`: 中文描述
- `description_it`: 意大利语描述

## 欧盟过敏原合规性

本系统完全符合欧盟法规 (Regolamento UE n. 1169/2011) 要求，包含以下14类主要过敏原：

1. **含麸质谷物** (Cereali contenenti glutine) - 小麦、大麦、黑麦、燕麦等
2. **甲壳类** (Crostacei) - 虾、蟹、龙虾等
3. **鸡蛋** (Uova) - 鸡蛋及其制品
4. **鱼类** (Pesce) - 各种鱼类
5. **花生** (Arachidi) - 花生及其制品
6. **大豆** (Soia) - 大豆及其制品
7. **牛奶** (Latte) - 牛奶及乳制品
8. **坚果** (Frutta a guscio) - 杏仁、榛子、核桃、腰果等
9. **芹菜** (Sedano) - 芹菜及其制品
10. **芥末** (Senape) - 芥末籽及其制品
11. **芝麻** (Semi di sesamo) - 芝麻籽及其制品
12. **二氧化硫和亚硫酸盐** (Anidride solforosa e solfiti) - 含量超过10 mg/kg或10 mg/l
13. **羽扇豆** (Lupini) - 羽扇豆及其制品
14. **软体动物** (Molluschi) - 贝类、鱿鱼、章鱼等

## 安装和运行

### 1. 安装依赖
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行应用
```bash
# 激活虚拟环境
source venv/bin/activate

# 启动应用
python app.py

# 添加演示数据（可选）
python demo_data.py
```

### 3. 访问网站
- 菜单页面: http://localhost:8081
- 后台管理: http://localhost:8081/admin

## 使用说明

### 菜单页面
1. 使用顶部语言切换按钮在中意双语间切换
2. 点击分类按钮筛选不同类别的菜品
3. 查看过敏源说明和菜品过敏源标识

### 后台管理
1. 访问 `/admin` 进入管理界面
2. 在"菜品管理"中添加、删除菜品
3. 在"分类管理"中管理菜品分类
4. 在"过敏源管理"中管理过敏源信息

## 二维码生成

要生成二维码供手机扫描，可以使用以下方法：

### 方法1: 使用提供的脚本
```bash
# 激活虚拟环境
source venv/bin/activate

# 生成二维码
python generate_qr.py
```

### 方法2: 使用在线二维码生成器
1. 输入你的服务器地址（如：`http://你的IP:8081`）
2. 生成二维码
3. 打印或显示给顾客扫描

## 项目结构

```
menu/
├── app.py                 # Flask应用主文件
├── requirements.txt       # Python依赖
├── README.md             # 说明文档
├── templates/            # HTML模板
│   ├── menu.html        # 菜单页面
│   └── admin.html       # 后台管理页面
├── static/              # 静态文件
│   ├── css/            # 样式文件
│   │   ├── style.css   # 菜单页面样式
│   │   └── admin.css   # 后台管理样式
│   ├── js/             # JavaScript文件
│   │   ├── menu.js     # 菜单页面脚本
│   │   └── admin.js    # 后台管理脚本
│   └── images/         # 图片文件
├── venv/               # Python虚拟环境
└── menu.db            # SQLite数据库（运行后生成）
```

## 技术栈

- **后端**: Flask (Python)
- **数据库**: SQLite + SQLAlchemy
- **前端**: HTML5, CSS3, JavaScript (原生)
- **图片处理**: Pillow

## 注意事项

1. 首次运行会自动创建数据库和初始化默认数据
2. 图片文件会保存在 `static/images/` 目录下
3. 建议在生产环境中使用更安全的密钥和数据库配置
4. 可以通过修改 `app.py` 中的配置来调整上传文件大小限制等

## 许可证

MIT License