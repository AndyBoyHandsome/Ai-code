from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any
from services.image_service import ImageService
import os

router = APIRouter()
image_service = ImageService(upload_dir="uploads")

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)) -> Dict[str, str]:
    """上传图片"""
    try:
        filename = image_service.save_image(file)
        return {"filename": filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/info/{filename}")
async def get_image_info(filename: str) -> Dict[str, Any]:
    """获取图片信息"""
    try:
        return image_service.get_image_info(filename)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{filename}")
async def delete_image(filename: str) -> Dict[str, bool]:
    """删除图片"""
    try:
        success = image_service.delete_image(filename)
        if not success:
            raise HTTPException(status_code=404, detail="Image not found")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto-group")
async def auto_group_images(
    image_paths: List[str],
    similarity_threshold: float = 0.55
) -> List[Dict[str, Any]]:
    """智能分组图片"""
    try:
        print(f"Auto-grouping images with similarity threshold: {similarity_threshold}")
        groups = image_service.auto_group_images(image_paths, similarity_threshold)
        return groups
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detect/{filename}")
async def get_detection_info(filename: str) -> Dict[str, Any]:
    """获取图片中的目标检测信息"""
    try:
        return image_service.get_detection_info(filename)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 