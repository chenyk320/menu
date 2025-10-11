# cdn_service.py
import os
import uuid
from datetime import datetime
from PIL import Image
import oss2
from config import Config

class CDNService:
    """CDN服务类"""
    
    def __init__(self):
        self.auth = None
        self.bucket = None
        self.cdn_domain = Config.CDN_DOMAIN
        
        if Config.is_cdn_enabled():
            self.auth = oss2.Auth(Config.OSS_ACCESS_KEY_ID, Config.OSS_ACCESS_KEY_SECRET)
            self.bucket = oss2.Bucket(self.auth, Config.OSS_ENDPOINT, Config.OSS_BUCKET_NAME)
    
    def is_enabled(self):
        """检查CDN服务是否可用"""
        return self.bucket is not None
    
    def upload_image(self, file_path, filename=None):
        """
        上传图片到CDN
        :param file_path: 本地图片路径
        :param filename: 文件名（可选）
        :return: CDN URL或None
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
            
            # 上传到OSS
            with open(file_path, 'rb') as file:
                result = self.bucket.put_object(filename, file)
            
            if result.status == 200:
                # 返回CDN URL
                cdn_url = f"{self.cdn_domain}/{filename}"
                print(f"✅ 图片上传成功: {cdn_url}")
                return cdn_url
            else:
                print(f"❌ 图片上传失败: {result}")
                return None
                
        except Exception as e:
            print(f"❌ CDN上传异常: {e}")
            return None
    
    def delete_image(self, filename):
        """
        删除CDN上的图片
        :param filename: 文件名
        :return: 是否成功
        """
        if not self.is_enabled():
            return False
        
        try:
            result = self.bucket.delete_object(filename)
            if result.status == 204:
                print(f"✅ CDN图片删除成功: {filename}")
                return True
            else:
                print(f"❌ CDN图片删除失败: {result}")
                return False
        except Exception as e:
            print(f"❌ CDN删除异常: {e}")
            return False
    
    def optimize_and_upload(self, file_path, filename=None, max_width=800, quality=85):
        """
        优化图片并上传到CDN
        :param file_path: 本地图片路径
        :param filename: 文件名
        :param max_width: 最大宽度
        :param quality: JPEG质量
        :return: CDN URL或None
        """
        if not self.is_enabled():
            return None
        
        try:
            # 优化图片
            optimized_path = self._optimize_image(file_path, max_width, quality)
            
            # 上传到CDN
            cdn_url = self.upload_image(optimized_path, filename)
            
            # 删除临时优化文件
            if optimized_path != file_path and os.path.exists(optimized_path):
                os.remove(optimized_path)
            
            return cdn_url
            
        except Exception as e:
            print(f"❌ 优化上传异常: {e}")
            return None
    
    def _optimize_image(self, file_path, max_width=800, quality=85):
        """
        优化图片
        :param file_path: 图片路径
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
                optimized_path = file_path.replace('.', '_optimized.')
                img.save(optimized_path, 'JPEG', quality=quality, optimize=True)
                
                return optimized_path
                
        except Exception as e:
            print(f"❌ 图片优化失败: {e}")
            return file_path
    
    def get_image_url(self, filename):
        """
        获取图片的CDN URL
        :param filename: 文件名
        :return: CDN URL
        """
        if self.is_enabled():
            return f"{self.cdn_domain}/{filename}"
        else:
            return f"/static/images/{filename}"
    
    def batch_upload(self, local_dir, remote_prefix=''):
        """
        批量上传本地图片到CDN
        :param local_dir: 本地目录
        :param remote_prefix: 远程前缀
        :return: 上传结果
        """
        if not self.is_enabled():
            return {'success': 0, 'failed': 0, 'results': []}
        
        results = []
        success_count = 0
        failed_count = 0
        
        for filename in os.listdir(local_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                local_path = os.path.join(local_dir, filename)
                remote_filename = f"{remote_prefix}{filename}" if remote_prefix else filename
                
                cdn_url = self.upload_image(local_path, remote_filename)
                
                result = {
                    'filename': filename,
                    'cdn_url': cdn_url,
                    'success': cdn_url is not None
                }
                results.append(result)
                
                if cdn_url:
                    success_count += 1
                else:
                    failed_count += 1
        
        return {
            'success': success_count,
            'failed': failed_count,
            'results': results
        }

# 创建全局CDN服务实例
cdn_service = CDNService()
