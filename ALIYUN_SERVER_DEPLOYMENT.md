## 阿里云服务器部署指南（定制版，含从 GitHub 拉取；本文件不上传 GitHub）

本指南基于你的参数定制：服务器以用户 `chenyk` 运行，项目路径 `/opt/menu`，域名 `qingtianmeishi.online`（含 `www`），从 GitHub 通过 SSH 拉取代码，Gunicorn 监听 `127.0.0.1:8000`、`workers=2`，systemd 服务名 `menu`。你会在后续自行配置 ESA 与 OSS，本指南不包含 ESA/OSS 的细节。

注意：本文件仅在本地保存用于部署参考，不需要也不应推送到 GitHub。

### 0) 创建部署用户、赋权与设置密码（含 root 密码）
```bash
sudo adduser chenyk                 # 跟随提示设置 chenyk 的密码
sudo usermod -aG sudo chenyk        # 赋予 sudo 权限
sudo passwd chenyk                  # 如需修改 chenyk 密码（可选）
sudo passwd root                    # 设置 root 密码（可选）
```

### 1) 准备目录与权限
```bash
sudo mkdir -p /opt/menu
sudo chown -R chenyk:chenyk /opt/menu
```

### 2) 从 GitHub 拉取并安装依赖（SSH 方式）
确保服务器 SSH 公钥已添加到 GitHub 账户。
```bash
sudo -iu chenyk bash -c '
cd /opt/menu
git clone git@github.com:chenyk320/menu.git .
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
'
```

### 3) 写入 .env（已含随机生成的 SECRET_KEY 与 ADMIN_PASSWORD）
```bash
sudo -iu chenyk bash -c 'cat > /opt/menu/.env << "EOF"
SECRET_KEY=0f4f6f4e4f3bd2c7f7b25a8c41a6f0d2f5a9b7c3e1d4a6b8c0e2f4a6c8e0d2f4
ADMIN_USERNAME=admin
ADMIN_PASSWORD=U9fKp3ZqS6tV1wXy2JmB
# DATABASE_URL 默认为 sqlite:///menu.db，无需设置
# DATABASE_URL=sqlite:///menu.db

# 预留（后续你自行配置 ESA/OSS）
# OSS_ACCESS_KEY_ID=
# OSS_ACCESS_KEY_SECRET=
# OSS_BUCKET_NAME=
# OSS_ENDPOINT=
# CDN_DOMAIN=
# CLOUDFLARE_DOMAIN=
EOF'
```

### 4) 初始化数据库（首次）
```bash
sudo -iu chenyk bash -c '
cd /opt/menu
source venv/bin/activate
python -c "from app import init_db; init_db()"
'
```

### 5) 配置并启动 systemd 服务（User=chenyk，Gunicorn 127.0.0.1:8000，workers=2）
```bash
sudo tee /etc/systemd/system/menu.service > /dev/null << 'EOF'
[Unit]
Description=Menu Flask app via Gunicorn
After=network.target

[Service]
User=chenyk
Group=chenyk
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

### 6) 配置 Nginx（反代到 Gunicorn，静态资源 alias）
```bash
sudo tee /etc/nginx/sites-available/menu.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name qingtianmeishi.online www.qingtianmeishi.online;

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

### 7) 防火墙（UFW）
阿里云安全组已放行 80/443。若本机 UFW 未启用，按需执行：
```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

### 8) 验证与常用操作
```bash
ss -tulpn | grep 8000                     # 确认 Gunicorn 监听
sudo systemctl status menu --no-pager     # 服务状态
journalctl -u menu -e                     # 服务日志
sudo nginx -t && sudo systemctl reload nginx
# 访问：http://qingtianmeishi.online/
# 后台：http://qingtianmeishi.online/admin
```

### 9) 可选：启用 HTTPS（稍后再做）
如果后续要开启 HTTPS，可使用：
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d qingtianmeishi.online -d www.qingtianmeishi.online
```

### 10) 更新/发布流程
```bash
cd /opt/menu
sudo -u chenyk git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade  # 如有依赖更新
# 如有数据库结构变化，谨慎执行：python -c "from app import init_db; init_db()"
sudo systemctl restart menu
sudo systemctl status menu --no-pager
```

---
后续接入 ESA 与 OSS 时，只需在 `/opt/menu/.env` 中加入相关变量并 `sudo systemctl restart menu` 使其生效。






