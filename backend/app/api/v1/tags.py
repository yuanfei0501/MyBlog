from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slugify import slugify

from app.core import get_db
from app.models import Tag
from app.schemas import TagCreate, TagResponse, MessageResponse
from app.api.v1.auth import get_current_admin

router = APIRouter(prefix="/tags", tags=["标签"])


@router.get("", response_model=list[TagResponse])
async def list_tags(db: AsyncSession = Depends(get_db)):
    """获取标签列表"""
    result = await db.execute(select(Tag).order_by(Tag.name))
    return result.scalars().all()


@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(
    data: TagCreate,
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """创建标签（管理员）"""
    slug = slugify(data.name)
    result = await db.execute(select(Tag).where(Tag.slug == slug))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="标签已存在")

    tag = Tag(name=data.name, slug=slug)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


@router.delete("/{tag_id}", response_model=MessageResponse)
async def delete_tag(
    tag_id: int,
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除标签（管理员）"""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    await db.delete(tag)
    await db.commit()
    return MessageResponse(message="标签已删除")
