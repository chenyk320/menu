# Cloudflare缓存规则配置
# 在Cloudflare面板中设置以下规则

## 1. 页面规则 (Page Rules)

### 规则1: 图片文件缓存
```
URL模式: your-domain.com/static/images/*
设置:
- 缓存级别: 缓存所有内容
- 边缘缓存TTL: 1个月
- 浏览器缓存TTL: 1年
- 始终在线: 开启
```

### 规则2: 其他静态文件
```
URL模式: your-domain.com/static/*
设置:
- 缓存级别: 缓存所有内容
- 边缘缓存TTL: 1周
- 浏览器缓存TTL: 1个月
```

### 规则3: HTML页面
```
URL模式: your-domain.com/*
设置:
- 缓存级别: 绕过缓存
- 始终在线: 开启
```

## 2. 缓存配置 (Caching)

### 缓存级别
- 标准缓存

### 浏览器缓存TTL
- 4小时

### 边缘缓存TTL
- 1个月

## 3. 压缩设置 (Speed)

### 自动压缩
- 开启所有压缩选项
- 压缩级别: 标准

### Brotli压缩
- 开启

## 4. 图片优化 (Speed > Optimization)

### 图片优化
- 开启
- 自动WebP转换
- 自动JPEG优化

### 移动优化
- 开启
- 自动调整图片尺寸

## 5. 安全设置 (Security)

### SSL/TLS
- 加密模式: 完全（严格）
- 始终使用HTTPS: 开启

### 防火墙规则
```
规则: 只允许Cloudflare IP访问源服务器
表达式: ip.src != cloudflare
动作: 阻止
```

## 6. 网络设置 (Network)

### HTTP/2
- 开启

### HTTP/3 (QUIC)
- 开启

### 0-RTT连接恢复
- 开启

## 7. 监控和分析

### 缓存命中率监控
- 在Analytics中查看缓存命中率
- 目标: 90%以上

### 性能监控
- 查看页面加载时间
- 监控Core Web Vitals

## 8. 自定义错误页面

### 404页面
```
URL: your-domain.com/404
内容: 自定义404页面
```

## 9. 重定向规则

### WWW重定向
```
源URL: www.your-domain.com/*
目标URL: your-domain.com/$1
状态码: 301
```

## 10. 高级设置

### 开发模式
- 仅在需要时开启
- 绕过缓存进行测试

### 清除缓存
- 在需要时手动清除
- 或使用API自动清除
