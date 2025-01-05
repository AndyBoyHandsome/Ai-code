import os
import uuid
import cv2
import numpy as np
from typing import List, Dict, Any
from PIL import Image
from datetime import datetime
from ultralytics import YOLO
import torch
from pathlib import Path
from fastapi import UploadFile
import io
import json

from app.models.schemas import ImageGroup
from app.models.schemas import Image as ImageModel
from app.models.schemas import ImageGroup, GroupResult, ImageFeatures

class ImageService:
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # 初始化 YOLOv8 模型
        model_dir = os.path.join(os.path.dirname(__file__), "..", "models")
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        # try:
        #     face_model_path = os.path.join(model_dir, "yolov8n-face.pt")
        #     # 使用专门的人脸检测模型
        #     self.model = YOLO("./yolov8n-face.pt")
        #     print("人脸检测模型加载成功")
        # except Exception as e:
        #     print(f"Error initializing models: {str(e)}")
        #     raise    
        model_path = os.path.join(model_dir, "yolov8n.pt")
        face_model_path = os.path.join(model_dir, "yolov8n-face.pt")
        
        try:
            if not os.path.exists(model_path):
                # 如果模型不存在，下载模型
                self.model = YOLO("yolov8n.pt")
                self.model.export()  # 导出模型
                if os.path.exists("yolov8n.pt"):
                    os.rename("yolov8n.pt", model_path)
            else:
                self.model = YOLO(model_path)
            
            # 初始化人脸检测模型
            if not os.path.exists(face_model_path):
                # 如果人脸模型不存在，下载并转换
                base_model = YOLO("yolov8n.pt")
                base_model.task = 'face'
                base_model.export()  # 导出模型
                if os.path.exists("yolov8n-face.pt"):
                    os.rename("yolov8n-face.pt", face_model_path)
                self.face_model = base_model
            else:
                self.face_model = YOLO(face_model_path)
        except Exception as e:
            print(f"Error initializing models: {str(e)}")
            raise
        self.images: Dict[str, ImageModel] = {}
        self.groups: Dict[str, ImageGroup] = {}
        self._ensure_upload_dir()

    def _ensure_upload_dir(self):
        """确保上传目录存在"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)


    def extract_features(self, image_path: str) -> np.ndarray:
        """提取图像特征"""
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        # 使用 YOLOv8 进行目标检测
        results = self.model(img)
        
        # 如果没有检测到任何目标，返回 None
        if len(results[0].boxes) == 0:
            return None
            
        # 获取所有检测到的目标的特征
        features = []
        for box in results[0].boxes:
            # 获取目标的类别和置信度
            cls = int(box.cls)
            conf = float(box.conf)
            
            # 获取边界框坐标
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # 提取目标区域
            roi = img[y1:y2, x1:x2]
            if roi.size == 0:
                continue
                
            # 调整大小为统一尺寸
            roi = cv2.resize(roi, (224, 224))
            
            # 转换为特征向量（使用像素值的平均值作为简单特征）
            feature = cv2.mean(roi)[:3]  # 只使用 RGB 通道
            features.append(feature)
        
        if not features:
            return None
            
        # 返回所有特征的平均值
        return np.mean(features, axis=0)

    def calculate_similarity(self, feature1: np.ndarray, feature2: np.ndarray) -> float:
        """计算两个特征向量的相似度"""
        if feature1 is None or feature2 is None:
            return 0.0
            
        # 使用余弦相似度
        similarity = np.dot(feature1, feature2) / (np.linalg.norm(feature1) * np.linalg.norm(feature2))
        return float(similarity)

    def extract_face_features(self, image_path: str) -> Dict[str, Any]:
        """使用 YOLOv8 提取人脸特征"""
        try:
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                return None
                
            # 使用YOLOv8进行人脸检测
            results = self.face_model(image)
            
            if len(results) == 0 or len(results[0].boxes) == 0:
                return None
                
            faces = []
            for box in results[0].boxes:
                if len(faces) > 0:
                    continue
                # 获取人脸框坐标
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                
                # 提取人脸区域
                face = image[y1:y2, x1:x2]
                
                # 调整人脸大小为统一尺寸
                face = cv2.resize(face, (112, 112))
                
                # 转换为RGB格式
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                
                # 归一化
                face = face.astype(np.float32) / 255.0
                
                faces.append({
                    'bbox': [x1, y1, x2, y2],
                    'features': face.flatten(),
                    'confidence': float(box.conf)
                })
            
            return {
                'faces': faces,
                'total_faces': len(faces)
            }
            
        except Exception as e:
            print(f"Error extracting face features: {str(e)}")
            return None
            
    def calculate_face_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> float:
        """计算两张图片中人脸的相似度"""
        if not features1 or not features2:
            return 0.0
            
        max_similarity = 0.0
        
        # 比较每个人脸对的相似度
        for face1 in features1['faces']:
            for face2 in features2['faces']:
                # 计算余弦相似度
                similarity = np.dot(face1['features'], face2['features']) / (
                    np.linalg.norm(face1['features']) * np.linalg.norm(face2['features'])
                )
                max_similarity = max(max_similarity, similarity)
                
        return max_similarity
        
    def auto_group_images(self, image_ids: List[str], similarity_threshold: float = 0.55) -> List[Dict[str, Any]]:
        """使用 YOLOv8 进行智能分组
        Args:
            image_ids: 图片ID列表
            similarity_threshold: 相似度阈值，默认0.55
        Returns:
            List[Dict[str, Any]]: 分组结果列表
        """
        # 存储每张图片的特征
        features_dict = {}
        # 第一步：提取所有图片的人脸特征
        for img_id in image_ids:
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
        groups = []
        processed_images = set()
        
        for img_path1, feature1 in features_dict.items():
            if img_path1 in processed_images:
                continue
                
            current_group = {
                'group_id': f"group_{len(groups)}",
                'name': f"人脸分组 {len(groups) + 1}",
                'image_ids': [img_path1],
                'image_scores': [0],
                'similarity_score': 1.0,
                'face_count': feature1['total_faces']
            }
            processed_images.add(img_path1)
            
            # 比较与其他图片的相似度
            for img_path2, feature2 in features_dict.items():
                if img_path2 in processed_images:
                    continue
                    
                # 计算人脸相似度
                similarity = self.calculate_face_similarity(feature1, feature2)
                
                # 如果相似度超过阈值，将图片添加到当前分组
                if similarity >= similarity_threshold:
                    current_group['image_ids'].append(img_path2)
                    current_group['image_scores'].append(similarity)
                    current_group['similarity_score'] = min(
                        current_group['similarity_score'],
                        similarity
                    )
                    current_group['face_count'] = max(
                        current_group['face_count'],
                        feature2['total_faces']
                    )
                    processed_images.add(img_path2)
                    
            if len(current_group['image_ids']) > 1:
                groups.append(current_group)
                
        # 第三步：处理未分组的图片
        ungrouped_images = [
            img_path for img_path in image_ids
            if img_path not in processed_images
        ]
        if ungrouped_images:
            groups.append({
                'group_id': f"group_{len(groups)}",
                'name': "其他图片",
                'image_ids': ungrouped_images,
                'similarity_score': 0.0,
                'face_count': 0
            })  
        return groups


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