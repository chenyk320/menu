#!/bin/bash

# SSL证书配置脚本
# 适用于阿里云ECS部署

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        exit 1
    fi
}

# 安装必要软件
install_dependencies() {
    log_info "安装SSL证书相关软件..."
    
    # 检测系统类型
    if [[ -f /etc/redhat-release ]]; then
        # CentOS/RHEL
        yum install -y openssl certbot
    elif [[ -f /etc/debian_version ]]; then
        # Ubuntu/Debian
        apt update
        apt install -y openssl certbot
    else
        log_error "不支持的操作系统"
        exit 1
    fi
}

# 创建证书目录
create_cert_dirs() {
    log_info "创建证书目录..."
    mkdir -p /etc/ssl/certs
    mkdir -p /etc/ssl/private
    mkdir -p /etc/ssl/csr
    
    # 设置权限
    chmod 755 /etc/ssl/certs
    chmod 700 /etc/ssl/private
    chmod 755 /etc/ssl/csr
}

# 生成自签名证书（开发/测试用）
generate_self_signed_cert() {
    local domain=$1
    local cert_file="/etc/ssl/certs/${domain}.crt"
    local key_file="/etc/ssl/private/${domain}.key"
    
    log_info "生成自签名证书 for ${domain}..."
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$key_file" \
        -out "$cert_file" \
        -subj "/C=CN/ST=Beijing/L=Beijing/O=MenuApp/OU=IT/CN=${domain}"
    
    # 设置权限
    chmod 644 "$cert_file"
    chmod 600 "$key_file"
    
    log_info "自签名证书生成完成"
    log_warn "注意：自签名证书仅用于开发/测试，生产环境请使用正式证书"
}

# 使用Let's Encrypt申请免费证书
generate_letsencrypt_cert() {
    local domain=$1
    local email=$2
    
    log_info "使用Let's Encrypt申请免费SSL证书..."
    
    # 停止nginx（如果正在运行）
    systemctl stop nginx 2>/dev/null || true
    
    # 申请证书
    certbot certonly --standalone \
        --email "$email" \
        --agree-tos \
        --no-eff-email \
        -d "$domain"
    
    # 创建软链接到标准位置
    ln -sf "/etc/letsencrypt/live/${domain}/fullchain.pem" "/etc/ssl/certs/${domain}.crt"
    ln -sf "/etc/letsencrypt/live/${domain}/privkey.pem" "/etc/ssl/private/${domain}.key"
    
    # 设置权限
    chmod 644 "/etc/ssl/certs/${domain}.crt"
    chmod 600 "/etc/ssl/private/${domain}.key"
    
    log_info "Let's Encrypt证书申请完成"
}

# 配置证书自动续期
setup_auto_renewal() {
    log_info "配置证书自动续期..."
    
    # 创建续期脚本
    cat > /etc/cron.daily/ssl-renew << 'EOF'
#!/bin/bash
# SSL证书自动续期脚本

# 续期Let's Encrypt证书
certbot renew --quiet --post-hook "systemctl reload nginx"

# 检查证书有效期
for cert in /etc/ssl/certs/*.crt; do
    if [[ -f "$cert" ]]; then
        expiry=$(openssl x509 -enddate -noout -in "$cert" | cut -d= -f2)
        echo "证书 $cert 有效期至: $expiry"
    fi
done
EOF
    
    chmod +x /etc/cron.daily/ssl-renew
    
    # 添加到crontab
    (crontab -l 2>/dev/null; echo "0 2 * * * /etc/cron.daily/ssl-renew") | crontab -
    
    log_info "证书自动续期配置完成"
}

# 验证证书
verify_cert() {
    local domain=$1
    local cert_file="/etc/ssl/certs/${domain}.crt"
    local key_file="/etc/ssl/private/${domain}.key"
    
    log_info "验证SSL证书..."
    
    if [[ ! -f "$cert_file" ]]; then
        log_error "证书文件不存在: $cert_file"
        return 1
    fi
    
    if [[ ! -f "$key_file" ]]; then
        log_error "私钥文件不存在: $key_file"
        return 1
    fi
    
    # 验证证书和私钥匹配
    cert_md5=$(openssl x509 -noout -modulus -in "$cert_file" | openssl md5)
    key_md5=$(openssl rsa -noout -modulus -in "$key_file" | openssl md5)
    
    if [[ "$cert_md5" == "$key_md5" ]]; then
        log_info "证书和私钥匹配 ✓"
    else
        log_error "证书和私钥不匹配 ✗"
        return 1
    fi
    
    # 显示证书信息
    log_info "证书信息:"
    openssl x509 -in "$cert_file" -text -noout | grep -E "(Subject:|Issuer:|Not Before|Not After)"
    
    return 0
}

# 主函数
main() {
    local domain=""
    local email=""
    local cert_type=""
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--domain)
                domain="$2"
                shift 2
                ;;
            -e|--email)
                email="$2"
                shift 2
                ;;
            -t|--type)
                cert_type="$2"
                shift 2
                ;;
            -h|--help)
                echo "用法: $0 [选项]"
                echo "选项:"
                echo "  -d, --domain DOMAIN    域名"
                echo "  -e, --email EMAIL     邮箱（Let's Encrypt需要）"
                echo "  -t, --type TYPE       证书类型 (self-signed|letsencrypt)"
                echo "  -h, --help           显示帮助"
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
    
    # 检查参数
    if [[ -z "$domain" ]]; then
        log_error "请指定域名 (-d 参数)"
        exit 1
    fi
    
    if [[ -z "$cert_type" ]]; then
        cert_type="self-signed"
    fi
    
    if [[ "$cert_type" == "letsencrypt" && -z "$email" ]]; then
        log_error "Let's Encrypt证书需要邮箱地址 (-e 参数)"
        exit 1
    fi
    
    log_info "开始配置SSL证书..."
    log_info "域名: $domain"
    log_info "证书类型: $cert_type"
    
    check_root
    install_dependencies
    create_cert_dirs
    
    case "$cert_type" in
        "self-signed")
            generate_self_signed_cert "$domain"
            ;;
        "letsencrypt")
            generate_letsencrypt_cert "$domain" "$email"
            setup_auto_renewal
            ;;
        *)
            log_error "不支持的证书类型: $cert_type"
            exit 1
            ;;
    esac
    
    verify_cert "$domain"
    
    log_info "SSL证书配置完成！"
    log_info "证书文件: /etc/ssl/certs/${domain}.crt"
    log_info "私钥文件: /etc/ssl/private/${domain}.key"
}

# 运行主函数
main "$@"
