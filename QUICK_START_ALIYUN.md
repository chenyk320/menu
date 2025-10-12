# 阿里云快速部署指南

## 概述

本指南提供在阿里云ECS服务器上快速部署菜单应用的步骤。

## 前置条件

- 阿里云ECS实例（推荐：2核4GB，CentOS 7.9或Ubuntu 20.04）
- 域名和DNS解析
- 阿里云OSS存储桶
- 阿里云CDN服务

## 快速部署步骤

### 1. 准备服务器

```bash
# 连接到服务器
ssh root@your-server-ip

# 下载部署脚本
wget https://raw.githubusercontent.com/your-username/menu/main/deploy-aliyun.sh
chmod +x deploy-aliyun.sh
```

### 2. 上传应用代码

```bash
# 方法1：从Git仓库克隆
git clone https://github.com/your-username/menu.git /var/www/menu

# 方法2：上传代码包
scp -r /path/to/menu root@your-server-ip:/var/www/
```

### 3. 配置环境变量

```bash
cd /var/www/menu
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

### 4. 运行部署脚本

```bash
# 使用自签名证书（开发/测试）
./deploy-aliyun.sh -d yourdomain.com -s self-signed

# 使用Let's Encrypt证书（生产环境）
./deploy-aliyun.sh -d yourdomain.com -e your-email@example.com -s letsencrypt
```

### 5. 配置阿里云CDN

1. 登录阿里云控制台
2. 进入CDN服务
3. 添加加速域名：`cdn.yourdomain.com`
4. 配置源站：`yourdomain.com`
5. 配置缓存规则（参考 `aliyun-cdn-config.md`）

### 6. 验证部署

```bash
# 检查服务状态
systemctl status menu
systemctl status nginx

# 检查应用日志
journalctl -u menu -f

# 测试访问
curl -I https://yourdomain.com
curl -I https://yourdomain.com/health
```

## 配置说明

### 1. 阿里云OSS配置

1. 创建OSS存储桶
2. 设置公共读权限
3. 获取AccessKey和SecretKey
4. 配置到 `.env` 文件

### 2. 阿里云CDN配置

1. 开通CDN服务
2. 添加加速域名
3. 配置缓存规则
4. 配置HTTPS证书

### 3. 域名解析

```
A记录：yourdomain.com -> ECS公网IP
CNAME记录：cdn.yourdomain.com -> CDN域名
```

## 常用命令

### 服务管理
```bash
# 重启应用
systemctl restart menu

# 重启Nginx
systemctl restart nginx

# 查看状态
systemctl status menu
systemctl status nginx

# 查看日志
journalctl -u menu -f
tail -f /var/log/nginx/menu_*.log
```

### 应用管理
```bash
# 进入应用目录
cd /var/www/menu

# 激活虚拟环境
source venv/bin/activate

# 数据库操作
python -c "from app import init_db; init_db()"

# 更新代码
git pull origin main
systemctl restart menu
```

### 监控和维护
```bash
# 查看系统资源
htop
df -h
free -h

# 查看网络连接
netstat -tulpn

# 查看进程
ps aux | grep python
ps aux | grep nginx
```

## 故障排除

### 1. 服务无法启动

```bash
# 查看详细错误
journalctl -u menu -n 50

# 检查配置文件
nginx -t

# 检查权限
ls -la /var/www/menu
```

### 2. 访问问题

```bash
# 检查端口
netstat -tulpn | grep :80
netstat -tulpn | grep :443
netstat -tulpn | grep :8081

# 检查防火墙
firewall-cmd --list-all
ufw status
```

### 3. SSL证书问题

```bash
# 检查证书
openssl x509 -in /etc/ssl/certs/yourdomain.com.crt -text -noout

# 测试SSL
openssl s_client -connect yourdomain.com:443
```

## 性能优化

### 1. 服务器优化

```bash
# 调整系统参数
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 65535' >> /etc/sysctl.conf
sysctl -p
```

### 2. Nginx优化

```bash
# 编辑Nginx配置
nano /etc/nginx/nginx.conf

# 调整worker进程数
worker_processes auto;
worker_connections 1024;
```

### 3. 应用优化

```bash
# 使用Gunicorn（可选）
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:8081 app:app
```

## 备份策略

### 1. 数据库备份

```bash
#!/bin/bash
# 数据库备份脚本
DATE=$(date +%Y%m%d_%H%M%S)
cp /var/www/menu/instance/menu.db /var/backups/menu_$DATE.db
```

### 2. 代码备份

```bash
#!/bin/bash
# 代码备份脚本
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /var/backups/menu_code_$DATE.tar.gz /var/www/menu
```

## 安全建议

### 1. 服务器安全

```bash
# 更新系统
yum update -y  # CentOS
apt update && apt upgrade -y  # Ubuntu

# 配置SSH
nano /etc/ssh/sshd_config
# 禁用root登录
# 更改默认端口
# 使用密钥认证
```

### 2. 应用安全

```bash
# 设置文件权限
chmod 600 /var/www/menu/.env
chmod 755 /var/www/menu
chown -R www-data:www-data /var/www/menu
```

## 监控告警

### 1. 系统监控

```bash
# 安装监控工具
yum install htop iotop -y  # CentOS
apt install htop iotop -y  # Ubuntu

# 设置定时任务
crontab -e
# 添加：*/5 * * * * /usr/local/bin/monitor-menu.sh
```

### 2. 日志监控

```bash
# 查看错误日志
tail -f /var/log/nginx/menu_error.log
journalctl -u menu --since "1 hour ago"
```

## 总结

通过以上步骤，您已经成功部署了菜单应用到阿里云环境。主要特点：

- ✅ 高可用性：systemd服务管理
- ✅ 安全性：HTTPS + 安全头
- ✅ 性能：Nginx反向代理
- ✅ 扩展性：CDN加速
- ✅ 监控：日志轮转 + 健康检查

如有问题，请参考详细的部署文档或联系技术支持。
