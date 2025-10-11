# CDN配置指南

## 阿里云OSS + CDN 配置步骤

### 1. 注册阿里云账号
- 访问：https://www.aliyun.com/
- 注册账号并实名认证
- 开通OSS和CDN服务

### 2. 创建OSS存储桶
1. 登录阿里云控制台
2. 进入OSS服务
3. 创建存储桶（Bucket）
   - 名称：menu-images
   - 地域：选择离用户最近的地域
   - 存储类型：标准存储
   - 读写权限：公共读

### 3. 配置CDN加速
1. 进入CDN控制台
2. 添加加速域名
3. 源站类型：OSS域名
4. 源站地址：你的OSS域名
5. 加速区域：全球

### 4. 获取访问密钥
1. 进入RAM控制台
2. 创建用户
3. 生成AccessKey
4. 授权OSS和CDN权限

## 配置信息示例

```python
# config.py
import os

class Config:
    # 阿里云OSS配置
    OSS_ACCESS_KEY_ID = os.environ.get('OSS_ACCESS_KEY_ID', 'your_access_key_id')
    OSS_ACCESS_KEY_SECRET = os.environ.get('OSS_ACCESS_KEY_SECRET', 'your_access_key_secret')
    OSS_BUCKET_NAME = os.environ.get('OSS_BUCKET_NAME', 'menu-images')
    OSS_ENDPOINT = os.environ.get('OSS_ENDPOINT', 'oss-cn-hangzhou.aliyuncs.com')
    
    # CDN配置
    CDN_DOMAIN = os.environ.get('CDN_DOMAIN', 'https://your-cdn-domain.com')
    
    # 本地备份配置
    LOCAL_BACKUP = os.environ.get('LOCAL_BACKUP', 'true').lower() == 'true'
```

## 环境变量设置

创建 `.env` 文件：
```bash
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET_NAME=menu-images
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
CDN_DOMAIN=https://your-cdn-domain.com
LOCAL_BACKUP=true
```
