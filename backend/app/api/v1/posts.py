from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional
from slugify import slugify
from datetime import datetime

from app.core import get_db
from app.core.config import settings
from app.models import User, Post, Category, Tag, PostTag, PostStatus
from app.schemas import (
    PostCreate,
    PostUpdate,
    PostListResponse,
    PostDetailResponse,
    PaginatedResponse,
    MessageResponse,
)
from app.api.v1.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/posts", tags=["文章"])


async def get_post_with_relations(db: AsyncSession, post_id: int = None, slug: str = None):
    """获取文章及其关联数据"""
    query = select(Post).options(
        selectinload(Post.author),
        selectinload(Post.category),
        selectinload(Post.tags),
    )
    if post_id:
        query = query.where(Post.id == post_id)
    elif slug:
        query = query.where(Post.slug == slug)
    else:
        return None

    result = await db.execute(query)
    return result.scalar_one_or_none()


@router.get("", response_model=PaginatedResponse)
async def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取文章列表"""
    query = select(Post).options(
        selectinload(Post.author),
        selectinload(Post.category),
        selectinload(Post.tags),
    )

    # 筛选条件
    if status:
        query = query.where(Post.status == PostStatus(status))
    else:
        # 默认只显示已发布的文章
        query = query.where(Post.status == PostStatus.PUBLISHED)

    if category_id:
        query = query.where(Post.category_id == category_id)

    if tag_id:
        query = query.where(Post.tags.any(Tag.id == tag_id))

    if keyword:
        query = query.where(
            or_(
                Post.title.ilike(f"%{keyword}%"),
                Post.content.ilike(f"%{keyword}%"),
                Post.summary.ilike(f"%{keyword}%"),
            )
        )

    # 排序：置顶优先，然后按发布时间倒序
    query = query.order_by(Post.is_top.desc(), Post.published_at.desc())

    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    posts = result.scalars().all()

    return PaginatedResponse(
        items=[PostListResponse.model_validate(post) for post in posts],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{slug}", response_model=PostDetailResponse)
async def get_post(slug: str, db: AsyncSession = Depends(get_db)):
    """获取文章详情"""
    post = await get_post_with_relations(db, slug=slug)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 增加阅读量
    post.view_count += 1
    await db.commit()

    return PostDetailResponse.model_validate(post)


@router.get("/detail/{post_id}", response_model=PostDetailResponse)
async def get_post_by_id(post_id: int, db: AsyncSession = Depends(get_db)):
    """通过 ID 获取文章详情（用于编辑）"""
    post = await get_post_with_relations(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return PostDetailResponse.model_validate(post)


@router.post("", response_model=PostDetailResponse, status_code=201)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建文章"""
    # 生成 slug
    slug = slugify(post_data.title)
    # 检查 slug 是否已存在
    result = await db.execute(select(Post).where(Post.slug == slug))
    if result.scalar_one_or_none():
        slug = f"{slug}-{int(datetime.now().timestamp())}"

    # 创建文章
    post = Post(
        title=post_data.title,
        slug=slug,
        content=post_data.content,
        summary=post_data.summary,
        cover_image=post_data.cover_image,
        category_id=post_data.category_id,
        is_top=post_data.is_top,
        author_id=current_user.id,
        status=PostStatus(post_data.status),
        published_at=datetime.utcnow() if post_data.status == "published" else None,
    )

    # 处理标签
    for tag_name in post_data.tags:
        tag_slug = slugify(tag_name)
        result = await db.execute(select(Tag).where(Tag.slug == tag_slug))
        tag = result.scalar_one_or_none()
        if not tag:
            tag = Tag(name=tag_name, slug=tag_slug)
            db.add(tag)
            await db.flush()
        post.tags.append(tag)

    db.add(post)
    await db.commit()
    await db.refresh(post)

    # 重新获取带关联的文章
    post = await get_post_with_relations(db, post_id=post.id)
    return PostDetailResponse.model_validate(post)


@router.put("/{post_id}", response_model=PostDetailResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新文章"""
    post = await get_post_with_relations(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 权限检查
    if post.author_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="无权限修改此文章")

    # 更新字段
    update_data = post_data.model_dump(exclude_unset=True, exclude={"tags"})

    # 处理状态变更
    if "status" in update_data:
        new_status = PostStatus(update_data["status"])
        if new_status == PostStatus.PUBLISHED and post.status != PostStatus.PUBLISHED:
            update_data["published_at"] = datetime.utcnow()
        update_data["status"] = new_status

    for field, value in update_data.items():
        setattr(post, field, value)

    # 更新标签
    if post_data.tags is not None:
        post.tags.clear()
        for tag_name in post_data.tags:
            tag_slug = slugify(tag_name)
            result = await db.execute(select(Tag).where(Tag.slug == tag_slug))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name, slug=tag_slug)
                db.add(tag)
                await db.flush()
            post.tags.append(tag)

    await db.commit()
    post = await get_post_with_relations(db, post_id=post.id)
    return PostDetailResponse.model_validate(post)


@router.delete("/{post_id}", response_model=MessageResponse)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除文章"""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")

    if post.author_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="无权限删除此文章")

    await db.delete(post)
    await db.commit()
    return MessageResponse(message="文章已删除")
