<template>
  <div class="settings-root">
    <div class="settings-card">
      <!-- Header -->
      <div class="settings-header">
        <div class="header-avatar" @click="triggerUpload">
          <img v-if="avatarPreview" :src="avatarPreview" class="header-avatar-img" />
          <span v-else class="header-avatar-text">{{ auth.user?.username?.charAt(0)?.toUpperCase() }}</span>
          <div class="header-avatar-overlay">更换</div>
        </div>
        <h2 class="header-name">{{ auth.user?.username }}</h2>
        <p class="header-date">注册于 {{ createdAt || '—' }}</p>
        <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="handleFile" />
      </div>

      <el-divider style="margin: 1.2rem 0;" />

      <!-- Avatar actions -->
      <div class="action-row">
        <span class="action-label">头像设置</span>
        <div class="action-btns">
          <el-button size="small" @click="triggerUpload">{{ avatarPreview ? '更换图片' : '上传图片' }}</el-button>
          <el-button v-if="avatarPreview" size="small" type="danger" plain @click="removeAvatar">移除头像</el-button>
        </div>
      </div>

      <el-divider style="margin: 1.2rem 0;" />

      <!-- Password Section -->
      <div v-if="pwdDone" class="pwd-done">
        <span class="done-icon">✅</span>
        <span>密码修改成功，即将跳转到学习仪表盘...</span>
      </div>

      <div v-else class="pwd-section">
        <span class="action-label">修改密码</span>
        <el-form :model="pwdForm" label-width="80px" class="pwd-form">
          <el-form-item label="原密码">
            <el-input v-model="pwdForm.oldPassword" type="password" show-password placeholder="输入原密码" size="large" />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input v-model="pwdForm.newPassword" type="password" show-password placeholder="至少4位" size="large" />
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input v-model="pwdForm.confirmPassword" type="password" show-password placeholder="再次输入新密码" size="large" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" size="large" :loading="pwdLoading" @click="handleUpdatePassword" class="pwd-btn">修改密码</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { updatePassword, updateAvatar, me } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const auth = useAuthStore()
const fileInput = ref(null)
const avatarPreview = ref('')
const createdAt = ref('')
const pwdLoading = ref(false)
const pwdDone = ref(false)

const pwdForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

onMounted(async () => {
  try {
    const info = await me()
    avatarPreview.value = info.avatar || ''
    createdAt.value = info.created_at || ''
    if (auth.user) auth.user.avatar = info.avatar || ''
  } catch { /* ignore */ }
})

function triggerUpload() {
  fileInput.value?.click()
}

function handleFile(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (file.size > 512 * 1024) {
    ElMessage.warning('图片大小不能超过 512KB')
    return
  }
  const reader = new FileReader()
  reader.onload = async () => {
    const dataUrl = reader.result
    avatarPreview.value = dataUrl
    try {
      await updateAvatar(dataUrl)
      if (auth.user) auth.user.avatar = dataUrl
      ElMessage.success('头像已更新')
    } catch (err) {
      ElMessage.error('头像更新失败：' + (err.response?.data?.detail || err.message))
    }
  }
  reader.readAsDataURL(file)
  e.target.value = ''
}

async function removeAvatar() {
  try {
    await updateAvatar('')
    avatarPreview.value = ''
    if (auth.user) auth.user.avatar = ''
    ElMessage.success('头像已移除')
  } catch (err) {
    ElMessage.error('移除失败：' + (err.response?.data?.detail || err.message))
  }
}

async function handleUpdatePassword() {
  if (!pwdForm.oldPassword) { ElMessage.warning('请输入原密码'); return }
  if (!pwdForm.newPassword || pwdForm.newPassword.length < 4) { ElMessage.warning('新密码至少4位'); return }
  if (pwdForm.newPassword !== pwdForm.confirmPassword) { ElMessage.warning('两次输入的新密码不一致'); return }

  try {
    await ElMessageBox.confirm('确认修改密码？', '确认', {
      confirmButtonText: '确认修改',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return // user cancelled
  }

  pwdLoading.value = true
  try {
    await updatePassword(pwdForm.oldPassword, pwdForm.newPassword)
    pwdDone.value = true
    setTimeout(() => { router.push('/') }, 1500)
  } catch (err) {
    ElMessage.error('修改失败：' + (err.response?.data?.detail || err.message))
  } finally {
    pwdLoading.value = false
  }
}
</script>

<style scoped>
.settings-root {
  min-height: calc(100vh - 3rem);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.settings-card {
  width: 100%;
  max-width: 480px;
  background: #FFFEF9;
  border-radius: 12px;
  padding: 2.5rem 2.5rem 2rem;
  box-shadow: 0 2px 16px rgba(60, 48, 40, 0.08);
  border: 1px solid #E8E0D5;
}

/* Header */
.settings-header {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header-avatar {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  background: linear-gradient(135deg, #C8A25C, #B8934F);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
  margin-bottom: 0.8rem;
}

.header-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.header-avatar-text {
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
}

.header-avatar-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.4);
  color: #fff;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  border-radius: 50%;
}

.header-avatar:hover .header-avatar-overlay {
  opacity: 1;
}

.header-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: #3C3028;
  margin: 0;
}

.header-date {
  font-size: 0.8rem;
  color: #A89880;
  margin: 0.25rem 0 0;
}

/* Action rows */
.action-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.action-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #5C4F42;
}

.action-btns {
  display: flex;
  gap: 0.5rem;
}

/* Password */
.pwd-section {
  display: flex;
  flex-direction: column;
}

.pwd-section .action-label {
  margin-bottom: 0.8rem;
}

.pwd-form {
  margin-top: 0;
}

.pwd-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #666;
}

.pwd-btn {
  width: 100%;
  border-radius: 6px;
  height: 44px;
  font-size: 1rem;
  font-weight: 600;
  background: linear-gradient(135deg, #C8A25C, #B8934F);
  border: none;
}

.pwd-btn:hover {
  background: linear-gradient(135deg, #B8934F, #A07D3E);
}

.pwd-done {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  padding: 1.5rem 0;
  font-size: 1rem;
  color: #333;
}

.done-icon {
  font-size: 1.6rem;
}
</style>
