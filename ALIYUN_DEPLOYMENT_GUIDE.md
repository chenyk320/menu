# 阿里云服务器 + 阿里云CDN 部署方案

## 概述

本方案将您的Flask菜单应用部署到阿里云ECS服务器，并使用阿里云CDN加速静态资源访问。

## 架构图

```
用户请求 → 阿里云CDN → 阿里云ECS服务器 → Flask应用
                ↓
            静态资源缓存
                ↓
            动态内容回源
```

## 部署步骤

### 1. 服务器环境准备

#### 1.1 系统要求
- 阿里云ECS实例（推荐配置：2核4GB，CentOS 7.9或Ubuntu 20.04）
- 公网IP和域名
- 安全组开放端口：80, 443, 22

#### 1.2 安装基础软件

```bash
# 更新系统
sudo yum update -y  # CentOS
# 或
sudo apt update && sudo apt upgrade -y  # Ubuntu

# 安装Python 3.8+
sudo yum install python3 python3-pip python3-venv -y  # CentOS
# 或
sudo apt install python3 python3-pip python3-venv -y  # Ubuntu

# 安装Nginx
sudo yum install nginx -y  # CentOS
# 或
sudo apt install nginx -y  # Ubuntu

# 安装Git
sudo yum install git -y  # CentOS
# 或
sudo apt install git -y  # Ubuntu
```

### 2. 应用部署

#### 2.1 克隆代码到服务器

```bash
# 创建应用目录
sudo mkdir -p /var/www/menu
sudo chown $USER:$USER /var/www/menu
cd /var/www/menu

# 克隆代码（替换为您的仓库地址）
git clone https://github.com/your-username/menu.git .

# 或者上传代码包
# scp -r /path/to/menu user@server:/var/www/
```

#### 2.2 创建虚拟环境

```bash
cd /var/www/menu
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2.3 配置环境变量

```bash
# 创建.env文件
cp env_example.txt .env
nano .env
```

配置内容：
```env
# Flask配置
SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=sqlite:///instance/menu.db
UPLOAD_FOLDER=static/images

# 阿里云OSS配置
OSS_ACCESS_KEY_ID=your_oss_access_key_id
OSS_ACCESS_KEY_SECRET=your_oss_access_key_secret
OSS_BUCKET_NAME=your-bucket-name
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com

# CDN配置
CDN_DOMAIN=https://your-cdn-domain.com

# 本地备份配置
LOCAL_BACKUP=true

# 管理员配置
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
```

### 3. 阿里云OSS配置

#### 3.1 创建OSS存储桶

1. 登录阿里云控制台
2. 进入对象存储OSS服务
3. 创建存储桶：
   - 存储桶名称：`your-bucket-name`
   - 地域：选择与ECS相同的地域
   - 读写权限：公共读
   - 存储类型：标准存储

#### 3.2 配置访问权限

1. 在存储桶的"权限管理"中设置：
   - 公共读权限：开启
   - 跨域设置：允许所有来源

#### 3.3 获取访问密钥

1. 进入RAM访问控制
2. 创建用户并分配OSS权限
3. 生成AccessKey ID和AccessKey Secret

### 4. 阿里云CDN配置

#### 4.1 开通CDN服务

1. 登录阿里云控制台
2. 进入CDN服务
3. 开通CDN服务

#### 4.2 添加加速域名

1. 添加加速域名：
   - 加速域名：`cdn.yourdomain.com`
   - 源站信息：选择OSS存储桶
   - 源站地址：`your-bucket-name.oss-cn-hangzhou.aliyuncs.com`

#### 4.3 配置缓存规则

1. 文件类型缓存：
   - 图片文件（jpg, jpeg, png, gif, webp）：缓存30天
   - CSS/JS文件：缓存7天
   - HTML文件：缓存1小时

2. 回源配置：
   - 回源协议：HTTP
   - 回源HOST：源站域名

### 5. Nginx配置

#### 5.1 创建Nginx配置文件

```bash
sudo nano /etc/nginx/sites-available/menu
```

配置内容：
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL证书配置
    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # 静态文件直接由Nginx处理
    location /static/ {
        alias /var/www/menu/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        
        # 启用gzip压缩
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    }
    
    # 图片文件特殊处理
    location ~* \.(jpg|jpeg|png|gif|webp|svg)$ {
        alias /var/www/menu/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        
        # 图片优化
        try_files $uri =404;
    }
    
    # 代理到Flask应用
    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

#### 5.2 启用站点配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/menu /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 6. SSL证书配置

#### 6.1 申请SSL证书

1. 使用阿里云SSL证书服务
2. 申请免费DV证书
3. 验证域名所有权
4. 下载证书文件

#### 6.2 安装证书

```bash
# 创建证书目录
sudo mkdir -p /etc/ssl/certs /etc/ssl/private

# 上传证书文件
sudo cp yourdomain.com.crt /etc/ssl/certs/
sudo cp yourdomain.com.key /etc/ssl/private/

