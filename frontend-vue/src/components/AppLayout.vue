<template>
  <div class="app-layout">
    <aside class="sidebar">
      <!-- 顶部：图书馆标识 -->
      <div class="sidebar-header">
        <div class="sidebar-logo-row">
          <span class="logo-icon">📚</span>
          <span class="logo-divider">|</span>
          <span class="logo-label">LIBRARY</span>
        </div>
        <div class="sidebar-system-name">多智能体学习系统</div>
        <div class="sidebar-version">v1.0 · DeepSeek AI</div>
      </div>

      <!-- 金色装饰线 -->
      <div class="sidebar-accent-line"></div>

      <!-- 导航菜单 -->
      <div class="sidebar-body">
        <el-menu
          :default-active="activeMenu"
          @select="handleMenuSelect"
          background-color="transparent"
          text-color="#C8B89A"
          active-text-color="#D4B86C"
        >
          <el-menu-item
            v-for="item in visibleMenuItems"
            :key="item.path"
            :index="item.path"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 底部分隔 -->
      <div class="sidebar-accent-line" style="margin-top: auto;"></div>

      <!-- 底部区域 -->
      <div class="sidebar-footer">
        <!-- 知识盲盒 -->
        <KnowledgeBlindBox />

        <!-- 画像引导 -->
        <div v-if="!store.hasProfile" class="onboard-hint" @click="$router.push('/onboarding')">
          <span class="onboard-hint-icon">📝</span>
          <span class="onboard-hint-text">完成画像引导</span>
          <span class="onboard-hint-arrow">→</span>
        </div>

        <!-- 用户卡片 -->
        <div v-if="auth.user" class="user-mini-card" @click="goSettings">
          <div class="user-mini-avatar">
            <img v-if="auth.user.avatar" :src="auth.user.avatar" />
            <template v-else>{{ auth.user.username.charAt(0).toUpperCase() }}</template>
          </div>
          <div class="user-mini-info">
            <div class="user-mini-name">{{ auth.user.username }}</div>
            <div class="user-mini-level" v-if="kb.level">{{ LEVEL[kb.level] || kb.level }}</div>
          </div>
          <span class="user-mini-logout" @click.stop="handleLogout" title="退出登录">退出</span>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <router-view />
    </main>

    <!-- 悬浮辅导助手 -->
    <FloatingTutor />
  </div>
</template>

<script setup>
import { computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStudentStore } from '../stores/student'
import { useAuthStore } from '../stores/auth'
import FloatingTutor from './FloatingTutor.vue'
import KnowledgeBlindBox from './KnowledgeBlindBox.vue'

const router = useRouter()
const route = useRoute()
const store = useStudentStore()
const auth = useAuthStore()

const activeMenu = computed(() => route.path)

const LEVEL = { beginner: '入门级', intermediate: '中级', advanced: '高级' }
const kb = computed(() => store.profile?.knowledge_base || {})

const allMenuItems = [
  { path: '/', icon: '🏠', label: '学习仪表盘' },
  { path: '/profile', icon: '🧠', label: '学习画像' },
  { path: '/resources', icon: '📄', label: '资源生成' },
  { path: '/learning-path', icon: '🗺️', label: '路径规划' },
  { path: '/library', icon: '📚', label: '资源库' },
  { path: '/assessment', icon: '📊', label: '学习评估' },
]

const lockedPages = ['/resources', '/learning-path', '/assessment', '/library']

const visibleMenuItems = computed(() => {
  if (store.hasProfile) return allMenuItems
  return allMenuItems.filter(i => !lockedPages.includes(i.path))
})

function handleMenuSelect(path) {
  router.push(path)
}

function goSettings() {
  router.push('/settings')
}

function handleLogout() {
  auth.logout()
  store.profile = null
  store.currentStudentId = null
  router.push('/login')
}

onMounted(() => {
  if (auth.studentId) {
    store.syncWithUser(auth.studentId)
  }
})

