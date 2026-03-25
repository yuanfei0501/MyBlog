from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ============ 用户相关 ============
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    nickname: Optional[str] = Field(None, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50)


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(UserBase):
    id: int
    nickname: Optional[str]
    avatar: Optional[str]
    bio: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 认证相关 ============
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class CurrentUser(BaseModel):
    id: int
    username: str
    email: str
    nickname: Optional[str]
    avatar: Optional[str]
    role: str


# ============ 分类相关 ============
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    slug: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 标签相关 ============
class TagBase(BaseModel):
    name: str = Field(..., max_length=50)


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int
    slug: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 文章相关 ============
class PostBase(BaseModel):
    title: str = Field(..., max_length=200)
    content: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    category_id: Optional[int] = None
    is_top: bool = False


class PostCreate(PostBase):
    tags: List[str] = []
    status: str = "draft"


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    category_id: Optional[int] = None
    is_top: Optional[bool] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None


class PostListResponse(BaseModel):
    id: int
    title: str
    slug: str
    summary: Optional[str]
    cover_image: Optional[str]
    status: str
    view_count: int
    is_top: bool
    author: UserResponse
    category: Optional[CategoryResponse]
    tags: List[TagResponse]
    created_at: datetime
    published_at: Optional[datetime]

    class Config:
        from_attributes = True


class PostDetailResponse(PostListResponse):
    content: str
    updated_at: datetime


# ============ 评论相关 ============
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class CommentCreate(CommentBase):
    post_id: int
    parent_id: Optional[int] = None


class CommentResponse(CommentBase):
    id: int
    post_id: int
    post_title: Optional[str] = None
    user: UserResponse
    parent_id: Optional[int]
    status: str
    created_at: datetime
    replies: List["CommentResponse"] = []

    class Config:
        from_attributes = True


# ============ 媒体相关 ============
class MediaResponse(BaseModel):
    id: int
    filename: str
    filepath: str
    filesize: int
    mimetype: str
    uploader_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 通用响应 ============
class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    message: str
    success: bool = True
