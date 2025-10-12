# 阿里云CDN配置优化指南

## 概述

本指南详细说明如何配置阿里云CDN以优化您的菜单应用性能。

## 1. CDN基础配置

### 1.1 开通CDN服务

1. 登录阿里云控制台
2. 进入CDN服务页面
3. 开通CDN服务（按流量计费）

### 1.2 添加加速域名

#### 配置步骤：
1. 进入CDN控制台
2. 点击"添加域名"
3. 填写配置信息：

```
加速域名：cdn.yourdomain.com
业务类型：图片小文件
源站信息：源站域名
源站地址：yourdomain.com
端口：443
协议：HTTPS
```

#### 高级配置：
```
加速区域：仅中国内地
资源分组：默认分组
服务协议：HTTP/HTTPS
HTTP端口：80
HTTPS端口：443
```

## 2. 缓存配置优化

### 2.1 缓存规则配置

#### 文件类型缓存策略：

| 文件类型 | 缓存时间 | 缓存规则 |
|---------|---------|---------|
| 图片文件 | 30天 | `*.jpg, *.jpeg, *.png, *.gif, *.webp, *.svg` |
| CSS文件 | 7天 | `*.css` |
| JS文件 | 7天 | `*.js` |
| HTML文件 | 1小时 | `*.html` |
| 字体文件 | 30天 | `*.woff, *.woff2, *.ttf, *.eot` |

#### 路径缓存策略：

```
/static/images/*    缓存30天
/static/css/*       缓存7天
/static/js/*        缓存7天
/admin/*            不缓存
/api/*              不缓存
/                   缓存1小时
```

### 2.2 缓存键配置

#### 忽略参数：
```
utm_source, utm_medium, utm_campaign, v, version, t, timestamp
```

#### 保留参数：
```
无特殊要求
```

## 3. 回源配置

### 3.1 回源协议配置

```
回源协议：HTTPS
回源端口：443
回源HOST：yourdomain.com
```

### 3.2 回源策略

```
主源站：yourdomain.com:443
备源站：无
回源方式：域名回源
回源SNI：开启
```

### 3.3 回源请求头

```
Host: yourdomain.com
X-Forwarded-For: $remote_addr
X-Real-IP: $remote_addr
X-Forwarded-Proto: $scheme
```

## 4. 安全配置

### 4.1 访问控制

#### IP访问限制：
```
允许访问：0.0.0.0/0
拒绝访问：无
```

#### Referer防盗链：
```
允许空Referer：是
允许Referer：yourdomain.com, *.yourdomain.com
拒绝Referer：无
```

### 4.2 HTTPS配置

```
HTTPS：开启
HTTP/2：开启
TLS版本：TLSv1.2, TLSv1.3
加密套件：推荐配置
```

## 5. 性能优化配置

### 5.1 压缩配置

#### Gzip压缩：
```
开启状态：开启
压缩类型：text/html, text/css, text/javascript, application/javascript, application/json, image/svg+xml
压缩级别：6
```

#### Brotli压缩：
```
开启状态：开启（如果支持）
压缩级别：6
```

### 5.2 智能压缩

```
智能压缩：开启
压缩阈值：1024字节
压缩比例：70%
```

### 5.3 图片优化

#### 图片处理：
```
WebP自适应：开启
图片质量：85%
图片格式：WebP, AVIF
```

#### 图片缩放：
```
开启状态：开启
最大宽度：1920px
最大高度：1080px
```

## 6. 高级功能配置

### 6.1 边缘计算

#### EdgeScript配置：
```javascript
// 图片优化脚本
if (request.uri.match(/\.(jpg|jpeg|png|gif|webp)$/i)) {
    // 添加WebP支持检测
    if (request.headers['accept'].includes('image/webp')) {
        request.uri = request.uri.replace(/\.(jpg|jpeg|png|gif)$/i, '.webp');
    }
    
    // 添加缓存控制
    response.headers['Cache-Control'] = 'public, max-age=2592000';
    response.headers['Expires'] = 'Thu, 31 Dec 2037 23:55:55 GMT';
}
```

### 6.2 实时日志

#### 日志配置：
```
日志类型：访问日志
日志格式：JSON
日志字段：时间、IP、URL、状态码、响应时间、User-Agent
存储位置：OSS
存储周期：30天
```

## 7. 监控和告警

### 7.1 监控指标

