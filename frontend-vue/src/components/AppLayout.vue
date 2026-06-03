<template>
  <div class="app-layout">
    <aside class="sidebar">
      <!-- 上卡片：导航菜单 + 知识盲盒 -->
      <div class="sidebar-card sidebar-nav-card">
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

        <!-- 画像引导 -->
        <div v-if="!store.hasProfile" class="onboard-hint" @click="$router.push('/onboarding')">
          <span class="onboard-hint-icon">📝</span>
          <span class="onboard-hint-text">完成画像引导</span>
          <span class="onboard-hint-arrow">→</span>
        </div>

        <!-- 知识盲盒 -->
        <KnowledgeBlindBox />
      </div>

      <!-- 下卡片：用户信息 -->
      <div class="sidebar-card sidebar-user-card">
        <!-- 顶部装饰线 -->
        <div class="user-card-ornament"></div>

        <!-- 头像 -->
        <div class="user-card-avatar-wrap" @click="goSettings">
          <div class="user-card-avatar">
            <img v-if="auth.user?.avatar" :src="auth.user.avatar" />
            <template v-else>{{ auth.user?.username?.charAt(0)?.toUpperCase() }}</template>
          </div>
        </div>

        <!-- 用户名 -->
        <div class="user-card-name" @click="goSettings">{{ auth.user?.username }}</div>

        <!-- 等级徽章 -->
        <div class="user-card-level-badge" v-if="kb.level">
          {{ LEVEL[kb.level] || kb.level }}
        </div>

        <!-- 学习概况 -->
        <div class="user-card-stats">
          <div class="user-stat-item">
            <span class="user-stat-val">{{ profileStats.resourceCount }}</span>
            <span class="user-stat-lbl">资源</span>
          </div>
          <div class="user-stat-div"></div>
          <div class="user-stat-item">
            <span class="user-stat-val">{{ profileStats.pathCount }}</span>
            <span class="user-stat-lbl">路径</span>
          </div>
          <div class="user-stat-div"></div>
          <div class="user-stat-item">
            <span class="user-stat-val">v{{ store.profileVersion || 0 }}</span>
            <span class="user-stat-lbl">画像</span>
          </div>
        </div>

        <!-- 弱项标签 -->
        <div class="user-card-weak" v-if="kb.weak_points?.length">
          <span class="weak-label">薄弱项</span>
          <span class="weak-tag" v-for="w in kb.weak_points.slice(0, 2)" :key="w">{{ w }}</span>
        </div>

        <!-- 操作 -->
        <div class="user-card-actions">
          <span class="user-action-btn" @click="goSettings">⚙️ 设置</span>
          <span class="user-action-btn logout" @click.stop="handleLogout">退出</span>
        </div>

        <!-- 底部装饰线 -->
        <div class="user-card-ornament bottom"></div>
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

const profileStats = computed(() => {
  const p = store.profile || {}
  return {
    resourceCount: Array.isArray(p.resources) ? p.resources.length : 0,
    pathCount: Array.isArray(p.learning_paths) ? p.learning_paths.length : 0,
  }
})

const allMenuItems = [
  { path: '/welcome', icon: '📚', label: '系统介绍' },
  { path: '/', icon: '🏠', label: ' 学习仪表盘' },
  { path: '/profile', icon: '🧠', label: ' 学习画像' },
  { path: '/resources', icon: '📄', label: ' 资源生成' },
  { path: '/learning-path', icon: '🗺️', label: ' 路径规划' },
  { path: '/library', icon: '📚', label: ' 资源库' },
  { path: '/knowledge-graph', icon: '🕸️', label: ' 知识图谱' },
  { path: '/assessment', icon: '📊', label: ' 学习评估' },
]

