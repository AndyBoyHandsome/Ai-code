from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.services.image_service import ImageService
from app.models.schemas import GroupResult, ImageGroup, GroupRequest
import os
import shutil

router = APIRouter()

# 设置上传目录
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 初始化 ImageService
image_service = ImageService(upload_dir=UPLOAD_DIR)

@router.post("/clear-cache")
async def clear_cache():
    """清除缓存和上传的图片"""
    try:
        # 清除上传目录中的所有文件
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
        if os.path.exists(uploads_dir):
            for filename in os.listdir(uploads_dir):
                file_path = os.path.join(uploads_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

        # 重置 ImageService 的状态
        image_service.reset()

        return {"message": "缓存已清除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/images/upload", response_model=List[str])
async def upload_images(files: List[UploadFile] = File(...)):
    """
    上传多个图片文件
    """
    try:
        # 验证是否有文件上传
        if not files:
            raise HTTPException(status_code=400, detail="没有上传任何文件")
        # 验证文件类型
        for file in files:
            if not file.content_type or not file.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail=f"文件 {file.filename} 不是有效的图片文件类型"
                )
        #print(f"Attempting to save {len(files)} files...")
        image_ids = await image_service.save_images(files)
        print(f"Successfully saved {len(image_ids)} files")
        return image_ids
        
    except ValueError as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error during upload: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器处理文件时发生错误")

@router.post("/images/group", response_model=List[GroupResult])
async def group_images(request: GroupRequest):
    """
    对上传的图片进行智能分组
    Args:
        request: GroupRequest - 包含图片ID列表和相似度阈值的请求对象
    Returns:
        List[GroupResult]: 分组结果列表
    """
    try:
        groups =  image_service.auto_group_images(
            request.image_ids,
            request.similarity_threshold
        )
        print(f"Grouping result: {groups}")
        return groups
    except Exception as e:
        print(f"Error during grouping: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/images")
async def get_images():
    """
    获取所有图片列表
    """
    try:
        images = []
        for filename in os.listdir(UPLOAD_DIR):
            if os.path.isfile(os.path.join(UPLOAD_DIR, filename)):
                images.append({"filename": filename})
        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/images/{image_id}")
async def get_image(image_id: str):
    """
    获取单个图片的信息
    """
    try:
        image = await image_service.get_image(image_id)
        return image
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/images/{image_id}")
async def delete_image(image_id: str):
    """
    删除单个图片
    """
    try:
        await image_service.delete_image(image_id)
        return {"message": "Image deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/groups", response_model=ImageGroup)
async def create_group(group: ImageGroup):
    """
    创建新的图片分组
    """
    try:
        created_group = await image_service.create_group(group)
        return created_group
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/groups", response_model=List[ImageGroup])
async def get_groups():
    """
    获取所有图片分组
    """
    try:
        groups = await image_service.get_groups()
        return groups
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/groups/{group_id}")
async def update_group(group_id: str, group: ImageGroup):
    """
    更新图片分组信息
    """
    try:
        updated_group = await image_service.update_group(group_id, group)
        return updated_group
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/groups/{group_id}")
async def delete_group(group_id: str):
    """
    删除图片分组
    """
    try:
        await image_service.delete_group(group_id)
        return {"message": "Group deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) 