from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core import get_db
from app.models import Comment, Post, CommentStatus
from app.schemas import CommentCreate, CommentResponse, MessageResponse
from app.api.v1.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/comments", tags=["评论"])


async def build_comment_tree(comments: list[Comment]) -> list[Comment]:
    """构建评论树结构"""
    comment_dict = {c.id: c for c in comments}
    root_comments = []

    for comment in comments:
        if comment.parent_id:
            parent = comment_dict.get(comment.parent_id)
            if parent:
                if not hasattr(parent, "replies"):
                    parent.replies = []
                parent.replies.append(comment)
        else:
            root_comments.append(comment)

    return root_comments


@router.get("/post/{post_id}", response_model=list[CommentResponse])
async def list_post_comments(
    post_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取文章评论列表"""
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.user))
        .where(Comment.post_id == post_id, Comment.status == CommentStatus.APPROVED)
        .order_by(Comment.created_at.desc())
    )
    comments = result.scalars().all()
    return [CommentResponse.model_validate(c) for c in build_comment_tree(list(comments))]


@router.post("", response_model=CommentResponse, status_code=201)
async def create_comment(
    data: CommentCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发表评论"""
    # 检查文章是否存在
    result = await db.execute(select(Post).where(Post.id == data.post_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="文章不存在")

    # 检查父评论
    if data.parent_id:
        result = await db.execute(select(Comment).where(Comment.id == data.parent_id))
        parent = result.scalar_one_or_none()
        if not parent or parent.post_id != data.post_id:
            raise HTTPException(status_code=400, detail="父评论不存在")

    comment = Comment(
        content=data.content,
        post_id=data.post_id,
        user_id=current_user.id,
        parent_id=data.parent_id,
        status=CommentStatus.APPROVED,  # 直接通过，或改为 PENDING 需要审核
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    # 重新获取带用户信息的评论
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.user))
        .where(Comment.id == comment.id)
    )
    return CommentResponse.model_validate(result.scalar_one())


@router.put("/{comment_id}/approve", response_model=MessageResponse)
async def approve_comment(
    comment_id: int,
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """审核通过评论（管理员）"""
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    comment.status = CommentStatus.APPROVED
    await db.commit()
    return MessageResponse(message="评论已通过")


@router.delete("/{comment_id}", response_model=MessageResponse)
async def delete_comment(
    comment_id: int,
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除评论（管理员）"""
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    await db.delete(comment)
    await db.commit()
    return MessageResponse(message="评论已删除")
