import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { guest: true } },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue'), meta: { guest: true } },
  { path: '/onboarding', name: 'Onboarding', component: () => import('../views/Onboarding.vue'), meta: { auth: true } },
  { path: '/', name: 'Home', component: () => import('../views/Home.vue'), meta: { auth: true } },
  { path: '/welcome', name: 'Welcome', component: () => import('../views/Welcome.vue'), meta: { auth: true } },
  { path: '/profile', name: 'Profile', component: () => import('../views/Profile.vue'), meta: { auth: true } },
  { path: '/resources', name: 'Resources', component: () => import('../views/Resources.vue'), meta: { auth: true } },
  { path: '/learning-path', name: 'LearningPath', component: () => import('../views/LearningPath.vue'), meta: { auth: true } },
  { path: '/tutoring', name: 'Tutoring', component: () => import('../views/Tutoring.vue'), meta: { auth: true } },
  { path: '/assessment', name: 'Assessment', component: () => import('../views/Assessment.vue'), meta: { auth: true } },
  { path: '/knowledge-graph', name: 'KnowledgeGraph', component: () => import('../views/KnowledgeGraph.vue'), meta: { auth: true } },
  { path: '/library', name: 'Library', component: () => import('../views/Library.vue'), meta: { auth: true } },
  { path: '/settings', name: 'Settings', component: () => import('../views/Settings.vue'), meta: { auth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  // Restore session from token before deciding
  if (auth.token && !auth.user) {
    try {
      await auth.fetchUser()
    } catch {
      // Token invalid, proceed to guest page
    }
  }

  if (to.meta.guest && auth.isLoggedIn) {
    return next('/welcome')
  }

  if (to.meta.auth && !auth.isLoggedIn) {
    return next('/login')
  }

  if (auth.needsOnboarding && to.path !== '/onboarding' && to.path !== '/settings') {
    return next('/onboarding')
  }

  next()
})

export default router
