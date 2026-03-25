import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // 博客前台
    {
      path: '/',
      component: () => import('@/views/blog/Layout.vue'),
      children: [
        {
          path: '',
          name: 'Home',
          component: () => import('@/views/blog/Home.vue'),
        },
        {
          path: 'post/:slug',
          name: 'Post',
          component: () => import('@/views/blog/Post.vue'),
        },
        {
          path: 'category/:slug',
          name: 'Category',
          component: () => import('@/views/blog/Category.vue'),
        },
        {
          path: 'tag/:slug',
          name: 'Tag',
          component: () => import('@/views/blog/Tag.vue'),
        },
        {
          path: 'search',
          name: 'Search',
          component: () => import('@/views/blog/Search.vue'),
        },
      ],
    },
    // 登录/注册
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/blog/Login.vue'),
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/blog/Register.vue'),
    },
    // 后台管理 - 仅管理员可访问
    {
      path: '/admin',
      component: () => import('@/views/admin/Layout.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/admin/Dashboard.vue'),
        },
        {
          path: 'posts',
          name: 'PostList',
          component: () => import('@/views/admin/PostList.vue'),
        },
        {
          path: 'posts/new',
          name: 'PostNew',
          component: () => import('@/views/admin/PostEditor.vue'),
        },
        {
          path: 'posts/:id/edit',
          name: 'PostEdit',
          component: () => import('@/views/admin/PostEditor.vue'),
        },
        {
          path: 'categories',
          name: 'Categories',
          component: () => import('@/views/admin/Categories.vue'),
        },
        {
          path: 'tags',
          name: 'Tags',
          component: () => import('@/views/admin/Tags.vue'),
        },
        {
          path: 'comments',
          name: 'Comments',
          component: () => import('@/views/admin/Comments.vue'),
        },
        {
          path: 'media',
          name: 'Media',
          component: () => import('@/views/admin/Media.vue'),
        },
        {
          path: 'users',
          name: 'Users',
          component: () => import('@/views/admin/Users.vue'),
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/admin/Settings.vue'),
        },
      ],
    },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  // 等待用户信息加载完成
  await userStore.init()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresAdmin && !userStore.isAdmin) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
