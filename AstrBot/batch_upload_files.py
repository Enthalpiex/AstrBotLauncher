#!/usr/bin/env python3
"""
批量上传文件到AstrBot知识库的外挂脚本
支持 txt、pdf、word、excel 等多种格式
自动记录已上传文件，避免重复上传
"""

import os
import json
import asyncio
import aiofiles
import aiohttp
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib
from tqdm import tqdm
import argparse
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_upload.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BatchFileUploader:
    def __init__(self, 
                 astrbot_url: str = "http://localhost:6185", 
                 username: str = "Germania", 
                 password: str = None,
                 upload_record_file: str = "upload_record.json"):
        self.astrbot_url = astrbot_url.rstrip('/')
        self.username = username
        self.password = password or "a5a35ac207741709fda357b1d1e8ad31"
        self.session = None
        self.token = None
        self.upload_record_file = upload_record_file
        self.uploaded_files = self.load_upload_record()
        
    def load_upload_record(self) -> Dict[str, Dict]:
        """加载已上传文件记录"""
        try:
            if os.path.exists(self.upload_record_file):
                with open(self.upload_record_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"加载上传记录失败: {e}")
        return {}
    
    def save_upload_record(self):
        """保存上传记录"""
        try:
            with open(self.upload_record_file, 'w', encoding='utf-8') as f:
                json.dump(self.uploaded_files, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存上传记录失败: {e}")
    
    def get_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"计算文件哈希失败 {file_path}: {e}")
            return ""
    
    def is_file_uploaded(self, file_path: str) -> bool:
        """检查文件是否已上传"""
        file_hash = self.get_file_hash(file_path)
        if not file_hash:
            return False
        
        file_name = os.path.basename(file_path)
        if file_name in self.uploaded_files:
            record = self.uploaded_files[file_name]
            return record.get('hash') == file_hash
        return False
    
    def mark_file_uploaded(self, file_path: str, collection_name: str):
        """标记文件为已上传"""
        file_name = os.path.basename(file_path)
        file_hash = self.get_file_hash(file_path)
        file_size = os.path.getsize(file_path)
        
        self.uploaded_files[file_name] = {
            'hash': file_hash,
            'size': file_size,
            'collection_name': collection_name,
            'upload_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'file_path': file_path
        }
        self.save_upload_record()
    
    async def login(self) -> bool:
        """登录AstrBot管理面板"""
        self.session = aiohttp.ClientSession()
        login_data = {
            "username": self.username,
            "password": self.password
        }
        
        try:
            async with self.session.post(f"{self.astrbot_url}/api/auth/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "ok":
                        self.token = result["data"]["token"]
                        logger.info("✅ 登录成功")
                        return True
                    else:
                        logger.error(f"❌ 登录失败: {result.get('message')}")
                        return False
                else:
                    logger.error(f"❌ 登录请求失败: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ 登录异常: {e}")
            return False
    
    async def get_knowledge_bases(self) -> List[Dict]:
        """获取知识库列表"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            async with self.session.get(f"{self.astrbot_url}/api/plug/alkaid/kb/collections", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("data", [])
                else:
                    logger.warning(f"⚠️ 获取知识库列表失败: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"❌ 获取知识库列表异常: {e}")
            return []
    
    async def create_knowledge_base(self, name: str, description: str = "", emoji: str = "📚") -> Optional[str]:
        """创建知识库"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # 先获取embedding提供商
        try:
            async with self.session.get(f"{self.astrbot_url}/api/config/provider/list?provider_type=embedding", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    providers = result.get("data", [])
                    if providers:
                        embedding_provider_id = providers[0]["id"]
                    else:
                        logger.error("❌ 未找到可用的embedding提供商")
                        return None
                else:
                    logger.error("❌ 获取提供商列表失败")
                    return None
        except Exception as e:
            logger.error(f"❌ 获取提供商列表异常: {e}")
            return None
        
        create_data = {
            "collection_name": name,
            "emoji": emoji,
            "description": description,
            "embedding_provider_id": embedding_provider_id
        }
        
        try:
            async with self.session.post(f"{self.astrbot_url}/api/plug/alkaid/kb/create_collection", 
                                       json=create_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"创建知识库响应: {result}")  # 调试信息
                    if result.get("status") == "ok":
                        # 获取创建后的实际知识库名称（可能包含UUID）
                        data = result.get("data", {})
                        if isinstance(data, dict):
                            created_name = data.get("collection_name", name)
                        else:
                            created_name = name
                        logger.info(f"✅ 创建知识库成功: {created_name}")
                        return created_name
                    else:
                        logger.error(f"❌ 创建知识库失败: {result.get('message')}")
                        return None
                else:
                    logger.error(f"❌ 创建知识库请求失败: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"❌ 创建知识库异常: {e}")
            return None
    
    async def upload_file(self, file_path: str, collection_name: str, 
                         chunk_size: int = None, chunk_overlap: int = None) -> bool:
        """上传单个文件到知识库"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename=os.path.basename(file_path))
                data.add_field('collection_name', collection_name)
                
                if chunk_size:
                    data.add_field('chunk_size', str(chunk_size))
                if chunk_overlap:
                    data.add_field('chunk_overlap', str(chunk_overlap))
                
                async with self.session.post(f"{self.astrbot_url}/api/plug/alkaid/kb/collection/add_file", 
                                           data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("status") == "ok":
                            logger.info(f"✅ 上传成功: {os.path.basename(file_path)}")
                            self.mark_file_uploaded(file_path, collection_name)
                            return True
                        else:
                            logger.error(f"❌ 上传失败: {os.path.basename(file_path)} - {result.get('message')}")
                            return False
                    else:
                        logger.error(f"❌ 上传请求失败: {os.path.basename(file_path)} - {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ 上传异常: {os.path.basename(file_path)} - {e}")
            return False
    
    def get_supported_files(self, folder_path: str) -> List[str]:
        """获取支持的文件列表"""
        supported_extensions = {
            '.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
            '.ppt', '.pptx', '.md', '.rtf', '.csv'
        }
        
        files = []
        try:
            for file_path in Path(folder_path).rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                    files.append(str(file_path))
        except Exception as e:
            logger.error(f"❌ 扫描文件失败: {e}")
        
        return sorted(files)
    
    async def close_session(self):
        """关闭session"""
        if self.session:
            await self.session.close()
    
    async def batch_upload_files(self, folder_path: str, kb_name: str = "批量上传知识库",
                               chunk_size: int = None, chunk_overlap: int = None,
                               delay: float = 1.0) -> bool:
        """批量上传文件夹中的所有文件"""
        try:
            if not await self.login():
                return False
            
            # 检查或创建知识库
            kbs = await self.get_knowledge_bases()
            kb_exists = any(kb.get('collection_name') == kb_name for kb in kbs)
            
            if not kb_exists:
                if not await self.create_knowledge_base(kb_name):
                    return False
                # 等待一下让知识库创建完成
                await asyncio.sleep(2)
                # 重新获取知识库列表，找到实际创建的知识库名称
                kbs = await self.get_knowledge_bases()
                logger.info(f"📋 知识库列表: {[kb.get('collection_name') for kb in kbs]}")
            
            # 找到匹配的知识库（可能是带UUID的名称）
            actual_kb_name = None
            for kb in kbs:
                if kb.get('collection_name') == kb_name or kb.get('collection_name', '').startswith(kb_name):
                    actual_kb_name = kb.get('collection_name')
                    break
            
            if not actual_kb_name:
                # 如果没有找到指定的知识库，使用第一个可用的知识库
                if kbs:
                    actual_kb_name = kbs[0].get('collection_name')
                    logger.warning(f"⚠️ 未找到指定知识库 '{kb_name}'，使用现有知识库: {actual_kb_name}")
                else:
                    logger.error(f"❌ 未找到知识库: {kb_name}")
                    logger.error(f"❌ 可用知识库: {[kb.get('collection_name') for kb in kbs]}")
                    return False
            
            logger.info(f"📚 使用知识库: {actual_kb_name}")
            
            # 获取所有支持的文件
            files = self.get_supported_files(folder_path)
            if not files:
                logger.warning(f"⚠️ 在 {folder_path} 中未找到支持的文件")
                return False
            
            logger.info(f"📁 找到 {len(files)} 个文件")
            
            # 过滤已上传的文件
            new_files = []
            skipped_files = []
            
            for file_path in files:
                if self.is_file_uploaded(file_path):
                    skipped_files.append(file_path)
                else:
                    new_files.append(file_path)
            
            logger.info(f"📊 统计信息:")
            logger.info(f"  - 总文件数: {len(files)}")
            logger.info(f"  - 已上传: {len(skipped_files)}")
            logger.info(f"  - 待上传: {len(new_files)}")
            
            if not new_files:
                logger.info("✅ 所有文件都已上传完成")
                return True
            
            # 开始上传
            success_count = 0
            failed_count = 0
            
            with tqdm(new_files, desc="上传进度", unit="文件") as pbar:
                for file_path in pbar:
                    pbar.set_description(f"正在上传: {os.path.basename(file_path)}")
                    
                    if await self.upload_file(file_path, actual_kb_name, chunk_size, chunk_overlap):
                        success_count += 1
                    else:
                        failed_count += 1
                    
                    # 延迟避免请求过快
                    if delay > 0:
                        await asyncio.sleep(delay)
            
            # 输出结果
            logger.info(f"🎉 批量上传完成!")
            logger.info(f"  - 成功: {success_count}")
            logger.info(f"  - 失败: {failed_count}")
            logger.info(f"  - 跳过: {len(skipped_files)}")
            
            return failed_count == 0
        finally:
            await self.close_session()

async def main():
    parser = argparse.ArgumentParser(description="批量上传文件到AstrBot知识库")
    parser.add_argument("folder_path", help="要上传的文件夹路径")
    parser.add_argument("--kb-name", default="批量上传知识库", help="知识库名称")
    parser.add_argument("--astrbot-url", default="http://localhost:6185", help="AstrBot地址")
    parser.add_argument("--username", default="Germania", help="用户名")
    parser.add_argument("--password", help="密码")
    parser.add_argument("--chunk-size", type=int, help="分片大小")
    parser.add_argument("--chunk-overlap", type=int, help="分片重叠")
    parser.add_argument("--delay", type=float, default=1.0, help="上传间隔(秒)")
    parser.add_argument("--record-file", default="upload_record.json", help="上传记录文件")
    
    args = parser.parse_args()
    
    # 检查文件夹是否存在
    if not os.path.exists(args.folder_path):
        logger.error(f"❌ 文件夹不存在: {args.folder_path}")
        return
    
    # 创建上传器
    uploader = BatchFileUploader(
        astrbot_url=args.astrbot_url,
        username=args.username,
        password=args.password,
        upload_record_file=args.record_file
    )
    
    # 开始批量上传
    success = await uploader.batch_upload_files(
        folder_path=args.folder_path,
        kb_name=args.kb_name,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        delay=args.delay
    )
    
    if success:
        logger.info("✅ 所有文件上传完成!")
    else:
        logger.error("❌ 部分文件上传失败，请检查日志")

if __name__ == "__main__":
    asyncio.run(main()) 