# cloudflare_config.py
# Cloudflare CDN配置方案

import os
import uuid
from PIL import Image
from config import Config

class CloudflareCDNService:
    """Cloudflare CDN服务类 - 本地存储 + Cloudflare加速"""
    
    def __init__(self):
        self.local_storage_path = Config.UPLOAD_FOLDER
        self.cloudflare_domain = Config.CLOUDFLARE_DOMAIN  # 您的域名
        self.enabled = bool(self.cloudflare_domain)
    
    def is_enabled(self):
        """检查Cloudflare CDN是否可用"""
        return self.enabled
    
    def upload_image(self, file_path, filename=None):
        """
        保存图片到本地，返回Cloudflare加速的URL
        :param file_path: 本地图片路径
        :param filename: 文件名（可选）
        :return: Cloudflare CDN URL或None
        """
        if not self.is_enabled():
            return None
        
        try:
            # 生成唯一文件名
            if not filename:
                filename = f"{uuid.uuid4()}.jpg"
            
            # 确保文件名有扩展名
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filename += '.jpg'
            
            # 优化图片
            optimized_path = self._optimize_image(file_path, filename)
            
            if optimized_path:
                # 返回Cloudflare CDN URL
                cdn_url = f"{self.cloudflare_domain}/static/images/{filename}"
                print(f"✅ 图片已保存到本地，Cloudflare CDN URL: {cdn_url}")
                return cdn_url
            else:
                return None
                
        except Exception as e:
            print(f"❌ Cloudflare CDN处理异常: {e}")
            return None
    
    def _optimize_image(self, file_path, filename, max_width=800, quality=85):
        """
        优化图片并保存到本地
        :param file_path: 原图片路径
        :param filename: 目标文件名
        :param max_width: 最大宽度
        :param quality: JPEG质量
        :return: 优化后的图片路径
        """
        try:
            with Image.open(file_path) as img:
                # 转换为RGB模式
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 调整尺寸
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                # 保存优化后的图片
                output_path = os.path.join(self.local_storage_path, filename)
                img.save(output_path, 'JPEG', quality=quality, optimize=True)
                
                return output_path
                
        except Exception as e:
            print(f"❌ 图片优化失败: {e}")
            return None
    
    def delete_image(self, filename):
        """
        删除本地图片
        :param filename: 文件名
        :return: 是否成功
        """
        try:
            file_path = os.path.join(self.local_storage_path, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"✅ 本地图片删除成功: {filename}")
                return True
            else:
                print(f"⚠️ 图片文件不存在: {filename}")
                return False
        except Exception as e:
            print(f"❌ 删除图片异常: {e}")
            return False
    
    def get_image_url(self, filename):
        """
        获取图片的Cloudflare CDN URL
        :param filename: 文件名
        :return: CDN URL
        """
        if self.is_enabled():
            return f"{self.cloudflare_domain}/static/images/{filename}"
        else:
            return f"/static/images/{filename}"

# 创建全局Cloudflare CDN服务实例
cloudflare_cdn_service = CloudflareCDNService()
