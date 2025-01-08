import os
import uuid
import cv2
import numpy as np
from typing import List, Dict, Any
from PIL import Image
from datetime import datetime
import torch
import insightface
from insightface.app import FaceAnalysis
import faiss
from pathlib import Path
import io
import json
from tqdm import tqdm
from fastapi import UploadFile

# Set environment variables to control threading
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['OMP_THREAD_LIMIT'] = '1'

from app.models.schemas import ImageGroup
from app.models.schemas import Image as ImageModel
from app.models.schemas import ImageGroup, GroupResult, ImageFeatures
from app.services.face_quality import FaceQualityAssessor
from app.services.face_recognizer import FaceRecognizer
class ImageService:
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # 初始化人脸分析模型
        self.face_analyzer = FaceAnalysis(
            name='buffalo_l',  # 使用大模型以提高准确率
            providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
        )
        self.face_analyzer.prepare(ctx_id=0, det_size=(640, 640))
        self.quality_assessor = FaceQualityAssessor() 
        self.recognizer = FaceRecognizer()
        # 初始化 Faiss 索引
        self.feature_dim = 512  # ArcFace 特征维度
        self.index = faiss.IndexFlatIP(self.feature_dim)  # 使用内积相似度
        
        self.images: Dict[str, ImageModel] = {}
        self.groups: Dict[str, ImageGroup] = {}
        self._ensure_upload_dir()

    def _ensure_upload_dir(self):
        """确保上传目录存在"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
    
    def detect_faces(self, image):
        """检测图片中的人脸"""
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            
        faces = self.face_analyzer.get(image)
        quality_faces = []
        
        for face in faces:
            if face.det_score > 0.5:
                is_good, quality_score, reasons = self.quality_assessor.is_good_quality(image, face)
                if is_good:
                    # 将face对象转换为可序列化的字典
                    face_dict = {
                        'bbox': face.bbox.tolist(),
                        'kps': face.kps.tolist(),
                        'det_score': float(face.det_score),
                        'features': face.embedding.tolist(),
                        'quality_score': quality_score,
                        # 'confidence': float(quality_score),
                        # 'gender': face.gender,
                        # 'age': face.age,
                        # 'angle': face.pose
                    }
                    quality_faces.append(face_dict)
        
        return quality_faces
    
    def extract_face_features(self, image_path: str) -> Dict[str, Any]:
        """使用 RetinaFace 和 ArcFace 提取人脸特征"""
        try:
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                return None
                
            faces = self.detect_faces(image)
            if not faces:
                print("没0人脸！")
                return {'total_faces': 0, 'features': []}
            print(f"{len(faces)}人脸！")
            return {
                'faces': faces,
                'total_faces': len(faces)
            }
        except Exception as e:
            print(f"Error extracting face features: {str(e)}")
            return None
            
    def calculate_face_similarity(self, feature1: Dict, feature2: Dict) -> float:
        """计算两张图片中人脸的相似度"""
        if not feature1['features'] or not feature2['features']:
            return 0.0
            
        # 获取所有人脸特征向量
        faces1 = [np.array(face['embedding']) for face in feature1['features']]
        faces2 = [np.array(face['embedding']) for face in feature2['features']]
        
        # 计算每对人脸之间的相似度
        max_similarity = 0.0
        for face1 in faces1:
            for face2 in faces2:
                # 使用余弦相似度
                similarity = np.dot(face1, face2) / (np.linalg.norm(face1) * np.linalg.norm(face2))
                max_similarity = max(max_similarity, similarity)
        
        return float(max_similarity)
        
    def auto_group_images(self, image_ids: List[str], similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """使用 RetinaFace 和 ArcFace 进行智能分组
        Args:
            image_ids: 图片ID列表
            similarity_threshold: 相似度阈值，默认0.55
        Returns:
            List[Dict[str, Any]]: 分组结果列表
        """
        # 存储每张图片的特征
        features_dict = {}
        embeddings_list = []
        image_map = []
        
        print("正在提取人脸特征...")
        for img_id in tqdm(image_ids):
            if img_id in self.images:
                image_name = self.images[img_id].filename
                full_path = os.path.join(self.upload_dir, image_name)
                if not os.path.exists(full_path):
                    continue
                    
                # 提取人脸特征
                features = self.extract_face_features(full_path)
                if features is not None and features['total_faces'] > 0:
                    features_dict[img_id] = features
        # 第二步：根据人脸特征相似度进行分组
        # 处理结果
        face_count = 0
        for img_path, feature1 in features_dict.items():
            if feature1['faces']:
                for face_dict in feature1['faces']:
                    try:
                        self.recognizer.add_face(face_dict, img_path)
                        face_count += 1
                    except Exception as e:
                        print(f"添加人脸时出错 ({img_path}): {str(e)}")
        
        print(f"共处理 {len(image_ids)} 张图片，"
            f"检测到 {face_count} 个人脸")
        
        # 构建索引并聚类
        if len(self.recognizer.face_features) > 0:
            print("开始构建索引...")
            self.recognizer.build_index()
            
            print("开始聚类分析...")
            groups = self.recognizer.cluster_faces(threshold=similarity_threshold)
            print(f"聚类完成，找到 {len(groups)} 个分组")
            
            # 格式化输出结果
            result = []
            for group_data in groups:
                # avg_quality = np.mean(group_data['quality_scores'])
                if len(group_data['image_ids']) > 0:
                    result.append({
                        'group_id': str(group_data['group_id']),
                        'name': f"人物_{group_data['group_id']}",
                        'image_ids': list(set(group_data['image_ids'])),
                        # 'quality_score': float(avg_quality)
                    })
            return result
        else:
            print("没有检测到任何有效的人脸！")
            return []

    async def save_images(self, files: List[UploadFile]) -> List[str]:
        """保存上传的图片文件"""
        image_ids = []
        for file in files:
            # 生成唯一ID
            image_id = str(uuid.uuid4())
            
            # 构建文件路径
            file_ext = os.path.splitext(file.filename)[1]
            filename = f"{image_id}{file_ext}"
            filepath = os.path.join(self.upload_dir, filename)
            # 保存文件
            with open(filepath, "wb") as f:
                content = await file.read()
                f.write(content)
            # 获取图片信息
            with Image.open(filepath) as img:
                width, height = img.size
            
            # 创建图片记录
            self.images[image_id] = ImageModel(
                id=image_id,
                filename=filename,
                name=file.filename,
                url=f"/uploads/{filename}",
                size=os.path.getsize(filepath),
                score =0,
                width=width,
                height=height,
                created_at=datetime.now()
            )
            
            image_ids.append(image_id)
        
        return image_ids

    async def get_image(self, image_id: str) -> ImageModel:
        """获取单个图片信息"""
        if image_id not in self.images:
            raise ValueError(f"Image not found: {image_id}")
        return self.images[image_id]

    async def delete_image(self, image_id: str):
        """删除图片"""
        if image_id not in self.images:
            raise ValueError(f"Image not found: {image_id}")
        
        image = self.images[image_id]
        filepath = os.path.join(os.getcwd(), image.url.lstrip('/'))
        
        # 删除文件
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # 删除记录
        del self.images[image_id]

    async def create_group(self, group: ImageGroup) -> ImageGroup:
        """创建新的图片分组"""
        group_id = str(uuid.uuid4())
        group.id = group_id
        group.created_at = datetime.now()
        self.groups[group_id] = group
        return group

    async def get_groups(self) -> List[ImageGroup]:
        """获取所有图片分组"""
        return list(self.groups.values())

    async def update_group(self, group_id: str, group: ImageGroup) -> ImageGroup:
        """更新图片分组信息"""
        if group_id not in self.groups:
            raise ValueError(f"Group not found: {group_id}")
        
        group.updated_at = datetime.now()
        self.groups[group_id] = group
        return group

    async def delete_group(self, group_id: str):
        """删除图片分组
        Args:
            group_id: str - 分组ID
        Returns:
            bool: 是否删除成功
        """
        try:
            group_file = os.path.join(os.path.dirname(self.upload_dir), "groups.json")
            if not os.path.exists(group_file):
                return False
            
            with open(group_file, 'r', encoding='utf-8') as f:
                groups = json.load(f)
            
            # 查找并删除分组
            groups = [g for g in groups if g['id'] != group_id]
            
            with open(group_file, 'w', encoding='utf-8') as f:
                json.dump(groups, f, ensure_ascii=False, default=str)
            
            return True
            
        except Exception as e:
            print(f"Error deleting group: {str(e)}")
            raise 

    def reset(self):
        """重置服务状态，清除所有图片和分组信息"""
        self.images.clear()
        self.groups.clear()
        # 重置人脸识别器的状态
        self.recognizer = FaceRecognizer() 