## 阿里云服务器部署指南（从 GitHub 部署，排除 ESA/OSS 配置）

本指南描述如何从 GitHub 拉取本项目并在阿里云 ECS 上部署，使用 Gunicorn + Nginx + systemd 的常见生产方案。文档不包含 ESA 与 OSS 的配置（你将后续自行配置）。

### 适用环境
- 操作系统：Ubuntu 20.04/22.04（其他 Linux 发行版可参考）
- 已具备：域名（可选）、服务器公网 IP、可用的 SSH 访问

### 1. 基础环境准备
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip nginx

# 可选：开放 80/443 端口（Ubuntu UFW）
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

### 2. 拉取代码与目录布局
建议部署到 `/opt/menu`（也可选择 `/srv/menu` 等）。
```bash
sudo mkdir -p /opt/menu
sudo chown -R $USER:$USER /opt/menu
cd /opt/menu

# 使用 SSH 克隆（确保已将服务器的 SSH 公钥加入 GitHub）
git clone git@github.com:chenyk320/menu.git .
```

### 3. Python 依赖安装
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# 生产推荐使用 Gunicorn
pip install gunicorn
```

### 4. 环境变量与配置
项目支持从环境变量读取配置，你可以在项目根目录创建 `.env`（不会被提交）。例如：
```bash
cat > .env << 'EOF'
SECRET_KEY=please-change-me
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this
# 若使用 SQLite（默认）：无需设置 DATABASE_URL；否则：
# DATABASE_URL=sqlite:///menu.db

# 你将来配置的 ESA/OSS 可在此放置，当前先留空
# OSS_ACCESS_KEY_ID=
# OSS_ACCESS_KEY_SECRET=
# OSS_BUCKET_NAME=
# OSS_ENDPOINT=
# CDN_DOMAIN=
# CLOUDFLARE_DOMAIN=
EOF
```

### 5. 初始化数据库（首次部署）
若使用 Gunicorn 启动，`if __name__ == '__main__'` 不会执行，因此需要手动初始化数据库：
```bash
source venv/bin/activate
python -c "from app import init_db; init_db()"

# 可选：导入演示数据
# python demo_data.py
```

### 6. 使用 Gunicorn 启动（临时验证）
```bash
source venv/bin/activate
gunicorn -b 127.0.0.1:8000 -w 2 app:app
# 看到启动正常后，Ctrl+C 退出，继续配置 systemd 与 Nginx
```

### 7. 配置 systemd 服务
创建 `menu.service` 以便开机自启与后台运行。
```bash
sudo tee /etc/systemd/system/menu.service > /dev/null << 'EOF'
[Unit]
Description=Menu Flask app via Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/menu
Environment="PATH=/opt/menu/venv/bin"
EnvironmentFile=-/opt/menu/.env
ExecStart=/opt/menu/venv/bin/gunicorn -b 127.0.0.1:8000 -w 2 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable menu
sudo systemctl start menu
sudo systemctl status menu --no-pager
```

如需以非 `www-data` 用户运行，将 `User`/`Group` 修改为你的部署用户，并确保该用户对 `/opt/menu` 有读写权限。

### 8. 配置 Nginx 反向代理
创建站点配置，将外部 80/443 请求转发到本机 127.0.0.1:8000 的 Gunicorn。
```bash
sudo tee /etc/nginx/sites-available/menu.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    # 如有域名，改成你的域名，例如：example.com
    # server_name example.com www.example.com;

    # 静态资源（直接由 Nginx 提供）
    location /static/ {
        alias /opt/menu/static/;
        access_log off;
        expires 7d;
    }

    # 反向代理到 Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/menu.conf /etc/nginx/sites-enabled/menu.conf
sudo nginx -t
sudo systemctl reload nginx
```

现在在浏览器访问：
- 使用域名（若已解析至服务器）：`http://你的域名/`
- 或使用服务器公网 IP：`http://你的服务器IP/`

后台管理：`/admin`（未登录会 302 跳转登录页）

### 9. 可选：启用 HTTPS（推荐）
使用 Certbot 申请 Let’s Encrypt 证书：
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d 你的域名 -d www.你的域名
# 自动生成 443 配置并申请证书，证书将自动续期
```

### 10. 更新与发布流程
```bash
cd /opt/menu
sudo -u www-data git pull  # 或使用你的部署用户

source venv/bin/activate
pip install -r requirements.txt --upgrade  # 如有依赖更新

# 如有数据库结构变化，执行你的迁移脚本或初始化逻辑
# 例如：python -c "from app import init_db; init_db()" （谨慎使用，避免覆盖数据）

sudo systemctl restart menu
sudo systemctl status menu --no-pager
```

### 11. 故障排查
- 服务未启动：`sudo systemctl status menu` 查看报错；`journalctl -u menu -e` 查看日志
- Nginx 配置错误：`sudo nginx -t` 校验并 `sudo systemctl reload nginx`
- 访问 502：确认 `menu` 服务是否正常监听 127.0.0.1:8000，`ss -tulpn | grep 8000`
- 静态资源 404：确认 `/opt/menu/static/` 路径与权限；`location /static/` 使用的是 `alias`
- 权限问题：运行用户需能读写项目目录与数据库文件（默认 SQLite 在项目内）

### 12. 安全加固建议
- 修改 `.env` 中的 `SECRET_KEY`、管理员账号密码
- 仅开放必要端口（80/443/22）；禁止 root 远程登录；定期打补丁
- 若使用自定义数据库/对象存储，请为凭据设置最小权限并定期轮换

---
当你准备接入 ESA 与 OSS 时，只需在 `.env` 中加入对应变量并在服务器上重启 `menu` 服务即可。此文档不涉及 ESA/OSS 的具体配置。


