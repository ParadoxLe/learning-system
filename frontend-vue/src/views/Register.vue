<template>
  <div class="login-root">
    <!-- 左侧：图书馆氛围 -->
    <div class="login-brand">
      <div class="brand-ornament-top"></div>

      <div class="brand-inner">
        <!-- 主视觉：打开的书 + 羽毛笔 -->
        <div class="brand-visual">
          <div class="visual-books">
            <span class="book book-1">📖</span>
            <span class="book book-2">📚</span>
            <span class="book book-3">📝</span>
          </div>
          <div class="visual-lamp">🪔</div>
        </div>

        <h1 class="brand-title">开启学习之旅</h1>

        <div class="brand-rule">
          <span class="rule-line"></span>
          <span class="rule-diamond">◆</span>
          <span class="rule-line"></span>
        </div>

        <p class="brand-desc">
          创建账号，AI 将为你构建专属学习画像，规划最优学习路径，随时随地提供个性化辅导。
        </p>

        <div class="brand-tags">
          <span class="brand-tag">免费注册</span>
          <span class="brand-tag">即刻体验</span>
          <span class="brand-tag">数据安全</span>
          <span class="brand-tag">隐私保护</span>
        </div>

        <div class="brand-quote">
          已有账号？
          <router-link to="/login" style="color:#D4B86C; text-decoration:none; font-weight:600;">
            返回登录 →
          </router-link>
        </div>
      </div>

      <div class="brand-ornament-bottom"></div>
    </div>

    <!-- 右侧：注册表单 -->
    <div class="login-form-side">
      <div class="form-card">
        <div class="form-tabs">
          <router-link to="/login" class="form-tab link">账号登录</router-link>
          <span class="form-tab active">注册新账号</span>
        </div>

        <p class="form-subtitle">填写信息，创建你的专属学习账号</p>

        <el-form @keyup.enter="handleRegister">
          <div class="input-group">
            <label class="input-label">用户名</label>
            <el-input
              v-model="username"
              placeholder="取个好记的名字"
              size="large"
              maxlength="50"
              show-word-limit
              class="custom-input"
            >
              <template #prefix>
                <span class="input-icon">👤</span>
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

          <div class="input-group">
            <label class="input-label">密码</label>
            <el-input
              v-model="password"
              type="password"
              placeholder="至少 4 位字符"
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
            <label class="input-label">确认密码</label>
            <el-input
              v-model="confirmPassword"
              type="password"
              placeholder="再次输入密码"
              size="large"
              show-password
              class="custom-input"
            >
              <template #prefix>
                <span class="input-icon">🔒</span>
              </template>
            </el-input>
          </div>

          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleRegister"
            class="login-submit-btn"
          >
            注 册 账 号
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
const confirmPassword = ref('')
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

