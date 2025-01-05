from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Image(BaseModel):
    """图片模型"""
    id: Optional[str] = None
    filename: str
    name: str
    url: Optional[str] = None
    size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    mode: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    score:float

class ImageGroup(BaseModel):
    """图片分组模型"""
    id: Optional[str] = None
    name: str
    image_ids: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

class FaceFeatures(BaseModel):
    """人脸特征模型"""
    bbox: List[int]
    features: List[float]
    confidence: float

class ImageFeatures(BaseModel):
    """图片特征模型"""
    faces: List[FaceFeatures]
    total_faces: int

class GroupResult(BaseModel):
    """分组结果模型"""
    group_id: str
    name: str
    image_ids: List[str]
    similarity_score: float = Field(ge=0.0, le=1.0)
    face_count: int = Field(ge=0)

class GroupRequest(BaseModel):
    """分组请求模型"""
    image_ids: List[str]
    similarity_threshold: float = Field(default=0.55, ge=0.0, le=1.0) 