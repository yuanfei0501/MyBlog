from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core import get_db
from app.models import User, UserRole
from app.schemas import UserUpdate, UserResponse, MessageResponse
from .auth import get_current_user, get_current_admin

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """获取个人资料"""
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新个人资料"""
    if update_data.nickname is not None:
        current_user.nickname = update_data.nickname
    if update_data.avatar is not None:
        current_user.avatar = update_data.avatar
    if update_data.bio is not None:
        current_user.bio = update_data.bio

    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表（管理员）"""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


@router.put("/{user_id}/role", response_model=MessageResponse)
async def update_user_role(
    user_id: int,
    role: UserRole,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """更新用户角色（管理员）"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.role = role
    await db.commit()
    return MessageResponse(message="角色更新成功")


@router.put("/{user_id}/status", response_model=MessageResponse)
async def toggle_user_status(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """切换用户状态（管理员）"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能禁用自己")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.is_active = not user.is_active
    await db.commit()
    return MessageResponse(message=f"用户已{'启用' if user.is_active else '禁用'}")
