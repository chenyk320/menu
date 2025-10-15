#!/bin/bash

# 阿里云部署脚本
# 适用于阿里云ECS + CDN部署方案

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
APP_NAME="menu"
APP_DIR="/var/www/menu"
APP_USER="www-data"
APP_GROUP="www-data"
# 以下参数根据你的环境填写
DOMAIN="qingtianmeishi.online"
EMAIL="chenyk320@gmail.com"
SSL_TYPE="letsencrypt"  # letsencrypt | self-signed
GIT_REPO="https://github.com/chenyk320/menu"
GIT_BRANCH="main"
PYTHON_BIN="python3"
# Gunicorn 并发与绑定
GUNICORN_WORKERS="5"
GUNICORN_THREADS="1"
GUNICORN_TIMEOUT="60"
GUNICORN_BIND="127.0.0.1:8000"
# OSS/ESA（仅写入 .env，不进 Git）
OSS_REGION_ID="eu-central-1"
OSS_BUCKET_NAME="qingtianmeishi-123"
OSS_ENDPOINT="oss-eu-central-1.aliyuncs.com"
CDN_DOMAIN="https://qingtianmeishi.online"
UPLOAD_PREFIX="images/"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        exit 1
    fi
}

# 检测操作系统
detect_os() {
    if [[ -f /etc/redhat-release ]]; then
        OS="centos"
        PKG_MANAGER="yum"
    elif [[ -f /etc/debian_version ]]; then
        OS="ubuntu"
        PKG_MANAGER="apt"
    else
        log_error "不支持的操作系统"
        exit 1
    fi
    log_info "检测到操作系统: $OS"
}

# 更新系统
update_system() {
    log_step "更新系统包..."
    
    if [[ "$OS" == "centos" ]]; then
        yum update -y
        yum install -y epel-release
    elif [[ "$OS" == "ubuntu" ]]; then
        apt update
        apt upgrade -y
    fi
    
    log_info "系统更新完成"
}

# 安装基础软件
install_dependencies() {
    log_step "安装基础软件..."
    
    if [[ "$OS" == "centos" ]]; then
        yum install -y python3 python3-pip python3-venv nginx git curl wget unzip
    elif [[ "$OS" == "ubuntu" ]]; then
        apt install -y python3 python3-pip python3-venv nginx git curl wget unzip
    fi
    
    log_info "基础软件安装完成"
}

# 创建应用用户
create_app_user() {
    log_step "创建应用用户..."
    
    if ! id "$APP_USER" &>/dev/null; then
        useradd -r -s /bin/false -d "$APP_DIR" "$APP_USER"
        log_info "创建用户 $APP_USER"
    else
        log_info "用户 $APP_USER 已存在"
    fi
}

# 创建应用目录
create_app_directory() {
    log_step "创建应用目录..."
    
    mkdir -p "$APP_DIR"
    mkdir -p "$APP_DIR/logs"
    mkdir -p "$APP_DIR/instance"
    mkdir -p "$APP_DIR/static/images"
    
    # 设置权限
    chown -R "$APP_USER:$APP_GROUP" "$APP_DIR"
    chmod -R 755 "$APP_DIR"
    
    log_info "应用目录创建完成"
}

# 部署应用代码
deploy_application() {
    log_step "部署应用代码..."
    
    if [[ -d "$APP_DIR/.git" ]]; then
        log_info "检测到已有仓库，拉取最新代码 ($GIT_BRANCH)..."
        cd "$APP_DIR"
        git fetch --all --prune
        git checkout "$GIT_BRANCH"
        git pull --ff-only origin "$GIT_BRANCH"
    else
        log_info "克隆仓库: $GIT_REPO ($GIT_BRANCH)"
        rm -rf "$APP_DIR"
        mkdir -p "$APP_DIR"
        git clone --branch "$GIT_BRANCH" --depth 1 "$GIT_REPO" "$APP_DIR"
    fi
    
    # 设置权限
    chown -R "$APP_USER:$APP_GROUP" "$APP_DIR"
    chmod -R 755 "$APP_DIR"
    
    log_info "应用代码部署完成"
}

