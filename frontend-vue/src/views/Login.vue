<template>
  <div class="login-root">
    <!-- 左侧：图书馆氛围 -->
    <div class="login-brand">
      <!-- 装饰木纹线条 -->
      <div class="brand-ornament-top"></div>

      <div class="brand-inner">
        <!-- 主视觉：书 + 灯 -->
        <div class="brand-visual">
          <div class="visual-books">
            <span class="book book-1">📕</span>
            <span class="book book-2">📗</span>
            <span class="book book-3">📘</span>
            <span class="book book-4">📙</span>
          </div>
          <div class="visual-lamp">🪔</div>
        </div>

        <h1 class="brand-title">多智能体学习系统</h1>

        <!-- 金色装饰线 -->
        <div class="brand-rule">
          <span class="rule-line"></span>
          <span class="rule-diamond">◆</span>
          <span class="rule-line"></span>
        </div>

        <p class="brand-desc">
          六个专业 AI Agent 协作，从画像构建到资源生成、路径规划、智能辅导，打造完整的个性化学习闭环。
        </p>

        <!-- 特性标签 -->
        <div class="brand-tags">
          <span class="brand-tag">6 维学习画像</span>
          <span class="brand-tag">多模态资源生成</span>
          <span class="brand-tag">自适应辅导</span>
          <span class="brand-tag">动态路径规划</span>
        </div>

        <p class="brand-quote">"每个人都有自己的学习节奏，让 AI 为你找到最适合的那一条路。"</p>
      </div>

      <div class="brand-ornament-bottom"></div>
    </div>

    <!-- 右侧：登录表单 -->
    <div class="login-form-side">
      <div class="form-card">
        <!-- 选项卡 -->
        <div class="form-tabs">
          <span class="form-tab active">账号登录</span>
          <router-link to="/register" class="form-tab link">注册新账号</router-link>
        </div>

        <p class="form-subtitle">欢迎回来，请登录你的账号</p>

        <el-form @keyup.enter="handleLogin">
          <div class="input-group">
            <label class="input-label">用户名</label>
            <el-input
              v-model="username"
              placeholder="请输入用户名"
              size="large"
              class="custom-input"
            >
              <template #prefix>
                <span class="input-icon">👤</span>
              </template>
            </el-input>
          </div>

          <div class="input-group">
            <label class="input-label">密码</label>
            <el-input
              v-model="password"
              type="password"
              placeholder="请输入密码"
              size="large"
              show-password
              class="custom-input"
            >
              <template #prefix>
                <span class="input-icon">🔒</span>
              </template>
            </el-input>
          </div>

          <div class="input-group">
            <label class="input-label">验证码</label>
            <div class="code-row">
              <el-input
                v-model="captchaInput"
                placeholder="输入右侧4位验证码"
                size="large"
                maxlength="4"
                class="code-input"
              >
                <template #prefix>
                  <span class="input-icon">🔑</span>
                </template>
              </el-input>
              <div class="captcha-display" @click="refreshCaptcha" title="点击刷新验证码">
                <span class="captcha-text">{{ captchaText }}</span>
                <span class="captcha-refresh">↻</span>
              </div>
            </div>
          </div>

          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-submit-btn"
          >
            登 录 账 号
          </el-button>
        </el-form>
      </div>

      <p class="login-footer-text">Powered by DeepSeek AI · 6 Agent Architecture</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getCaptcha } from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const captchaInput = ref('')
const captchaId = ref('')
const captchaText = ref('')
const loading = ref(false)

async function refreshCaptcha() {
  try {
    const data = await getCaptcha()
    captchaId.value = data.captcha_id
    captchaText.value = data.captcha_text
    captchaInput.value = ''
  } catch {
    captchaText.value = '----'
  }
}

onMounted(refreshCaptcha)

async function handleLogin() {
  if (!username.value.trim() || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  if (!captchaInput.value.trim() || captchaInput.value.length !== 4) {
    ElMessage.warning('请输入4位验证码')
    return
  }
  loading.value = true
  try {
    await auth.login(username.value.trim(), password.value, captchaId.value, captchaInput.value.trim())
    ElMessage.success('登录成功')
    router.push('/welcome')
  } catch (e) {
    const msg = e.response?.data?.detail
    ElMessage({ message: Array.isArray(msg) ? msg.map(m => m.msg).join('；') : (msg || '登录失败'), type: 'error', duration: 4000 })
    refreshCaptcha()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ===== 整体布局 ===== */
.login-root {
  min-height: 100vh;
  display: flex;
}

/* ===== 左侧品牌区 ===== */
.login-brand {
  width: 44%;
  background: linear-gradient(170deg, #2C1A10 0%, #3E2723 25%, #4A2E20 60%, #5D3A2C 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 3rem;
  position: relative;
  overflow: hidden;
}

/* 木纹纹理叠加 */
.login-brand::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    repeating-linear-gradient(
      2deg,
      transparent,
      transparent 3px,
      rgba(255,255,255,0.008) 3px,
      rgba(255,255,255,0.008) 6px
    ),
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 40px,
      rgba(0,0,0,0.03) 40px,
      rgba(0,0,0,0.03) 41px
    );
  pointer-events: none;
}

/* 装饰光晕 */
.login-brand::after {
  content: '';
  position: absolute;
  top: -20%;
  right: -30%;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(200, 162, 92, 0.06) 0%, transparent 70%);
  pointer-events: none;
}

/* 顶部装饰条 */
.brand-ornament-top {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent 0%, #C8A25C 20%, #D4B86C 50%, #C8A25C 80%, transparent 100%);
}

.brand-ornament-bottom {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent 0%, #C8A25C 20%, #D4B86C 50%, #C8A25C 80%, transparent 100%);
}

.brand-inner {
  position: relative;
  z-index: 1;
  max-width: 440px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

/* 主视觉：书本 + 灯 */
.brand-visual {
  position: relative;
  margin-bottom: 2rem;
}

.visual-books {
  display: flex;
  gap: 0.3rem;
  justify-content: center;
}

.book {
  font-size: 2.8rem;
  display: block;
  transition: transform 0.3s;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
}

.book-1 { transform: rotate(-8deg) translateY(0); }
.book-2 { transform: rotate(-3deg) translateY(-6px); }
.book-3 { transform: rotate(2deg) translateY(-4px); }
.book-4 { transform: rotate(7deg) translateY(2px); }

.visual-lamp {
  position: absolute;
  top: -2.2rem;
  right: -2rem;
  font-size: 2.5rem;
  filter: drop-shadow(0 0 12px rgba(212, 184, 108, 0.5));
  animation: lampGlow 3s ease-in-out infinite;
}

@keyframes lampGlow {
  0%, 100% { filter: drop-shadow(0 0 12px rgba(212, 184, 108, 0.4)); }
  50% { filter: drop-shadow(0 0 22px rgba(212, 184, 108, 0.7)); }
}

.brand-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: #F0E6D8;
  margin: 0;
  letter-spacing: 0.04em;
  line-height: 1.3;
}

/* 金色装饰线 */
.brand-rule {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 1.2rem 0;
  width: 100%;
  max-width: 280px;
}

.rule-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, #C8A25C, transparent);
}

