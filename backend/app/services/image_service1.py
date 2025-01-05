import os
import uuid
import numpy as np
from datetime import datetime
from typing import List, Dict
from fastapi import UploadFile
from PIL import Image
import cv2
from sklearn.cluster import DBSCAN
from app.models.schemas import Image as ImageModel
from app.models.schemas import ImageGroup, GroupResult, ImageFeatures

class ImageService:
    def __init__(self):
        self.upload_dir = "uploads"
        self.images: Dict[str, ImageModel] = {}
        self.groups: Dict[str, ImageGroup] = {}
        self._ensure_upload_dir()

    def _ensure_upload_dir(self):
        """确保上传目录存在"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

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
                filename=file.filename,
                url=f"/uploads/{filename}",
                size=os.path.getsize(filepath),
                # type=file.content_type,
                width=width,
                height=height,
                created_at=datetime.now(),
            )
            
            image_ids.append(image_id)
        
        return image_ids

    async def group_images(self, image_ids: List[str]) -> List[GroupResult]:
        """对图片进行智能分组"""
        # 提取特征
        features = []
        for image_id in image_ids:
            if image_id in self.images:
                image = self.images[image_id]
                features.append(await self._extract_features(image))
        
        if not features:
            return []
        
        # 转换特征为numpy数组
        feature_matrix = np.array([
            f.color_features + f.texture_features + f.composition_features 
            for f in features
        ])
        
        # 使用DBSCAN进行聚类
        clustering = DBSCAN(eps=0.5, min_samples=2).fit(feature_matrix)
        labels = clustering.labels_
        
        # 整理分组结果
        groups = {}
        for idx, label in enumerate(labels):
            if label == -1:  # 噪声点（未分组）
                continue
            
            if label not in groups:
                groups[label] = {
                    'image_ids': [],
                    'features': []
                }
            
            groups[label]['image_ids'].append(image_ids[idx])
            groups[label]['features'].append(feature_matrix[idx])
        
        # 创建分组结果
        results = []
        for label, group in groups.items():
            # 计算组内平均相似度
            features = np.array(group['features'])
            similarity_score = self._calculate_group_similarity(features)
            
            # 生成唯一ID并创建分组
            group_id = str(uuid.uuid4())
            group_name = f"Group {label + 1}"
            
            # 创建并保存分组
            self.groups[group_id] = ImageGroup(
                id=group_id,
                name=group_name,
                description=f"相似度: {similarity_score:.2%}",
                auto_sort=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                images=group['image_ids']
            )
            
            # 更新图片的分组ID
            for image_id in group['image_ids']:
                if image_id in self.images:
                    self.images[image_id].group_id = group_id
                    self.images[image_id].updated_at = datetime.now()
            
            # 添加到结果列表
            results.append(GroupResult(
                group_id=group_id,
                name=group_name,
                similarity_score=similarity_score,
                image_ids=group['image_ids']
            ))
        
        return results

    async def _extract_features(self, image: ImageModel) -> ImageFeatures:
        """提取图片特征"""
        filepath = os.path.join(os.getcwd(), image.url.lstrip('/'))
        img = cv2.imread(filepath)
        if img is None:
            raise ValueError(f"Cannot read image: {filepath}")
        
        # 调整图片大小为统一尺寸
        img = cv2.resize(img, (224, 224))
        
        # 1. 颜色特征
        color_features = self._extract_color_features(img)
        
        # 2. 纹理特征
        texture_features = self._extract_texture_features(img)
        
        # 3. 构图特征
        composition_features = self._extract_composition_features(img)
        
        return ImageFeatures(
            id=image.id,
            color_features=color_features,
            texture_features=texture_features,
            composition_features=composition_features,
            metadata={
                'width': image.width,
                'height': image.height,
                'aspect_ratio': image.width / image.height if image.width and image.height else None
            }
        )

    def _extract_color_features(self, img: np.ndarray) -> List[float]:
        """提取颜色特征"""
        # 转换为HSV颜色空间
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # 计算颜色直方图
        h_hist = cv2.calcHist([hsv], [0], None, [8], [0, 180])
        s_hist = cv2.calcHist([hsv], [1], None, [4], [0, 256])
        v_hist = cv2.calcHist([hsv], [2], None, [4], [0, 256])
        
        # 归一化
        h_hist = cv2.normalize(h_hist, h_hist).flatten()
        s_hist = cv2.normalize(s_hist, s_hist).flatten()
        v_hist = cv2.normalize(v_hist, v_hist).flatten()
        
        return list(np.concatenate([h_hist, s_hist, v_hist]))

    def _extract_texture_features(self, img: np.ndarray) -> List[float]:
        """提取纹理特征"""
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 计算GLCM（灰度共生矩阵）特征
        glcm = self._calculate_glcm(gray)
        
        # 计算Haralick纹理特征
        haralick = self._calculate_haralick_features(glcm)
        
        return list(haralick)

    def _extract_composition_features(self, img: np.ndarray) -> List[float]:
        """提取构图特征"""
        # 将图像分为3x3网格
        h, w = img.shape[:2]
        cell_h, cell_w = h // 3, w // 3
        
        features = []
        for i in range(3):
            for j in range(3):
                # 提取网格cell
                cell = img[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
                
                # 计算每个网格的平均亮度和边缘强度
                gray_cell = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
                avg_brightness = np.mean(gray_cell)
                
                edges = cv2.Canny(gray_cell, 100, 200)
                edge_density = np.mean(edges)
                
                features.extend([avg_brightness, edge_density])
        
        # 归一化特征
        features = np.array(features)
        features = (features - np.min(features)) / (np.max(features) - np.min(features))
        
        return list(features)

    def _calculate_glcm(self, img: np.ndarray) -> np.ndarray:
        """计算灰度共生矩阵"""
        levels = 8
        h, w = img.shape
        # 量化灰度级别
        img = img // (256 // levels)
        glcm = np.zeros((levels, levels))
        
        for i in range(h-1):
            for j in range(w-1):
                current = img[i, j]
                right = img[i, j+1]
                glcm[current, right] += 1
        
        # 对称化和归一化
        glcm = glcm + glcm.T
        glcm = glcm / glcm.sum()
        
        return glcm

    def _calculate_haralick_features(self, glcm: np.ndarray) -> np.ndarray:
        """计算Haralick纹理特征"""
        features = []
        
        # 计算对比度
        contrast = np.sum(np.square(np.arange(glcm.shape[0])) * glcm)
        features.append(contrast)
        
        # 计算同质性
        homogeneity = np.sum(glcm / (1 + np.square(np.arange(glcm.shape[0]))))
        features.append(homogeneity)
        
        # 计算能量
        energy = np.sum(np.square(glcm))
        features.append(energy)
        
        # 计算相关性
        mu_i = np.sum(np.arange(glcm.shape[0]) * np.sum(glcm, axis=1))
        mu_j = np.sum(np.arange(glcm.shape[0]) * np.sum(glcm, axis=0))
        sigma_i = np.sqrt(np.sum(np.square(np.arange(glcm.shape[0]) - mu_i) * np.sum(glcm, axis=1)))
        sigma_j = np.sqrt(np.sum(np.square(np.arange(glcm.shape[0]) - mu_j) * np.sum(glcm, axis=0)))
        
        correlation = np.sum((np.arange(glcm.shape[0])[:, None] - mu_i) * 
                           (np.arange(glcm.shape[0])[None, :] - mu_j) * 
                           glcm) / (sigma_i * sigma_j)
        features.append(correlation)
        
        return np.array(features)

    def _calculate_group_similarity(self, features: np.ndarray) -> float:
        """计算组内平均相似度"""
        if len(features) < 2:
            return 1.0
        
        # 计算组内所有图片对之间��余弦相似度
        similarities = []
        for i in range(len(features)):
            for j in range(i + 1, len(features)):
                similarity = np.dot(features[i], features[j]) / (
                    np.linalg.norm(features[i]) * np.linalg.norm(features[j])
                )
                similarities.append(similarity)
        
        return float(np.mean(similarities))

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
        """删除图片分组"""
        if group_id not in self.groups:
            raise ValueError(f"Group not found: {group_id}")
        
        # 更新相关图片的分组ID
        for image in self.images.values():
            if image.group_id == group_id:
                image.group_id = None
                image.updated_at = datetime.now()
        
        # 删除分组
        del self.groups[group_id] 