#### 关键指标：
- 命中率：>90%
- 响应时间：<100ms
- 错误率：<1%
- 带宽使用：监控峰值

#### 监控配置：
```
监控频率：1分钟
告警阈值：
  - 命中率 < 80%
  - 响应时间 > 500ms
  - 错误率 > 5%
  - 带宽使用 > 80%
```

### 7.2 告警配置

#### 告警规则：
```
告警方式：短信 + 邮件
告警频率：5分钟
告警级别：严重、警告、提醒
```

## 8. 成本优化

### 8.1 流量优化

#### 缓存优化：
```
静态资源缓存：30天
动态内容缓存：不缓存
图片压缩：开启
智能压缩：开启
```

#### 回源优化：
```
回源请求：最小化
回源带宽：监控使用
回源时间：优化配置
```

### 8.2 计费优化

#### 计费方式：
```
按流量计费：推荐
按峰值带宽计费：高流量场景
按请求数计费：API场景
```

## 9. 故障排除

### 9.1 常见问题

#### 缓存不生效：
1. 检查缓存规则配置
2. 检查HTTP头设置
3. 检查文件类型匹配

#### 回源失败：
1. 检查源站配置
2. 检查网络连通性
3. 检查SSL证书

#### 性能问题：
1. 检查缓存命中率
2. 检查回源比例
3. 检查压缩配置

### 9.2 调试工具

#### 缓存调试：
```bash
# 检查缓存状态
curl -I https://cdn.yourdomain.com/static/images/logo.png

# 检查回源情况
curl -H "Cache-Control: no-cache" https://cdn.yourdomain.com/
```

#### 性能测试：
```bash
# 使用ab测试
ab -n 1000 -c 10 https://cdn.yourdomain.com/

# 使用curl测试
curl -w "@curl-format.txt" -o /dev/null -s https://cdn.yourdomain.com/
```

## 10. 最佳实践

### 10.1 配置建议

1. **缓存策略**：
   - 静态资源长期缓存
   - 动态内容不缓存
   - 合理设置缓存时间

2. **安全配置**：
   - 启用HTTPS
   - 配置防盗链
   - 设置访问控制

3. **性能优化**：
   - 启用压缩
   - 优化图片
   - 使用HTTP/2

### 10.2 监控建议

1. **定期检查**：
   - 缓存命中率
   - 响应时间
   - 错误率

2. **性能调优**：
   - 根据监控数据调整配置
   - 优化缓存规则
   - 调整压缩设置

## 11. 配置示例

### 11.1 完整配置示例

```json
{
  "domain": "cdn.yourdomain.com",
  "origin": {
    "type": "domain",
    "address": "yourdomain.com",
    "port": 443,
    "protocol": "https"
  },
  "cache": {
    "rules": [
      {
        "path": "/static/images/*",
        "ttl": 2592000,
        "cache_control": "public, max-age=2592000"
      },
      {
        "path": "/static/css/*",
        "ttl": 604800,
        "cache_control": "public, max-age=604800"
      },
      {
        "path": "/admin/*",
        "ttl": 0,
        "cache_control": "no-cache, no-store, must-revalidate"
      }
    ]
  },
  "compression": {
    "gzip": true,
    "brotli": true,
    "types": ["text/html", "text/css", "text/javascript", "application/javascript"]
  },
  "security": {
    "https": true,
    "http2": true,
    "tls_versions": ["TLSv1.2", "TLSv1.3"]
  }
}
```

### 11.2 监控配置示例

```yaml
monitoring:
  metrics:
    - name: "cache_hit_ratio"
      threshold: 0.9
      alert: "warning"
    - name: "response_time"
      threshold: 100
      unit: "ms"
      alert: "critical"
    - name: "error_rate"
      threshold: 0.01
      alert: "critical"
  
  alerts:
    - name: "low_cache_hit_ratio"
      condition: "cache_hit_ratio < 0.8"
      action: "send_notification"
    - name: "high_response_time"
      condition: "response_time > 500"
      action: "send_notification"
```

## 总结

通过以上配置，您的阿里云CDN将能够：

- ✅ 提供快速的静态资源访问
- ✅ 减少源站压力
- ✅ 优化用户体验
- ✅ 降低带宽成本
- ✅ 提供安全的内容分发

建议定期监控CDN性能指标，根据实际使用情况调整配置参数。
