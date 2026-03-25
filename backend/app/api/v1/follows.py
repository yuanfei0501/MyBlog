from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.core import get_db
from app.models import User, Follow, Post, PostStatus
from app.schemas import MessageResponse, UserResponse
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/follows", tags=["关注"])


@router.post("/{user_id}", response_model=MessageResponse)
async def follow_user(
    user_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """关注用户"""
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="不能关注自己")

    # 检查用户是否存在
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 检查是否已关注
    result = await db.execute(
        select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == user_id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="已经关注了该用户")

    # 创建关注
    follow = Follow(follower_id=current_user.id, following_id=user_id)
    db.add(follow)
    await db.commit()

    return MessageResponse(message="关注成功")


@router.delete("/{user_id}", response_model=MessageResponse)
async def unfollow_user(
    user_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """取消关注"""
    result = await db.execute(
        select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == user_id,
        )
    )
    follow = result.scalar_one_or_none()
    if not follow:
        raise HTTPException(status_code=400, detail="未关注该用户")

    await db.delete(follow)
    await db.commit()

    return MessageResponse(message="取消关注成功")


@router.get("/status/{user_id}")
async def get_follow_status(
    user_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取关注状态"""
    result = await db.execute(
        select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == user_id,
        )
    )
    is_following = result.scalar_one_or_none() is not None
    return {"is_following": is_following}


@router.get("/count/{user_id}")
async def get_follow_count(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取用户关注/粉丝数"""
    # 粉丝数（有多少人关注我）
    followers_count = await db.execute(
        select(func.count(Follow.id)).where(Follow.following_id == user_id)
    )
    # 关注数（我关注了多少人）
    following_count = await db.execute(
        select(func.count(Follow.id)).where(Follow.follower_id == user_id)
    )

    return {
        "followers": followers_count.scalar(),
        "following": following_count.scalar(),
    }


@router.get("/followers/{user_id}", response_model=list[UserResponse])
async def get_followers(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取用户的粉丝列表"""
    result = await db.execute(
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
        .order_by(Follow.created_at.desc())
    )
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]


@router.get("/following/{user_id}", response_model=list[UserResponse])
async def get_following(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取用户关注的列表"""
    result = await db.execute(
        select(User)
        .join(Follow, Follow.following_id == User.id)
        .where(Follow.follower_id == user_id)
        .order_by(Follow.created_at.desc())
    )
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]


@router.get("/stats/{user_id}")
async def get_user_stats(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取用户统计信息"""
    # 文章数
    posts_count = await db.execute(
        select(func.count(Post.id)).where(
            Post.author_id == user_id,
            Post.status == PostStatus.PUBLISHED
        )
    )
    # 粉丝数
    followers_count = await db.execute(
        select(func.count(Follow.id)).where(Follow.following_id == user_id)
    )
    # 关注数
    following_count = await db.execute(
        select(func.count(Follow.id)).where(Follow.follower_id == user_id)
    )

    return {
        "posts": posts_count.scalar(),
        "followers": followers_count.scalar(),
        "following": following_count.scalar(),
    }