.rule-diamond {
  color: #C8A25C;
  font-size: 0.5rem;
}

.brand-desc {
  color: #A89880;
  font-size: 0.9rem;
  line-height: 1.8;
  margin: 0 0 1.5rem 0;
  max-width: 380px;
}

/* 特性标签 */
.brand-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.brand-tag {
  font-size: 0.72rem;
  color: #B8A088;
  border: 1px solid rgba(184, 160, 136, 0.3);
  border-radius: 3px;
  padding: 0.25rem 0.7rem;
  letter-spacing: 0.04em;
}

.brand-quote {
  color: #8B7A65;
  font-size: 0.85rem;
  font-style: italic;
  line-height: 1.7;
  margin: 0;
}

/* ===== 右侧表单区 ===== */
.login-form-side {
  width: 56%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #FBF7F0 0%, #F5EDE0 100%);
  padding: 3rem;
  position: relative;
}

/* 右侧装饰竖线 */
.login-form-side::before {
  content: '';
  position: absolute;
  left: 0;
  top: 15%;
  bottom: 15%;
  width: 1px;
  background: linear-gradient(180deg, transparent, rgba(200, 162, 92, 0.3), transparent);
}

.form-card {
  width: 100%;
  max-width: 420px;
  background: #FFFEF9;
  border-radius: 8px;
  padding: 2.5rem 2.5rem 2rem;
  box-shadow: 0 2px 24px rgba(60, 48, 40, 0.08);
  border: 1px solid #E8E0D5;
}

.form-tabs {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 0.8rem;
}

.form-tab {
  font-size: 0.95rem;
  color: #A89880;
  text-decoration: none;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  cursor: pointer;
}

.form-tab.active {
  color: #3C3028;
  font-weight: 700;
  border-bottom-color: #C8A25C;
  font-size: 1.25rem;
}

.form-tab.link {
  font-size: 0.88rem;
  align-self: flex-end;
  margin-left: auto;
}

.form-tab.link:hover {
  color: #C8A25C;
}

.form-subtitle {
  color: #A89880;
  font-size: 0.85rem;
  margin: 0 0 2rem 0;
  padding-bottom: 1.2rem;
  border-bottom: 1px solid #E8E0D5;
}

.input-group {
  margin-bottom: 1.3rem;
}

.input-label {
  display: block;
  font-size: 0.78rem;
  font-weight: 600;
  color: #5C4F42;
  margin-bottom: 0.4rem;
}

.custom-input :deep(.el-input__wrapper) {
  border-radius: 6px;
  box-shadow: 0 0 0 1px #D4C4A8;
  padding-left: 0.3rem;
  background: #FBF7F0;
  transition: all 0.2s;
}

.custom-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(200, 162, 92, 0.5);
  background: #FFFEF9;
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(200, 162, 92, 0.35);
  background: #FFFEF9;
}

.input-icon {
  font-size: 1rem;
}

.code-row {
  display: flex;
  gap: 0.6rem;
}

.code-input {
  flex: 1;
}

.captcha-display {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: linear-gradient(135deg, #F5EDE0, #EDE5D5);
  border: 1.5px dashed rgba(200, 162, 92, 0.4);
  border-radius: 6px;
  padding: 0 1rem;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s;
  min-width: 115px;
  justify-content: center;
}

.captcha-display:hover {
  background: linear-gradient(135deg, #EDE0D0, #E0D4C0);
  border-color: rgba(200, 162, 92, 0.6);
}

.captcha-text {
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: 0.3em;
  color: #3C3028;
  font-family: 'Georgia', 'Courier New', serif;
  font-style: italic;
}

.captcha-refresh {
  font-size: 1.1rem;
  color: #C8A25C;
}

.login-submit-btn {
  width: 100%;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  height: 48px;
  margin-top: 0.8rem;
  background: linear-gradient(135deg, #5D3A2C, #4A2E20);
  border: none;
  transition: all 0.25s;
}

.login-submit-btn:hover {
  background: linear-gradient(135deg, #4A2E20, #3E2723);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(60, 48, 40, 0.25);
}

.login-footer-text {
  margin-top: 2rem;
  font-size: 0.72rem;
  color: #B8A088;
  letter-spacing: 0.06em;
}
</style>
