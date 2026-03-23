// 用户相关
export interface User {
  id: number
  username: string
  email: string
  nickname: string | null
  avatar: string | null
  bio: string | null
  role: string
  is_active: boolean
  created_at: string
}

export interface CurrentUser {
  id: number
  username: string
  email: string
  nickname: string | null
  avatar: string | null
  role: string
}

// 认证相关
export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

// 文章相关
export interface Post {
  id: number
  title: string
  slug: string
  content: string
  summary: string | null
  cover_image: string | null
  status: string
  view_count: number
  is_top: boolean
  author: User
  category: Category | null
  tags: Tag[]
  created_at: string
  updated_at: string
  published_at: string | null
}

export interface PostCreate {
  title: string
  content: string
  summary?: string
  cover_image?: string
  category_id?: number
  is_top?: boolean
  tags?: string[]
  status?: string
}

// 分类和标签
export interface Category {
  id: number
  name: string
  slug: string
  description: string | null
  parent_id: number | null
  created_at: string
}

export interface Tag {
  id: number
  name: string
  slug: string
  created_at: string
}

// 评论
export interface Comment {
  id: number
  content: string
  post_id: number
  user: User
  parent_id: number | null
  status: string
  created_at: string
  replies: Comment[]
}

export interface CommentCreate {
  content: string
  post_id: number
  parent_id?: number
}

// 媒体
export interface Media {
  id: number
  filename: string
  filepath: string
  filesize: number
  mimetype: string
  uploader_id: number
  created_at: string
}

// 通用响应
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface MessageResponse {
  message: string
  success: boolean
}

// 仪表盘数据
export interface DashboardData {
  posts: {
    total: number
    published: number
    draft: number
  }
  users: {
    total: number
  }
  comments: {
    total: number
    pending: number
  }
  media: {
    total: number
  }
  views: {
    recent_7_days: number
  }
  recent_posts: Array<{
    id: number
    title: string
    status: string
    view_count: number
    created_at: string
  }>
  recent_comments: Array<{
    id: number
    content: string
    status: string
    created_at: string
  }>
}