watch(() => route.path, (path) => {
  if (!store.hasProfile && lockedPages.includes(path)) {
    router.push('/profile')
  }
})
</script>

<style scoped>
/* 侧边栏头部 */
.sidebar-header {
  padding: 1.6rem 1.2rem 1rem;
  text-align: center;
}

.sidebar-logo-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.logo-icon {
  font-size: 1.8rem;
}

.logo-divider {
  color: rgba(200, 162, 92, 0.3);
  font-weight: 200;
  font-size: 1.2rem;
}

.logo-label {
  font-size: 0.65rem;
  letter-spacing: 0.2em;
  color: rgba(200, 162, 92, 0.5);
  font-weight: 500;
}

.sidebar-system-name {
  font-size: 0.92rem;
  font-weight: 700;
  color: #E0D3C0;
  letter-spacing: 0.04em;
}

.sidebar-version {
  font-size: 0.68rem;
  color: rgba(184, 160, 136, 0.6);
  margin-top: 0.2rem;
}

/* 金色装饰线 */
.sidebar-accent-line {
  height: 1px;
  margin: 0 1rem;
  background: linear-gradient(90deg, transparent, rgba(200, 162, 92, 0.3), transparent);
}

/* 导航区 */
.sidebar-body {
  flex: 1;
  padding: 0.6rem 0.6rem;
  overflow-y: auto;
}

/* 导航项样式（覆盖全局） */
.sidebar-body :deep(.el-menu) {
  border-right: none !important;
}

.sidebar-body :deep(.el-menu-item) {
  border-radius: 6px;
  margin: 3px 4px;
  height: 48px !important;
  line-height: 48px !important;
  font-size: 0.92rem !important;
  color: #C8B89A !important;
  transition: all 0.2s;
}

.sidebar-body :deep(.el-menu-item:hover) {
  color: #E0D3C0 !important;
  background: rgba(200, 162, 92, 0.08) !important;
}

.sidebar-body :deep(.el-menu-item.is-active) {
  color: #D4B86C !important;
  background: rgba(200, 162, 92, 0.15) !important;
  font-weight: 600;
}

.nav-icon {
  display: inline-block;
  width: 1.6rem;
  text-align: center;
  margin-right: 4px;
  font-size: 1rem;
}

.nav-label {
  font-size: 0.88rem;
}

/* 底部区 */
.sidebar-footer {
  padding: 0.6rem 0.8rem 0.8rem;
}

/* 画像引导提示 */
.onboard-hint {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.7rem;
  margin-bottom: 0.5rem;
  border-radius: 6px;
  background: rgba(200, 162, 92, 0.1);
  border: 1px solid rgba(200, 162, 92, 0.15);
  cursor: pointer;
  transition: all 0.2s;
}

.onboard-hint:hover {
  background: rgba(200, 162, 92, 0.18);
  border-color: rgba(200, 162, 92, 0.3);
}

.onboard-hint-icon {
  font-size: 0.9rem;
}

.onboard-hint-text {
  flex: 1;
  font-size: 0.78rem;
  color: #D4B86C;
  font-weight: 500;
}

.onboard-hint-arrow {
  color: rgba(212, 184, 108, 0.5);
  font-size: 0.75rem;
}

/* 用户迷你卡片 */
.user-mini-card {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.user-mini-card:hover {
  background: rgba(255, 254, 249, 0.06);
}

.user-mini-avatar {
  width: 34px;
  height: 34px;
  border-radius: 6px;
  background: linear-gradient(135deg, #C8A25C, #B8934F);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
  color: #FFFEF9;
  flex-shrink: 0;
  overflow: hidden;
}

.user-mini-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-mini-info {
  flex: 1;
  min-width: 0;
}

.user-mini-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: #E0D3C0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-mini-level {
  font-size: 0.7rem;
  color: #B8A088;
}

.user-mini-logout {
  font-size: 0.7rem;
  color: rgba(184, 160, 136, 0.5);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.user-mini-logout:hover {
  color: #E0B860;
  background: rgba(200, 162, 92, 0.12);
}
</style>
