import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import type {
  User,
  CurrentUser,
  LoginRequest,
  TokenResponse,
  Post,
  PostCreate,
  Category,
  Tag,
  Comment,
  CommentCreate,
  Media,
  PaginatedResponse,
  MessageResponse,
  DashboardData,
} from '@/types'

const api: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const { data } = await api.post<TokenResponse>('/auth/refresh', null, {
            params: { refresh_token: refreshToken },
          })
          localStorage.setItem('access_token', data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)
          error.config.headers.Authorization = `Bearer ${data.access_token}`
          return api.request(error.config)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

// 认证 API
export const authApi = {
  register: (data: LoginRequest & { email: string }) =>
    api.post<User>('/auth/register', data),
  login: (data: LoginRequest) =>
    api.post<TokenResponse>('/auth/login', data),
  getMe: () =>
    api.get<CurrentUser>('/auth/me'),
}

// 用户 API
export const userApi = {
  getProfile: () => api.get<User>('/users/profile'),
  updateProfile: (data: Partial<User>) => api.put<User>('/users/profile', data),
  list: (skip = 0, limit = 20) =>
    api.get<User[]>('/users', { params: { skip, limit } }),
  updateRole: (userId: number, role: string) =>
    api.put<MessageResponse>(`/users/${userId}/role`, null, { params: { role } }),
  toggleStatus: (userId: number) =>
    api.put<MessageResponse>(`/users/${userId}/status`),
}

// 文章 API
export const postApi = {
  list: (params: {
    page?: number
    page_size?: number
    category_id?: number
    tag_id?: number
    keyword?: string
    status?: string
  }) => api.get<PaginatedResponse<Post>>('/posts', { params }),
  get: (slug: string) => api.get<Post>(`/posts/${slug}`),
  getById: (id: number) => api.get<Post>(`/posts/detail/${id}`),
  create: (data: PostCreate) => api.post<Post>('/posts', data),
  update: (id: number, data: Partial<PostCreate>) =>
    api.put<Post>(`/posts/${id}`, data),
  delete: (id: number) => api.delete<MessageResponse>(`/posts/${id}`),
}

// 分类 API
export const categoryApi = {
  list: () => api.get<Category[]>('/categories'),
  create: (data: { name: string; description?: string }) =>
    api.post<Category>('/categories', data),
  update: (id: number, data: Partial<Category>) =>
    api.put<Category>(`/categories/${id}`, data),
  delete: (id: number) => api.delete<MessageResponse>(`/categories/${id}`),
}

// 标签 API
export const tagApi = {
  list: () => api.get<Tag[]>('/tags'),
  create: (data: { name: string }) => api.post<Tag>('/tags', data),
  delete: (id: number) => api.delete<MessageResponse>(`/tags/${id}`),
}

// 评论 API
export const commentApi = {
  listByPost: (postId: number) =>
    api.get<Comment[]>(`/comments/post/${postId}`),
  listAll: () =>
    api.get<Comment[]>('/comments/admin/all'),
  create: (data: CommentCreate) => api.post<Comment>('/comments', data),
  approve: (id: number) =>
    api.put<MessageResponse>(`/comments/${id}/approve`),
  delete: (id: number) =>
    api.delete<MessageResponse>(`/comments/${id}`),
}

// 媒体 API
export const mediaApi = {
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<Media>('/media/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  list: (page = 1, pageSize = 20) =>
    api.get<PaginatedResponse<Media>>('/media', { params: { page, page_size: pageSize } }),
  delete: (id: number) => api.delete<MessageResponse>(`/media/${id}`),
}

// 后台管理 API
export const adminApi = {
  getDashboard: () => api.get<DashboardData>('/admin/dashboard'),
}

// 关注 API
export const followApi = {
  follow: (userId: number) => api.post<MessageResponse>(`/follows/${userId}`),
  unfollow: (userId: number) => api.delete<MessageResponse>(`/follows/${userId}`),
  getStatus: (userId: number) => api.get<{ is_following: boolean }>(`/follows/status/${userId}`),
  getCount: (userId: number) => api.get<{ followers: number; following: number }>(`/follows/count/${userId}`),
  getFollowers: (userId: number) => api.get<User[]>(`/follows/followers/${userId}`),
  getFollowing: (userId: number) => api.get<User[]>(`/follows/following/${userId}`),
  getStats: (userId: number) => api.get<{ posts: number; followers: number; following: number }>(`/follows/stats/${userId}`),
}

export default api