# 设置权限
sudo chmod 644 /etc/ssl/certs/yourdomain.com.crt
sudo chmod 600 /etc/ssl/private/yourdomain.com.key
```

### 7. 系统服务配置

#### 7.1 创建systemd服务文件

```bash
sudo nano /etc/systemd/system/menu.service
```

配置内容：
```ini
[Unit]
Description=Menu Flask Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/menu
Environment=PATH=/var/www/menu/venv/bin
ExecStart=/var/www/menu/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 7.2 启动服务

```bash
# 重新加载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start menu
sudo systemctl enable menu

# 检查状态
sudo systemctl status menu
```

### 8. 数据库初始化

```bash
cd /var/www/menu
source venv/bin/activate
python -c "from app import init_db; init_db()"
```

### 9. 防火墙配置

```bash
# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# Ubuntu
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 10. 监控和日志

#### 10.1 配置日志轮转

```bash
sudo nano /etc/logrotate.d/menu
```

内容：
```
/var/www/menu/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload menu
    endscript
}
```

#### 10.2 设置监控

```bash
# 安装监控工具
sudo yum install htop iotop -y  # CentOS
# 或
sudo apt install htop iotop -y  # Ubuntu

# 设置定时任务检查服务
sudo crontab -e
```

添加：
```bash
# 每分钟检查服务状态
* * * * * systemctl is-active --quiet menu || systemctl restart menu
```

## 性能优化

### 1. CDN优化配置

1. **缓存策略**：
   - 静态资源：30天
   - 动态内容：不缓存

2. **压缩配置**：
   - 启用Gzip压缩
   - 启用Brotli压缩

3. **HTTP/2**：
   - 启用HTTP/2协议

### 2. 服务器优化

1. **Nginx优化**：
   - 调整worker进程数
   - 启用连接复用
   - 配置缓存

2. **Python优化**：
   - 使用Gunicorn替代开发服务器
   - 配置多进程

### 3. 数据库优化

1. **SQLite优化**：
   - 启用WAL模式
   - 调整缓存大小

## 安全配置

### 1. 服务器安全

1. **SSH安全**：
   - 禁用root登录
   - 使用密钥认证
   - 更改默认端口

2. **防火墙**：
   - 只开放必要端口
   - 配置DDoS防护

### 2. 应用安全

1. **HTTPS强制**：
   - 所有请求重定向到HTTPS
   - 配置HSTS

2. **安全头**：
   - 配置CSP
   - 防止XSS攻击

## 备份策略

### 1. 数据库备份

```bash
#!/bin/bash
# 数据库备份脚本
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/menu"
mkdir -p $BACKUP_DIR

# 备份数据库
cp /var/www/menu/instance/menu.db $BACKUP_DIR/menu_$DATE.db

# 清理旧备份（保留30天）
find $BACKUP_DIR -name "menu_*.db" -mtime +30 -delete
```

### 2. 代码备份

```bash
#!/bin/bash
# 代码备份脚本
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/menu"
mkdir -p $BACKUP_DIR

# 备份代码
tar -czf $BACKUP_DIR/menu_code_$DATE.tar.gz /var/www/menu --exclude=venv --exclude=__pycache__
```

## 故障排除

### 1. 常见问题

1. **服务无法启动**：
   ```bash
   sudo journalctl -u menu -f
   ```

2. **Nginx配置错误**：
   ```bash
   sudo nginx -t
   ```

3. **权限问题**：
   ```bash
   sudo chown -R www-data:www-data /var/www/menu
   ```

### 2. 性能监控

1. **系统资源**：
   ```bash
   htop
   iotop
   ```

2. **网络连接**：
   ```bash
   netstat -tulpn
   ```

## 维护指南

### 1. 定期维护

1. **系统更新**：
   ```bash
   sudo yum update -y  # CentOS
   sudo apt update && sudo apt upgrade -y  # Ubuntu
   ```

2. **日志清理**：
   ```bash
   sudo logrotate -f /etc/logrotate.d/menu
   ```

### 2. 监控告警

1. **服务状态监控**
2. **资源使用监控**
3. **错误日志监控**

## 成本优化

### 1. 阿里云资源优化

1. **ECS实例**：选择合适的实例规格
2. **CDN流量**：优化缓存策略减少回源
3. **OSS存储**：选择合适的存储类型

### 2. 性能优化

1. **图片优化**：使用WebP格式
2. **代码优化**：减少不必要的请求
3. **缓存策略**：合理设置缓存时间

## 总结

本部署方案提供了完整的阿里云环境下的Flask应用部署方案，包括：

- ✅ 服务器环境配置
- ✅ 应用部署和配置
- ✅ 阿里云OSS存储配置
- ✅ 阿里云CDN加速配置
- ✅ Nginx反向代理配置
- ✅ SSL证书配置
- ✅ 系统服务配置
- ✅ 安全配置
- ✅ 监控和备份
- ✅ 性能优化

通过这个方案，您的菜单应用将获得：
- 高可用性和稳定性
- 快速的静态资源访问
- 安全的HTTPS访问
- 良好的用户体验
- 合理的成本控制
