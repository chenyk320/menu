# config.py
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///menu.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/images')
    
    # 阿里云OSS配置
    OSS_ACCESS_KEY_ID = os.environ.get('OSS_ACCESS_KEY_ID')
    OSS_ACCESS_KEY_SECRET = os.environ.get('OSS_ACCESS_KEY_SECRET')
    OSS_BUCKET_NAME = os.environ.get('OSS_BUCKET_NAME', 'menu-images')
    OSS_ENDPOINT = os.environ.get('OSS_ENDPOINT', 'oss-cn-hangzhou.aliyuncs.com')
    
    # CDN配置
    CDN_DOMAIN = os.environ.get('CDN_DOMAIN')
    
    # 本地备份配置 - 默认不备份到本地，避免上传到GitHub
    LOCAL_BACKUP = os.environ.get('LOCAL_BACKUP', 'false').lower() == 'true'
    
    # 管理员配置
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'chenyaokang')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '761748142')
    
    @classmethod
    def is_cdn_enabled(cls):
        """检查CDN是否已配置"""
        return bool(cls.OSS_ACCESS_KEY_ID and cls.OSS_ACCESS_KEY_SECRET and cls.CDN_DOMAIN)