const lockedPages = ['/resources', '/learning-path', '/assessment', '/library', '/knowledge-graph']

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
/* 侧边栏卡片 */
.sidebar-card {
  background: linear-gradient(180deg, #4A2E20 0%, #5D3A2C 40%, #523527 100%);
  border-radius: 10px;
  overflow: hidden;
}

.sidebar-nav-card {
  flex: 2;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.sidebar-user-card {
  flex: 1;
  padding: 0.5rem 0.7rem;
  min-height: 0;
}

/* 侧边栏头部 */
.sidebar-header {
  padding: 1.6rem 1.2rem 1rem;
  text-align: center;
  flex-shrink: 0;
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
  background: rgba(255, 254, 249, 0.05) !important;
  transition: all 0.2s;
}

.sidebar-body :deep(.el-menu-item:hover) {
  color: #E0D3C0 !important;
  background: rgba(200, 162, 92, 0.12) !important;
}

.sidebar-body :deep(.el-menu-item.is-active) {
  color: #D4B86C !important;
  background: rgba(200, 162, 92, 0.18) !important;
  font-weight: 600;
}

.nav-icon {
  display: inline-block;
  width: 1.6rem;
  text-align: center;
  margin-right: 4px;
  font-size: 1.15rem;
}

.nav-label {
  font-size: 0.95rem;
}


/* 画像引导提示 */
.onboard-hint {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.7rem;
  margin: 0 0.7rem 0.5rem;
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

/* 用户卡片 */
.sidebar-user-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-evenly;
  text-align: center;
  padding: 0.5rem 0.9rem;
  gap: 0.25rem;
}

.user-card-ornament {
  width: 60%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(200, 162, 92, 0.35), transparent);
  flex-shrink: 0;
}

.user-card-avatar-wrap {
  cursor: pointer;
}

.user-card-avatar {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: linear-gradient(135deg, #C8A25C, #B8934F);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 2.4rem;
  color: #FFFEF9;
  overflow: hidden;
  border: 2px solid rgba(200, 162, 92, 0.3);
  transition: border-color 0.2s;
}

.user-card-avatar-wrap:hover .user-card-avatar {
  border-color: rgba(200, 162, 92, 0.6);
}

.user-card-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-card-name {
  font-size: 0.92rem;
  font-weight: 700;
  color: #F0E6D8;
  cursor: pointer;
  transition: color 0.2s;
}
.user-card-name:hover {
  color: #D4B86C;
}

.user-card-level-badge {
  font-size: 0.68rem;
  font-weight: 600;
  color: #D4B86C;
  background: rgba(200, 162, 92, 0.15);
  border: 1px solid rgba(200, 162, 92, 0.25);
  padding: 0.12rem 0.7rem;
  border-radius: 10px;
  letter-spacing: 0.06em;
}

/* 学习概况 */
.user-card-stats {
  display: flex;
  align-items: center;
  gap: 0;
  width: 100%;
  padding: 0.3rem 0;
}

.user-stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.05rem;
}

.user-stat-val {
  font-size: 1.05rem;
  font-weight: 700;
  color: #D4B86C;
}

.user-stat-lbl {
  font-size: 0.66rem;
  color: #B8A088;
  font-weight: 500;
}

.user-stat-div {
  width: 1px;
  height: 20px;
  background: rgba(200, 162, 92, 0.15);
  flex-shrink: 0;
}

/* 弱项标签 */
.user-card-weak {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  flex-wrap: wrap;
  justify-content: center;
}

.weak-label {
  font-size: 0.64rem;
  color: #B8A088;
}

.weak-tag {
  font-size: 0.62rem;
  background: rgba(114, 47, 55, 0.15);
  color: #C08070;
  padding: 0.08rem 0.4rem;
  border-radius: 3px;
}

/* 操作按钮 */
.user-card-actions {
  display: flex;
  gap: 0.5rem;
  width: 100%;
  padding-top: 0.2rem;
}

.user-action-btn {
  flex: 1;
  font-size: 0.72rem;
  color: #B8A088;
  padding: 0.3rem 0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(255, 254, 249, 0.04);
}

.user-action-btn:hover {
  color: #D4B86C;
  background: rgba(200, 162, 92, 0.1);
}

.user-action-btn.logout:hover {
  color: #C08070;
  background: rgba(114, 47, 55, 0.12);
}
</style>