async function handleRegister() {
  const u = username.value.trim()
  const c = captchaInput.value.trim()
  if (!u) { ElMessage.warning('请输入用户名'); return }
  if (!c || c.length !== 4) { ElMessage.warning('请输入4位验证码'); return }
  if (password.value.length < 4) { ElMessage.warning('密码至少需要4位'); return }
  if (password.value !== confirmPassword.value) { ElMessage.warning('两次输入的密码不一致'); return }
  loading.value = true
  try {
    await auth.register(u, password.value, captchaId.value, c)
    ElMessage.success('注册成功')
    router.push('/')
  } catch (err) {
    ElMessage({ message: err.response?.data?.detail || '注册失败', type: 'error', duration: 4000 })
    refreshCaptcha()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
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

.login-brand::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    repeating-linear-gradient(2deg, transparent, transparent 3px, rgba(255,255,255,0.008) 3px, rgba(255,255,255,0.008) 6px),
    repeating-linear-gradient(90deg, transparent, transparent 40px, rgba(0,0,0,0.03) 40px, rgba(0,0,0,0.03) 41px);
  pointer-events: none;
}

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

.brand-ornament-top {
  position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, transparent 0%, #C8A25C 20%, #D4B86C 50%, #C8A25C 80%, transparent 100%);
}

.brand-ornament-bottom {
  position: absolute;
  bottom: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, transparent 0%, #C8A25C 20%, #D4B86C 50%, #C8A25C 80%, transparent 100%);
}

.brand-inner {
  position: relative; z-index: 1;
  max-width: 440px;
  display: flex; flex-direction: column; align-items: center;
  text-align: center;
}

.brand-visual {
  position: relative;
  margin-bottom: 2rem;
}

.visual-books {
  display: flex; gap: 0.3rem; justify-content: center;
}

.book {
  font-size: 2.8rem;
  display: block;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
}

.book-1 { transform: rotate(-10deg) translateY(0); }
.book-2 { transform: translateY(-8px); }
.book-3 { transform: rotate(8deg) translateY(2px); }

.visual-lamp {
  position: absolute;
  top: -2.2rem; right: -1.5rem;
  font-size: 2.5rem;
  filter: drop-shadow(0 0 12px rgba(212, 184, 108, 0.5));
  animation: lampGlow 3s ease-in-out infinite;
}

@keyframes lampGlow {
  0%, 100% { filter: drop-shadow(0 0 12px rgba(212, 184, 108, 0.4)); }
  50% { filter: drop-shadow(0 0 22px rgba(212, 184, 108, 0.7)); }
}

.brand-title {
  font-size: 2.2rem; font-weight: 800;
  color: #F0E6D8;
  margin: 0; letter-spacing: 0.04em; line-height: 1.3;
}

.brand-rule {
  display: flex; align-items: center; gap: 1rem;
  margin: 1.2rem 0; width: 100%; max-width: 280px;
}

.rule-line {
  flex: 1; height: 1px;
  background: linear-gradient(90deg, transparent, #C8A25C, transparent);
}

.rule-diamond {
  color: #C8A25C; font-size: 0.5rem;
}

.brand-desc {
  color: #A89880; font-size: 0.9rem; line-height: 1.8;
  margin: 0 0 1.5rem 0; max-width: 380px;
}

.brand-tags {
  display: flex; flex-wrap: wrap; justify-content: center;
  gap: 0.5rem; margin-bottom: 2rem;
}

.brand-tag {
  font-size: 0.72rem; color: #B8A088;
  border: 1px solid rgba(184, 160, 136, 0.3);
  border-radius: 3px; padding: 0.25rem 0.7rem; letter-spacing: 0.04em;
}

.brand-quote {
  color: #8B7A65; font-size: 0.85rem; font-style: italic;
  line-height: 1.7; margin: 0;
}

/* ===== 右侧表单区 ===== */
.login-form-side {
  width: 56%;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  background: linear-gradient(180deg, #FBF7F0 0%, #F5EDE0 100%);
  padding: 3rem; position: relative;
}

.login-form-side::before {
  content: '';
  position: absolute; left: 0; top: 15%; bottom: 15%; width: 1px;
  background: linear-gradient(180deg, transparent, rgba(200, 162, 92, 0.3), transparent);
}

.form-card {
  width: 100%; max-width: 420px;
  background: #FFFEF9;
  border-radius: 8px;
  padding: 2.5rem 2.5rem 2rem;
  box-shadow: 0 2px 24px rgba(60, 48, 40, 0.08);
  border: 1px solid #E8E0D5;
}

.form-tabs {
  display: flex; gap: 1.5rem; margin-bottom: 0.8rem;
}

.form-tab {
  font-size: 0.95rem; color: #A89880; text-decoration: none;
  padding-bottom: 0.5rem; border-bottom: 2px solid transparent;
  transition: all 0.2s; cursor: pointer;
}

.form-tab.active {
  color: #3C3028; font-weight: 700;
  border-bottom-color: #C8A25C; font-size: 1.25rem;
}

.form-tab.link {
  font-size: 0.88rem; align-self: flex-end;
}

.form-tab.link:hover { color: #C8A25C; }

.form-subtitle {
  color: #A89880; font-size: 0.85rem;
  margin: 0 0 2rem 0; padding-bottom: 1.2rem;
  border-bottom: 1px solid #E8E0D5;
}

.input-group { margin-bottom: 1.2rem; }

.input-label {
  display: block; font-size: 0.78rem; font-weight: 600;
  color: #5C4F42; margin-bottom: 0.4rem;
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

.input-icon { font-size: 1rem; }

.code-row { display: flex; gap: 0.6rem; }

.code-input { flex: 1; }

.captcha-display {
  flex-shrink: 0; display: flex; align-items: center; gap: 0.4rem;
  background: linear-gradient(135deg, #F5EDE0, #EDE5D5);
  border: 1.5px dashed rgba(200, 162, 92, 0.4);
  border-radius: 6px; padding: 0 1rem;
  cursor: pointer; user-select: none; transition: all 0.2s;
  min-width: 115px; justify-content: center;
}

.captcha-display:hover {
  background: linear-gradient(135deg, #EDE0D0, #E0D4C0);
  border-color: rgba(200, 162, 92, 0.6);
}

.captcha-text {
  font-size: 1.3rem; font-weight: 700; letter-spacing: 0.3em;
  color: #3C3028;
  font-family: 'Georgia', 'Courier New', serif; font-style: italic;
}

.captcha-refresh { font-size: 1.1rem; color: #C8A25C; }

.login-submit-btn {
  width: 100%; border-radius: 6px; font-size: 0.95rem;
  font-weight: 600; letter-spacing: 0.12em; height: 48px;
  margin-top: 0.8rem;
  background: linear-gradient(135deg, #5D3A2C, #4A2E20);
  border: none; transition: all 0.25s;
}

.login-submit-btn:hover {
  background: linear-gradient(135deg, #4A2E20, #3E2723);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(60, 48, 40, 0.25);
}

.login-footer-text {
  margin-top: 2rem; font-size: 0.72rem;
  color: #B8A088; letter-spacing: 0.06em;
}
</style>
