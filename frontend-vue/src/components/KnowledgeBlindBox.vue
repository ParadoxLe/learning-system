<template>
  <!-- 侧边栏小卡片 -->
  <div class="blind-box-mini" :class="{ opened: isOpen }" @click="openBox">
    <div v-if="!isOpen" class="mini-closed">
      <span class="mini-icon">🎁</span>
      <span class="mini-sparkle">✨</span>
      <span class="mini-label">知识盲盒</span>
    </div>
    <div v-else class="mini-opened">
      <span class="mini-icon-small">{{ card.box_icon || '🎁' }}</span>
      <span class="mini-label-small">{{ card.box_label || '今日盲盒' }}</span>
    </div>
  </div>

  <!-- 全屏遮罩 + 大卡片 -->
  <Teleport to="body">
    <div v-if="showModal" class="blindbox-overlay" @click.self="closeModal">
      <div class="blindbox-modal">
        <!-- 未打开：大盲盒 -->
        <div v-if="!isOpen" class="modal-closed" @click="openBox">
          <div class="modal-gift-wrap">
            <span class="modal-gift-icon">🎁</span>
            <span class="modal-sparkle">✨</span>
          </div>
          <p class="modal-title">今日知识盲盒</p>
          <p class="modal-hint">点击打开，发现今日惊喜</p>
        </div>

        <!-- 已打开：内容 -->
        <div v-else class="modal-opened">
          <div class="modal-header">
            <span class="modal-box-icon">{{ card.box_icon || '🎁' }}</span>
            <span class="modal-box-label">{{ card.box_label || '知识盲盒' }}</span>
            <span class="modal-date">{{ card.date }}</span>
          </div>
          <div class="modal-tags">
            <span class="modal-tag cat">{{ card.category }}</span>
            <span class="modal-tag diff">{{ DIFF[card.difficulty] || card.difficulty }}</span>
          </div>
          <h3 class="modal-card-title">{{ card.title }}</h3>
          <p class="modal-card-content">{{ card.content }}</p>
          <div class="modal-footer">
            <span class="modal-footer-tip">💡 明天再来，解锁新的知识盲盒</span>
            <button class="modal-close-btn" @click="closeModal">关闭</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { useStudentStore } from '../stores/student'
import { getDailyBlindBox } from '../api'
import { ElMessage } from 'element-plus'

const store = useStudentStore()
const isOpen = ref(false)
const showModal = ref(false)
const card = ref({})
const loading = ref(false)

const DIFF = { beginner: '入门', intermediate: '进阶', advanced: '高级' }

async function openBox() {
  if (loading.value) return

  // Always show modal first
  showModal.value = true

  if (isOpen.value) return

  loading.value = true
  try {
    const data = await getDailyBlindBox(store.currentStudentId)
    card.value = data
    isOpen.value = true
  } catch (e) {
    ElMessage.error('盲盒打开失败：' + (e.response?.data?.detail || e.message))
    showModal.value = false
  } finally {
    loading.value = false
  }
}

function closeModal() {
  showModal.value = false
}
</script>

<style scoped>
/* ===== 侧边栏小卡片 ===== */
.blind-box-mini {
  background: linear-gradient(135deg, #C8A25C, #B8934F);
  border-radius: 8px;
  padding: 2rem 0.8rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(60, 48, 40, 0.2);
}

.blind-box-mini::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 20% 30%, rgba(255,254,249,0.15) 0%, transparent 60%);
  pointer-events: none;
}

.blind-box-mini:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(60, 48, 40, 0.3);
}

.mini-closed {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  position: relative;
}

.mini-icon {
  font-size: 1.6rem;
  animation: miniFloat 2.5s ease-in-out infinite;
}

.mini-sparkle {
  position: absolute;
  left: 0.6rem;
  top: -0.3rem;
  font-size: 0.5rem;
  animation: miniSparkle 1.5s ease-in-out infinite;
}

.mini-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #FFFEF9;
}

.mini-opened {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.mini-icon-small {
  font-size: 1rem;
}

.mini-label-small {
  font-size: 0.75rem;
  font-weight: 600;
  color: #FFFEF9;
}

@keyframes miniFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

@keyframes miniSparkle {
  0%, 100% { opacity: 0.3; transform: scale(0.7); }
  50% { opacity: 1; transform: scale(1.1); }
}

/* ===== 全屏遮罩 ===== */
.blindbox-overlay {
  position: fixed;
  inset: 0;
  background: rgba(40, 28, 18, 0.6);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  animation: fadeIn 0.25s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* ===== 弹窗卡片 ===== */
.blindbox-modal {
  background: linear-gradient(160deg, #FFFEF9 0%, #FBF7F0 40%, #F5EDE0 100%);
  border-radius: 12px;
  padding: 6rem 7rem;
  min-width: 800px;
  max-width: 1000px;
  box-shadow: 0 16px 64px rgba(60, 48, 40, 0.3);
  position: relative;
  overflow: hidden;
  animation: scaleIn 0.3s ease;
  border: 1px solid #E8E0D5;
}

.blindbox-modal::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 20% 10%, rgba(200,162,92,0.08) 0%, transparent 50%),
              radial-gradient(ellipse at 80% 90%, rgba(184,147,79,0.05) 0%, transparent 50%);
  pointer-events: none;
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.85); }
  to { opacity: 1; transform: scale(1); }
}

/* ---- 未打开 ---- */
.modal-closed {
  text-align: center;
  cursor: pointer;
  user-select: none;
}

.modal-gift-wrap {
  position: relative;
  display: inline-block;
}

.modal-gift-icon {
  font-size: 6rem;
  display: block;
  animation: modalFloat 2.5s ease-in-out infinite;
}

.modal-sparkle {
  position: absolute;
  top: 0;
  right: -0.5rem;
  font-size: 2.2rem;
  animation: modalSparkle 1.5s ease-in-out infinite;
}

.modal-title {
  margin: 1.5rem 0 0.4rem;
  font-size: 1.5rem;
  font-weight: 700;
  color: #3C3028;
}

.modal-hint {
  margin: 0;
  font-size: 1rem;
  color: #A89880;
}

@keyframes modalFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-14px); }
}

@keyframes modalSparkle {
  0%, 100% { opacity: 0.3; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.25); }
}

/* ---- 已打开 ---- */
.modal-opened {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-box-icon {
  font-size: 1.8rem;
}

.modal-box-label {
  font-weight: 700;
  font-size: 1.1rem;
  color: #3C3028;
}

.modal-date {
  margin-left: auto;
  font-size: 0.85rem;
  color: #A89880;
}

.modal-tags {
  display: flex;
  gap: 0.5rem;
}

.modal-tag {
  font-size: 0.74rem;
  padding: 0.15rem 0.65rem;
  border-radius: 4px;
  font-weight: 500;
}

.modal-tag.cat {
  background: rgba(200, 162, 92, 0.18);
  color: #8B6F3D;
}

.modal-tag.diff {
  background: rgba(61, 122, 92, 0.15);
  color: #3D7A5C;
}

.modal-card-title {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 700;
  color: #3C3028;
  line-height: 1.4;
}

.modal-card-content {
  margin: 0;
  font-size: 1rem;
  color: #5C4F42;
  line-height: 1.75;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.5rem;
}

.modal-footer-tip {
  font-size: 0.78rem;
  color: #A89880;
}

.modal-close-btn {
  padding: 0.35rem 1.4rem;
  border-radius: 6px;
  border: none;
  background: linear-gradient(135deg, #C8A25C, #B8934F);
  color: #FFFEF9;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.modal-close-btn:hover {
  opacity: 0.85;
}
</style>
