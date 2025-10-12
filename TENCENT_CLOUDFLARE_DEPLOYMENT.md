# 腾讯云 + Cloudflare 部署指南

## 🎯 方案概述

使用腾讯云CVM服务器 + Cloudflare免费CDN的方案，成本极低且性能优秀。

## 💰 成本分析

### 腾讯云CVM
- **配置**: 1核1GB，50GB SSD
- **价格**: 约35元/月
- **带宽**: 1Mbps（足够使用）

### Cloudflare CDN
- **费用**: 完全免费
- **功能**: 全球加速、DDoS防护、SSL证书
- **限制**: 无流量限制，无请求限制

### 总成本
- **月费用**: 35元（仅服务器费用）
- **年费用**: 420元

## 🚀 部署步骤

### 1. 购买腾讯云CVM

#### 推荐配置
```
实例规格: S5.SMALL1
CPU: 1核
内存: 1GB
存储: 50GB SSD
带宽: 1Mbps
操作系统: Ubuntu 20.04 LTS
```

#### 购买步骤
1. 登录腾讯云控制台
2. 选择CVM云服务器
3. 选择"按量计费"或"包年包月"
4. 选择推荐配置
5. 设置安全组（开放80、443、22端口）

### 2. 配置服务器环境

#### 连接服务器
```bash
ssh root@your-server-ip
```

#### 安装必要软件
```bash
# 更新系统
apt update && apt upgrade -y

# 安装Python3和pip
apt install python3 python3-pip python3-venv -y

# 安装Nginx
apt install nginx -y

# 安装Git
apt install git -y
```

#### 部署应用
```bash
# 克隆代码
git clone https://github.com/your-username/menu.git
cd menu

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env-cloudflare.txt .env
nano .env  # 编辑配置文件
```

### 3. 配置Cloudflare CDN

#### 注册Cloudflare
1. 访问 https://cloudflare.com
2. 注册免费账号
3. 添加您的域名

#### DNS配置
```
A记录: @ -> 您的服务器IP
A记录: www -> 您的服务器IP
CNAME: cdn -> 您的服务器IP
```

#### SSL配置
1. 在Cloudflare面板中启用SSL
2. 选择"Full"模式
3. 启用"Always Use HTTPS"

### 4. 配置Nginx

#### 创建Nginx配置
```bash
nano /etc/nginx/sites-available/menu
```

#### Nginx配置内容
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL配置（Cloudflare提供）
    ssl_certificate /etc/ssl/certs/cloudflare.crt;
    ssl_certificate_key /etc/ssl/private/cloudflare.key;
    
    # 静态文件处理
    location /static/ {
        alias /root/menu/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 应用代理
    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 启用配置
```bash
ln -s /etc/nginx/sites-available/menu /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 5. 配置Gunicorn

#### 安装Gunicorn
```bash
pip install gunicorn
```

#### 创建Gunicorn配置
```bash
nano /root/menu/gunicorn.conf.py
```

#### Gunicorn配置内容
```python
bind = "127.0.0.1:8081"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
```

#### 创建系统服务
```bash
nano /etc/systemd/system/menu.service
```

#### 服务配置内容
```ini
[Unit]
Description=Menu Flask App
After=network.target

[Service]
User=root
WorkingDirectory=/root/menu
Environment=PATH=/root/menu/venv/bin
ExecStart=/root/menu/venv/bin/gunicorn --config gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 启动服务
```bash
systemctl daemon-reload
systemctl enable menu
systemctl start menu
systemctl status menu
```

## 🔧 环境变量配置

### .env文件配置
```bash
# Flask配置
SECRET_KEY=your-very-secure-secret-key
DATABASE_URL=sqlite:///menu.db
UPLOAD_FOLDER=static/images

# Cloudflare CDN配置
CLOUDFLARE_DOMAIN=https://your-domain.com
LOCAL_BACKUP=true

# 管理员配置
ADMIN_USERNAME=chenyaokang
ADMIN_PASSWORD=your-secure-password
```

## 📊 性能优化

### Cloudflare缓存规则
在Cloudflare面板中设置缓存规则：

```
缓存级别: 标准
浏览器缓存TTL: 4小时
边缘缓存TTL: 1个月
```

### 图片优化
```bash
# 批量优化现有图片
python optimize_images.py static/images
```

## 🔒 安全配置

### 防火墙设置
```bash
# 只开放必要端口
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

### 定期备份
```bash
# 创建备份脚本
nano /root/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /root/backup_$DATE.tar.gz /root/menu
# 可以上传到腾讯云COS或其他云存储
```

## 📈 监控和维护

### 日志查看
```bash
# 应用日志
journalctl -u menu -f

# Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 性能监控
```bash
# 系统资源
htop
df -h
free -h
```

## 🎉 部署完成

部署完成后，您的网站将具备：

✅ **全球加速**: Cloudflare全球CDN节点
✅ **安全防护**: DDoS防护、SSL证书
✅ **成本极低**: 月费用仅35元
✅ **高可用性**: 99.9%可用性保证
✅ **易于维护**: 简单的配置和管理

## 🔄 升级路径

随着业务增长，可以：

1. **升级服务器**: 2核2GB → 4核4GB
2. **添加缓存**: Redis缓存
3. **数据库升级**: SQLite → PostgreSQL
4. **负载均衡**: 多服务器部署

## 📞 技术支持

- 腾讯云技术支持
- Cloudflare社区支持
- 项目GitHub Issues

这个方案既经济又实用，完全满足您的需求！
