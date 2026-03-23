from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.core import get_db
from app.models import User, Post, Comment, Media, PostStatus, CommentStatus
from app.api.v1.auth import get_current_admin

router = APIRouter(prefix="/admin", tags=["后台管理"])


@router.get("/dashboard")
async def get_dashboard(
    current_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取仪表盘统计数据"""
    # 文章统计
    total_posts = (await db.execute(select(func.count(Post.id)))).scalar()
    published_posts = (await db.execute(
        select(func.count(Post.id)).where(Post.status == PostStatus.PUBLISHED)
    )).scalar()
    draft_posts = (await db.execute(
        select(func.count(Post.id)).where(Post.status == PostStatus.DRAFT)
    )).scalar()

    # 用户统计
    total_users = (await db.execute(select(func.count(User.id)))).scalar()

    # 评论统计
    total_comments = (await db.execute(select(func.count(Comment.id)))).scalar()
    pending_comments = (await db.execute(
        select(func.count(Comment.id)).where(Comment.status == CommentStatus.PENDING)
    )).scalar()

    # 媒体统计
    total_media = (await db.execute(select(func.count(Media.id)))).scalar()

    # 最近 7 天访问量（这里用文章阅读量模拟）
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_views = (await db.execute(
        select(func.sum(Post.view_count)).where(Post.published_at >= seven_days_ago)
    )).scalar() or 0

    # 最新文章
    recent_posts_result = await db.execute(
        select(Post)
        .order_by(Post.created_at.desc())
        .limit(5)
    )
    recent_posts = [
        {
            "id": p.id,
            "title": p.title,
            "status": p.status.value,
            "view_count": p.view_count,
            "created_at": p.created_at.isoformat(),
        }
        for p in recent_posts_result.scalars().all()
    ]

    # 最新评论
    recent_comments_result = await db.execute(
        select(Comment)
        .order_by(Comment.created_at.desc())
        .limit(5)
    )
    recent_comments = [
        {
            "id": c.id,
            "content": c.content[:50] + "..." if len(c.content) > 50 else c.content,
            "status": c.status.value,
            "created_at": c.created_at.isoformat(),
        }
        for c in recent_comments_result.scalars().all()
    ]

    return {
        "posts": {
            "total": total_posts,
            "published": published_posts,
            "draft": draft_posts,
        },
        "users": {
            "total": total_users,
        },
        "comments": {
            "total": total_comments,
            "pending": pending_comments,
        },
        "media": {
            "total": total_media,
        },
        "views": {
            "recent_7_days": recent_views,
        },
        "recent_posts": recent_posts,
        "recent_comments": recent_comments,
    }
