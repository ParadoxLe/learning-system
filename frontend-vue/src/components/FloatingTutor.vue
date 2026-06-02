<template>
  <div class="floating-tutor">
    <!-- FAB 按钮 -->
    <div class="tutor-fab" @click="togglePanel" :class="{ active: visible }">
      <span v-if="!visible">🤖</span>
      <span v-else>✕</span>
    </div>

    <!-- 滑出面板 -->
    <transition name="tutor-slide">
      <div v-if="visible" class="tutor-panel">
        <div class="tutor-panel-header">
          <span>🤖 智能辅导助手</span>
          <span style="font-size:0.75rem; color:#999;">TutorAgent 随叫随到</span>
        </div>

        <!-- 画像上下文摘要 -->
        <div v-if="store.hasProfile && profile" class="tutor-context-mini">
          <span v-if="cs.primary_style" class="context-chip">
            {{ STYLE[cs.primary_style] || cs.primary_style }}
          </span>
          <span v-if="kb.level" class="context-chip">
            {{ LEVEL[kb.level] || kb.level }}
          </span>
          <span v-if="kb.weak_points?.length" class="context-chip" style="background:#fff3e0;color:#e65100;">
            ⚠️ {{ kb.weak_points[0] }}
          </span>
        </div>
        <div v-else class="tutor-context-mini" style="background:#fff8e6;color:#b0780a;">
          未构建画像，使用通用模式
        </div>

        <!-- 聊天区 -->
        <div class="tutor-chat" ref="chatContainer">
          <div v-if="messages.length === 0" style="color:#bbb; font-size:0.85rem; text-align:center; padding:1.5rem 0;">
            学习中遇到问题？直接问我
          </div>
          <div
            v-for="(msg, i) in messages"
            :key="i"
            :class="['tutor-msg', msg.role]"
          >
            <div v-if="msg.role === 'assistant'" class="markdown-content" v-html="renderMd(msg.content)" />
            <template v-else>{{ msg.content }}</template>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="tutor-input-row">
          <el-input
            v-model="question"
            placeholder="输入问题..."
            size="small"
            @keyup.enter="askQuestion"
            :disabled="loading"
          />
          <el-button type="primary" size="small" @click="askQuestion" :loading="loading">
            发送
          </el-button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useStudentStore } from '../stores/student'
import MarkdownIt from 'markdown-it'
import { ElMessage } from 'element-plus'

const store = useStudentStore()
const md = new MarkdownIt()

const visible = ref(false)
const messages = ref([])
const question = ref('')
const loading = ref(false)
const chatContainer = ref(null)

const LEVEL = { beginner: '入门级', intermediate: '中级', advanced: '高级' }
const STYLE = { visual: '视觉型', verbal: '文字型', logical: '逻辑型', hands_on: '动手型', social: '社交型' }

const profile = computed(() => store.profile)
const kb = computed(() => profile.value?.knowledge_base || {})
const cs = computed(() => profile.value?.cognitive_style || {})

function renderMd(content) {
  return md.render(content || '')
}

function togglePanel() {
  visible.value = !visible.value
}

async function askQuestion() {
  const q = question.value.trim()
  if (!q || loading.value) return
  if (!store.currentStudentId) { ElMessage.warning('请先创建学生'); return }

  messages.value.push({ role: 'user', content: q })
  messages.value.push({ role: 'assistant', content: '' })
  question.value = ''
  loading.value = true

  const lastMsg = messages.value[messages.value.length - 1]

  try {
    const token = localStorage.getItem('token')
    const response = await fetch('/api/tutor/ask/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        student_id: store.currentStudentId,
        question: q,
        context: '',
      }),
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const text = decoder.decode(value, { stream: true })
      const lines = text.split('\n')
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') continue
          try { lastMsg.content += JSON.parse(data) } catch { lastMsg.content += data }
          await nextTick()
          if (chatContainer.value) {
            chatContainer.value.scrollTop = chatContainer.value.scrollHeight
          }
        }
      }
    }
  } catch (e) {
    lastMsg.content = '抱歉，请求失败：' + (e.message || '未知错误')
  } finally {
    loading.value = false
  }
}
</script>