# 创建虚拟环境
create_virtualenv() {
    log_step "创建Python虚拟环境..."
    
    cd "$APP_DIR"
    
    # 始终在服务器上重建 venv
    rm -rf venv
    $PYTHON_BIN -m venv venv
    
    # 激活虚拟环境并安装依赖
    source venv/bin/activate
    pip install --upgrade pip wheel setuptools
    pip install -r requirements.txt
    pip install gunicorn
    
    # 设置权限
    chown -R "$APP_USER:$APP_GROUP" "$APP_DIR/venv"
    
    log_info "虚拟环境创建完成"
}

# 配置环境变量
configure_environment() {
    log_step "配置环境变量 (.env)..."
    
    if [[ ! -f "$APP_DIR/.env" ]]; then
        SECRET_KEY_GENERATED=$(openssl rand -hex 32)
        cat > "$APP_DIR/.env" << EOF
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY_GENERATED
DATABASE_URL=sqlite:///instance/menu.db

# OSS
OSS_ACCESS_KEY_ID=
OSS_ACCESS_KEY_SECRET=
OSS_BUCKET_NAME=$OSS_BUCKET_NAME
OSS_ENDPOINT=$OSS_ENDPOINT

# CDN/ESA
CDN_DOMAIN=$CDN_DOMAIN
UPLOAD_FOLDER=static/images
LOCAL_BACKUP=true
EOF
        log_warn "已生成 .env（未包含敏感 AccessKey），请部署后在服务器上编辑填入 OSS_ACCESS_KEY_ID/OSS_ACCESS_KEY_SECRET。"
    fi
    
    # 设置权限
    chown "$APP_USER:$APP_GROUP" "$APP_DIR/.env"
    chmod 600 "$APP_DIR/.env"
    
    log_info ".env 就绪"
}

# 初始化数据库
init_database() {
    log_step "初始化数据库（按需执行）..."
    
    cd "$APP_DIR"
    source venv/bin/activate
    
    # 初始化数据库（失败可忽略，后续可手动执行）
    python -c "from app import init_db; init_db()" || log_warn "init_db 调用失败"
    
    # 设置权限
    chown -R "$APP_USER:$APP_GROUP" "$APP_DIR/instance"
    chmod -R 755 "$APP_DIR/instance"
    
    log_info "数据库初始化步骤完成"
}

