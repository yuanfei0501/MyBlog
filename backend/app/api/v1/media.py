import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core import get_db
from app.core.config import settings
from app.models import Media
from app.schemas import MediaResponse, PaginatedResponse, MessageResponse
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/media", tags=["媒体管理"])


def generate_filename(original_filename: str) -> str:
    """生成唯一文件名"""
    ext = original_filename.rsplit(".", 1)[-1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    return f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}.{ext}"


@router.post("/upload", response_model=MediaResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传文件"""
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制")

    # 生成文件名和路径
    filename = generate_filename(file.filename)
    year_month = datetime.now().strftime("%Y/%m")
    upload_dir = os.path.join(settings.UPLOAD_DIR, year_month)
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, filename)
    relative_path = f"/uploads/{year_month}/{filename}"

    # 保存文件
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    # 保存到数据库
    media = Media(
        filename=file.filename,
        filepath=relative_path,
        filesize=file.size,
        mimetype=file.content_type,
        uploader_id=current_user.id,
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)

    return media


@router.get("", response_model=PaginatedResponse)
async def list_media(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取媒体列表"""
    offset = (page - 1) * page_size
    query = select(Media).order_by(Media.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    # 获取总数
    count_result = await db.execute(select(Media))
    total = len(count_result.scalars().all())

    return PaginatedResponse(
        items=[MediaResponse.model_validate(m) for m in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.delete("/{media_id}", response_model=MessageResponse)
async def delete_media(
    media_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除媒体文件"""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="文件不存在")

    # 权限检查：只有上传者或管理员可以删除
    if media.uploader_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="无权限删除此文件")

    # 删除物理文件
    if os.path.exists(media.filepath.lstrip("/")):
        os.remove(media.filepath.lstrip("/"))

    # 删除数据库记录
    await db.delete(media)
    await db.commit()

    return MessageResponse(message="文件已删除")
