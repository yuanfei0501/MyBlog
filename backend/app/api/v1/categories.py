from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slugify import slugify

from app.core import get_db
from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate, CategoryResponse, MessageResponse
from app.api.v1.auth import get_current_admin

router = APIRouter(prefix="/categories", tags=["分类"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """获取分类列表"""
    result = await db.execute(select(Category).order_by(Category.created_at))
    return result.scalars().all()


@router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(
    data: CategoryCreate,
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """创建分类（管理员）"""
    slug = slugify(data.name)
    result = await db.execute(select(Category).where(Category.slug == slug))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="分类已存在")

    category = Category(name=data.name, slug=slug, description=data.description, parent_id=data.parent_id)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """更新分类（管理员）"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    if data.name:
        category.name = data.name
        category.slug = slugify(data.name)
    if data.description is not None:
        category.description = data.description
    if data.parent_id is not None:
        category.parent_id = data.parent_id

    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", response_model=MessageResponse)
async def delete_category(
    category_id: int,
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除分类（管理员）"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    await db.delete(category)
    await db.commit()
    return MessageResponse(message="分类已删除")