# 配置Nginx
configure_nginx() {
    log_step "配置Nginx..."
    
    # 备份原配置
    if [[ -f /etc/nginx/nginx.conf ]]; then
        cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
    fi
    
    # 创建站点配置
    cat > "/etc/nginx/sites-available/$APP_NAME" << EOF
# Nginx配置文件 - 阿里云部署
# 适用于阿里云ECS + CDN部署方案

# 上游服务器配置
upstream menu_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

# HTTP（不强制跳转 HTTPS）
server {
    listen 80;
    server_name $DOMAIN;
    
    # 健康检查端点
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
    
    # 主应用代理
    location / {
        proxy_pass http://menu_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }
}

# HTTPS主配置
server {
    listen 443 ssl http2;
    server_name $DOMAIN;
    
    # SSL证书配置（Let’s Encrypt）
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 安全头配置
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # 日志配置
    access_log /var/log/nginx/menu_access.log;
    error_log /var/log/nginx/menu_error.log;
    
    # 客户端配置
    client_max_body_size 10M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # 静态文件处理 - 图片文件
    location ~* \\.(jpg|jpeg|png|gif|webp|svg|ico)$ {
        alias $APP_DIR/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        add_header Vary "Accept-Encoding";
        
        # 图片优化
        try_files \$uri =404;
        
        # 启用gzip压缩（对SVG有效）
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types image/svg+xml;
    }
    
    # 静态文件处理 - CSS/JS文件
    location ~* \\.(css|js)$ {
        alias $APP_DIR/static/;
        expires 7d;
        add_header Cache-Control "public, immutable";
        add_header Vary "Accept-Encoding";
        
        # 启用gzip压缩
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_comp_level 6;
        gzip_types text/css application/javascript text/javascript;
    }
    
    # 静态文件处理 - 其他静态资源
    location /static/ {
        alias $APP_DIR/static/;
        expires 1d;
        add_header Cache-Control "public";
        add_header Vary "Accept-Encoding";
        
        # 启用gzip压缩
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_comp_level 6;
        gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    }
    
    # 管理后台特殊处理
    location /admin {
        proxy_pass http://menu_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓存控制
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }
    
    # API接口处理
    location /api/ {
        proxy_pass http://menu_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓存控制
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }
    
    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
    
    # 主应用代理
    location / {
        proxy_pass http://menu_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓存控制
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }
    
    # 错误页面
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
    
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
EOF
    
    # 启用站点
    ln -sf "/etc/nginx/sites-available/$APP_NAME" "/etc/nginx/sites-enabled/"
    
    # 测试配置
    nginx -t
    
    log_info "Nginx配置完成"
}

# 配置SSL证书
configure_ssl() {
    log_step "配置SSL证书..."
    
    if [[ "$SSL_TYPE" == "letsencrypt" ]]; then
        # 使用Let's Encrypt
        if [[ -z "$EMAIL" ]]; then
            log_error "Let's Encrypt证书需要邮箱地址"
            exit 1
        fi
        
        # 安装certbot
        if [[ "$OS" == "centos" ]]; then
            yum install -y certbot python3-certbot-nginx
        elif [[ "$OS" == "ubuntu" ]]; then
            apt install -y certbot python3-certbot-nginx
        fi
        
        # 申请证书（不强制跳转）
        certbot --nginx -d "$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive --no-redirect
        
    else
        # 生成自签名证书
        mkdir -p /etc/ssl/certs /etc/ssl/private
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "/etc/ssl/private/$DOMAIN.key" \
            -out "/etc/ssl/certs/$DOMAIN.crt" \
            -subj "/C=CN/ST=Beijing/L=Beijing/O=MenuApp/OU=IT/CN=$DOMAIN"
        
        chmod 644 "/etc/ssl/certs/$DOMAIN.crt"
        chmod 600 "/etc/ssl/private/$DOMAIN.key"
        
        log_warn "已生成自签名证书，生产环境请使用正式证书"
    fi
    
    log_info "SSL证书配置完成"
}

# 配置systemd服务
configure_systemd() {
    log_step "配置systemd服务..."
    
    cat > "/etc/systemd/system/$APP_NAME.service" << EOF
[Unit]
Description=Menu Flask Application
Documentation=$GIT_REPO
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=PYTHONPATH=$APP_DIR
Environment=FLASK_ENV=production
Environment=FLASK_APP=app.py

# 启动命令（Gunicorn）
ExecStart=$APP_DIR/venv/bin/gunicorn --workers $GUNICORN_WORKERS --threads $GUNICORN_THREADS --timeout $GUNICORN_TIMEOUT --bind 127.0.0.1:8000 app:app

# 重启策略
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3

# 资源限制
LimitNOFILE=65536
LimitNPROC=4096

# 安全配置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR
ReadWritePaths=$APP_DIR/instance
ReadWritePaths=$APP_DIR/static/images

# 日志配置
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$APP_NAME

# 健康检查
ExecStartPost=/bin/sleep 5
ExecStartPost=/bin/bash -c 'curl -f http://127.0.0.1:8000/health || exit 1'

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载systemd
    systemctl daemon-reload
    
    log_info "systemd服务配置完成"
}

# 配置防火墙
configure_firewall() {
    log_step "配置防火墙..."
    
    if [[ "$OS" == "centos" ]]; then
        # CentOS/RHEL
        if systemctl is-active --quiet firewalld; then
            firewall-cmd --permanent --add-service=http
            firewall-cmd --permanent --add-service=https
            firewall-cmd --reload
        fi
    elif [[ "$OS" == "ubuntu" ]]; then
        # 根据你的选择，不启用 ufw，仅提示
        log_info "跳过 UFW 配置（请在安全组放行 22/80/443）"
    fi
    
    log_info "防火墙配置完成"
}

# 启动服务
start_services() {
    log_step "启动服务..."
    
    # 启动应用服务
    systemctl start "$APP_NAME"
    systemctl enable "$APP_NAME"
    
    # 启动Nginx
    systemctl start nginx
    systemctl enable nginx
    
    # 检查服务状态
    systemctl status "$APP_NAME" --no-pager
    systemctl status nginx --no-pager
    
    log_info "服务启动完成"
}

# 配置日志轮转
configure_logrotate() {
    log_step "配置日志轮转..."
    
    cat > "/etc/logrotate.d/$APP_NAME" << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $APP_USER $APP_GROUP
    postrotate
        systemctl reload $APP_NAME
    endscript
}
EOF
    
    log_info "日志轮转配置完成"
}

# 配置监控
configure_monitoring() {
    log_step "配置监控..."
    
    # 创建监控脚本
    cat > "/usr/local/bin/monitor-$APP_NAME.sh" << EOF
#!/bin/bash
# 监控脚本

# 检查服务状态
if ! systemctl is-active --quiet $APP_NAME; then
    echo "\$(date): $APP_NAME service is down, restarting..." >> /var/log/$APP_NAME-monitor.log
    systemctl restart $APP_NAME
fi

# 检查Nginx状态
if ! systemctl is-active --quiet nginx; then
    echo "\$(date): Nginx service is down, restarting..." >> /var/log/$APP_NAME-monitor.log
    systemctl restart nginx
fi

# 检查磁盘空间
DISK_USAGE=\$(df / | awk 'NR==2 {print \$5}' | sed 's/%//')
if [ \$DISK_USAGE -gt 80 ]; then
    echo "\$(date): Disk usage is \${DISK_USAGE}%" >> /var/log/$APP_NAME-monitor.log
fi
EOF
    
    chmod +x "/usr/local/bin/monitor-$APP_NAME.sh"
    
    # 添加到crontab
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/monitor-$APP_NAME.sh") | crontab -
    
    log_info "监控配置完成"
}

# 显示部署信息
show_deployment_info() {
    log_step "部署完成！"
    
    echo ""
    echo "=========================================="
    echo "部署信息："
    echo "=========================================="
    echo "应用目录: $APP_DIR"
    echo "应用用户: $APP_USER"
    echo "域名: $DOMAIN"
    echo "SSL类型: $SSL_TYPE"
    echo ""
    echo "服务状态："
    echo "应用服务: $(systemctl is-active $APP_NAME)"
    echo "Nginx服务: $(systemctl is-active nginx)"
    echo ""
    echo "访问地址："
    echo "HTTP: http://$DOMAIN"
    echo "HTTPS: https://$DOMAIN"
    echo "管理后台: https://$DOMAIN/admin"
    echo ""
    echo "日志文件："
    echo "应用日志: journalctl -u $APP_NAME -f"
    echo "Nginx日志: /var/log/nginx/menu_*.log"
    echo ""
    echo "常用命令："
    echo "重启应用: systemctl restart $APP_NAME"
    echo "重启Nginx: systemctl restart nginx"
    echo "查看状态: systemctl status $APP_NAME"
    echo "=========================================="
}

# 主函数
main() {
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--domain)
                DOMAIN="$2"
                shift 2
                ;;
            -e|--email)
                EMAIL="$2"
                shift 2
                ;;
            -s|--ssl-type)
                SSL_TYPE="$2"
                shift 2
                ;;
            -h|--help)
                echo "用法: $0 [选项]"
                echo "选项:"
                echo "  -d, --domain DOMAIN    域名 (必需)"
                echo "  -e, --email EMAIL     邮箱（Let's Encrypt需要）"
                echo "  -s, --ssl-type TYPE    SSL类型 (self-signed|letsencrypt)"
                echo "  -h, --help           显示帮助"
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
    
    # 检查必需参数
    if [[ -z "$DOMAIN" ]]; then
        log_error "请指定域名 (-d 参数)"
        exit 1
    fi
    
    if [[ "$SSL_TYPE" == "letsencrypt" && -z "$EMAIL" ]]; then
        log_error "Let's Encrypt证书需要邮箱地址 (-e 参数)"
        exit 1
    fi
    
    log_info "开始部署 $APP_NAME 应用..."
    log_info "域名: $DOMAIN"
    log_info "SSL类型: $SSL_TYPE"
    
    check_root
    detect_os
    update_system
    install_dependencies
    create_app_user
    create_app_directory
    deploy_application
    create_virtualenv
    configure_environment
    init_database
    configure_nginx
    configure_ssl
    configure_systemd
    configure_firewall
    start_services
    configure_logrotate
    configure_monitoring
    show_deployment_info
}

# 运行主函数
main "$@"
