# 服务器部署指南

## 🚀 快速部署

### 1. 安装依赖
```bash
# 安装Python依赖
pip install -r requirements.txt

# 或者使用虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）
```bash
# 复制环境变量模板
cp env_example.txt .env

# 编辑配置文件
nano .env
```

### 3. 初始化数据库
```bash
python -c "from app import init_db; init_db()"
```

### 4. 启动应用
```bash
python app.py
```

## 🔧 生产环境部署

### 使用Gunicorn（推荐）
```bash
# 安装Gunicorn
pip install gunicorn

# 启动应用
gunicorn -w 4 -b 0.0.0.0:8081 app:app
```

### 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /static {
        alias /var/www/mywebsite/menu/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 📋 依赖包说明

### 必需依赖
- `Flask>=2.3.0` - Web框架
- `Flask-SQLAlchemy>=3.0.0` - 数据库ORM
- `Werkzeug>=2.3.0` - WSGI工具
- `Pillow>=9.0.0` - 图片处理
- `qrcode[pil]>=8.0.0` - 二维码生成

### 可选依赖（CDN功能）
- `oss2>=2.19.0` - 阿里云OSS SDK
- `python-dotenv>=1.0.0` - 环境变量管理

## ⚠️ 常见问题

### 1. 缺少依赖包
```bash
# 错误：ModuleNotFoundError: No module named 'oss2'
# 解决：安装缺失的依赖
pip install oss2 python-dotenv
```

### 2. CDN服务不可用
```bash
# 应用会自动检测CDN服务是否可用
# 如果不可用，会使用本地存储
# 控制台会显示：⚠️ CDN服务不可用，将使用本地存储
```

### 3. 数据库初始化
```bash
# 如果数据库不存在，运行：
python -c "from app import init_db; init_db()"
```

### 4. 权限问题
```bash
# 确保应用有写入权限
chmod 755 /var/www/mywebsite/menu
chown -R www-data:www-data /var/www/mywebsite/menu
```

## 🛠️ 配置选项

### 基本配置
```python
# app.py 中的配置
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///menu.db'
app.config['UPLOAD_FOLDER'] = 'static/images'
```

### CDN配置（可选）
```bash
# .env 文件
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET_NAME=menu-images
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
CDN_DOMAIN=https://your-cdn-domain.com
LOCAL_BACKUP=false
```

## 📊 性能优化

### 1. 启用CDN（推荐）
- 配置阿里云OSS + CDN
- 图片自动上传到云端
- 全球加速访问

### 2. 图片优化
- 自动压缩图片到800px宽度
- JPEG质量85%
- 支持懒加载

### 3. 缓存配置
```nginx
# Nginx缓存配置
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 🔍 故障排除

### 检查应用状态
```bash
# 检查进程
ps aux | grep python

# 检查端口
netstat -tlnp | grep 8081

# 检查日志
tail -f /var/log/nginx/error.log
```

### 重启应用
```bash
# 使用systemd（推荐）
sudo systemctl restart menu-app

# 手动重启
pkill -f "python app.py"
python app.py &
```

## 📞 技术支持

如果遇到问题：
1. 检查依赖包是否完整安装
2. 检查环境变量配置
3. 查看应用日志
4. 验证数据库连接

---

通过以上步骤，你的应用应该能够成功部署到服务器上！
