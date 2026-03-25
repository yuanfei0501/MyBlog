from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core import get_db
from app.models import Comment, Post, CommentStatus
from app.schemas import CommentCreate, CommentResponse, MessageResponse, UserResponse
from app.api.v1.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/comments", tags=["评论"])


@router.get("/admin/all", response_model=list[CommentResponse])
async def list_all_comments(
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取所有评论（管理员）"""
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.user), selectinload(Comment.post))
        .order_by(Comment.created_at.desc())
    )
    comments = result.scalars().all()
    # 返回扁平列表，方便管理
    return [
        CommentResponse(
            id=c.id,
            content=c.content,
            post_id=c.post_id,
            post_title=c.post.title if c.post else None,
            user=UserResponse.model_validate(c.user),
            parent_id=c.parent_id,
            status=c.status.value,
            created_at=c.created_at,
            replies=[]
        )
        for c in comments
    ]


def build_comment_response_tree(comments: list[Comment]) -> list[dict]:
    """构建评论树结构，返回字典列表"""
    # 先将所有评论转换为字典
    comment_map = {}
    for c in comments:
        comment_map[c.id] = {
            "id": c.id,
            "content": c.content,
            "post_id": c.post_id,
            "user": UserResponse.model_validate(c.user).model_dump(),
            "parent_id": c.parent_id,
            "status": c.status.value,
            "created_at": c.created_at,
            "replies": []
        }

    # 构建树结构
    root_comments = []
    for c in comments:
        if c.parent_id and c.parent_id in comment_map:
            comment_map[c.parent_id]["replies"].append(comment_map[c.id])
        else:
            root_comments.append(comment_map[c.id])

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
    return build_comment_response_tree(list(comments))


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

    # 管理员评论直接通过，普通用户需要审核
    from app.models import UserRole
    comment_status = CommentStatus.APPROVED if current_user.role == UserRole.ADMIN else CommentStatus.PENDING

    comment = Comment(
        content=data.content,
        post_id=data.post_id,
        user_id=current_user.id,
        parent_id=data.parent_id,
        status=comment_status,
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
    new_comment = result.scalar_one()
    # 手动构建响应数据，避免 SQLAlchemy 懒加载问题
    from app.schemas import UserResponse
    return CommentResponse(
        id=new_comment.id,
        content=new_comment.content,
        post_id=new_comment.post_id,
        user=UserResponse.model_validate(new_comment.user),
        parent_id=new_comment.parent_id,
        status=new_comment.status.value,
        created_at=new_comment.created_at,
        replies=[]
    )


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
