<template>
  <div class="onboard-root">
    <!-- Left: Digital Human -->
    <div class="onboard-left">
        <DigitalHuman ref="dhRef" />
      </div>

      <!-- Right: Chat card -->
      <div class="onboard-right">
        <div class="onboard-card">
      <!-- ==================== Step 1: 选择学段 ==================== -->
      <div v-if="step === 1" class="card-body">
        <div class="card-icon">👋</div>
        <h2 class="card-title">选择你的学习阶段</h2>
        <p class="card-desc">帮助 AI 了解你的知识起点，定制最合适的学习方案</p>

        <div class="stage-list">
          <div
            v-for="s in stages"
            :key="s.value"
            :class="['stage-row', { picked: selectedStage === s.value }]"
            @click="selectedStage = s.value"
          >
            <span class="stage-row-emoji">{{ s.emoji }}</span>
            <div class="stage-row-text">
              <span class="stage-row-name">{{ s.label }}</span>
              <span class="stage-row-desc">{{ s.desc }}</span>
            </div>
            <span v-if="selectedStage === s.value" class="stage-check">✓</span>
          </div>
        </div>

        <el-button
          type="primary"
          size="large"
          :disabled="!selectedStage"
          @click="startChat"
          class="onboard-btn"
        >
          下一步 → 开始对话
        </el-button>
      </div>

      <!-- ==================== Step 2: AI 对话 ==================== -->
      <div v-if="step === 2" class="card-body chat-body">
        <div class="chat-header">
          <span class="chat-stage-tag">{{ selectedStageLabel }}</span>
          <span class="chat-title">让 AI 了解你的学习情况</span>
          <span class="chat-subtitle">用自然语言回答，AI 会通过对话了解你的特点</span>
        </div>

        <!-- Messages -->
        <div class="chat-messages" ref="chatBox">
          <div
            v-for="(msg, i) in messages"
            :key="i"
            :class="['chat-msg', msg.role]"
          >
            <div class="chat-avatar">{{ msg.role === 'assistant' ? '🤖' : '🙋' }}</div>
            <div class="chat-bubble">
              <div v-if="msg.role === 'assistant'" v-html="renderMd(msg.content)" />
              <template v-else>{{ msg.content }}</template>
            </div>
          </div>

          <!-- Typing indicator -->
          <div v-if="waiting" class="chat-msg assistant">
            <div class="chat-avatar">🤖</div>
            <div class="chat-bubble typing">
              <span class="typing-dot" />
              <span class="typing-dot" />
              <span class="typing-dot" />
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="chat-input-row" v-if="!profileReady">
          <el-input
            v-model="input"
            placeholder="在这里输入你的回答..."
            size="large"
            :disabled="waiting"
            @keyup.enter="sendMsg"
          />
          <el-button
            type="primary"
            size="large"
            :disabled="!input.trim() || waiting"
            :loading="waiting"
            @click="sendMsg"
          >
            发送
          </el-button>
        </div>

        <!-- Profile ready -->
        <div v-if="profileReady" class="profile-done">
          <span class="done-icon">✅</span>
          <span class="done-text">学习画像已生成，正在跳转到学习仪表盘...</span>
        </div>
        </div>
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useStudentStore } from '../stores/student'
import MarkdownIt from 'markdown-it'
import { ElMessage } from 'element-plus'
import DigitalHuman from '../components/DigitalHuman.vue'

const router = useRouter()
const auth = useAuthStore()
const store = useStudentStore()
const md = new MarkdownIt()
const dhRef = ref(null)

const step = ref(1)
const selectedStage = ref('')
const messages = ref([])
const input = ref('')
const waiting = ref(false)
const profileReady = ref(false)
const chatBox = ref(null)

const stages = [
  { value: 'primary', label: '小学', emoji: '🏫', desc: '基础学科启蒙' },
  { value: 'junior', label: '初中', emoji: '📐', desc: '知识体系构建' },
  { value: 'senior', label: '高中', emoji: '📖', desc: '深度学科学习' },
  { value: 'university', label: '大学', emoji: '🎓', desc: '专业领域深入' },
  { value: 'postgrad', label: '研究生', emoji: '🔬', desc: '学术研究方向' },
  { value: 'career', label: '职场进修', emoji: '💼', desc: '职业技能提升' },
  { value: 'self', label: '自学/其他', emoji: '🌱', desc: '自主学习探索' },
]

const selectedStageLabel = computed(() => {
  return stages.find(s => s.value === selectedStage.value)?.label || ''
})

function renderMd(text) { return md.render(text || '') }

function scrollToBottom() {
  nextTick(() => {
    if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
  })
}

async function startChat() {
  step.value = 2
  const stage = stages.find(s => s.value === selectedStage.value)
  const welcomeText = `你好！我是你的专属学习画像分析师。\n\n你目前处于 **${stage?.label}** 阶段（${stage?.desc}），请先自由介绍一下自己的学习情况吧。比如：\n\n- 你目前在学什么？\n- 你的学习目标是什么？\n- 你觉得自己擅长和不擅长的方面？\n- 你喜欢什么样的学习方式？\n\n尽情表达就好，我会根据你的描述来构建学习画像。`
  messages.value.push({ role: 'assistant', content: welcomeText })
  scrollToBottom()
  // Make digital human speak the welcome
  dhRef.value?.speak('你好！我是你的专属学习画像分析师，请自由介绍一下自己的学习情况吧。')
}

async function sendMsg() {
  const text = input.value.trim()
  if (!text || waiting.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: text })
  scrollToBottom()

  waiting.value = true
  messages.value.push({ role: 'assistant', content: '' })

  try {
    const token = localStorage.getItem('token')
    const response = await fetch('/api/profile/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        student_id: store.currentStudentId,
        message: text,
      }),
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const raw = line.slice(6)
          if (raw === '[DONE]') continue
          try {
            const data = JSON.parse(raw)
            if (data.status === 'complete' && data.profile) {
              const last = messages.value[messages.value.length - 1]
              last.content = '已根据你的回答生成学习画像，正在为你跳转...'
              saveProfile(data.profile)
              return
            } else if (data.status === 'need_more_info') {
              // fallback — text already streamed
            } else if (data.error) {
              const last = messages.value[messages.value.length - 1]
              last.content = '抱歉，出了点问题，请重试。'
              ElMessage.error('请求失败：' + data.error)
            } else if (data.token) {
              const last = messages.value[messages.value.length - 1]
              last.content += data.token
            }
          } catch {
            const last = messages.value[messages.value.length - 1]
            last.content += raw
          }
          await nextTick()
          scrollToBottom()
        }
      }
    }
  } catch (e) {
    const last = messages.value[messages.value.length - 1]
    last.content = '抱歉，出了点问题，请重试。'
    ElMessage.error('请求失败：' + (e.message || e))
  } finally {
    waiting.value = false
    scrollToBottom()
    // Speak the AI response via digital human
    const lastMsg = messages.value[messages.value.length - 1]
    if (lastMsg && lastMsg.role === 'assistant' && lastMsg.content) {
      // Strip markdown for speech
      const plain = lastMsg.content.replace(/[#*`_~\[\]()>|\-]/g, '').replace(/\n+/g, '，').slice(0, 200)
      dhRef.value?.speak(plain)
    }
  }
}

function saveProfile(profile) {
  store.profile = profile
  store.profileVersion = 1
  auth.hasProfile = true
  profileReady.value = true
  ElMessage.success('学习画像已生成！')
  sessionStorage.removeItem('_intro_shown')
  setTimeout(() => { router.replace('/welcome') }, 2000)
}
</script>

<style scoped>
.onboard-root {
  display: flex; justify-content: center; align-items: center; gap: 2rem;
  width: 100%; min-height: 100vh; padding: 3rem 5rem;
  background: linear-gradient(135deg, #F5EDE0 0%, #F5EDE0 50%, #F5EDE0 100%);
  box-sizing: border-box;
}

/* Left: Digital Human */
.onboard-left {
  flex: 1; overflow: hidden;
  background: #fff; border-radius: 20px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.08);
  height: 90vh;
}

/* Right: Chat card */
.onboard-right {
  flex: 3; min-width: 0;
  height: 90vh;
}

.onboard-card {
  width: 100%; height: 100%; max-width: none;
  background: #fff; border-radius: 20px;
  overflow: hidden; box-shadow: 0 8px 40px rgba(0,0,0,0.08);
}
.card-body { padding: 2rem 2.2rem; height: 100%; overflow-y: auto; box-sizing: border-box; }

/* ===== Step 1: Stage selection ===== */
.card-icon { font-size: 2.5rem; text-align: center; margin-bottom: 0.5rem; }
.card-title { text-align: center; font-size: 1.4rem; font-weight: 700; color: #3C3028; margin: 0 0 0.3rem; }
.card-desc { text-align: center; font-size: 0.9rem; color: #7A6E63; margin: 0 0 1.2rem; }

.stage-list { display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 1.2rem; }
.stage-row {
  display: flex; align-items: center; gap: 0.7rem;
  padding: 0.7rem 1rem; border-radius: 12px; cursor: pointer;
  border: 1.5px solid #E8E0D5; transition: all 0.2s;
}
.stage-row:hover { border-color: #D4C4A8; background: #FFFEF9; }
.stage-row.picked { border-color: #C8A25C; background: #faf5ec; box-shadow: 0 0 0 3px rgba(200,162,92,0.12); }
.stage-row-emoji { font-size: 1.3rem; flex-shrink: 0; }
.stage-row-text { flex: 1; display: flex; flex-direction: column; }
.stage-row-name { font-weight: 600; font-size: 0.9rem; color: #3C3028; }
.stage-row-desc { font-size: 0.75rem; color: #7A6E63; }
.stage-check { font-size: 1rem; color: #C8A25C; font-weight: 700; }
.onboard-btn { width: 100%; height: 46px; font-size: 1rem; }

/* ===== Step 2: Chat ===== */
.chat-body { display: flex; flex-direction: column; height: 100%; padding: 0; }
.chat-header {
  padding: 1.2rem 1.5rem; border-bottom: 1px solid #E8E0D5;
  display: flex; flex-direction: column; align-items: center; gap: 0.2rem;
  flex-shrink: 0;
}
.chat-stage-tag {
  font-size: 0.72rem; background: linear-gradient(135deg, rgba(200,162,92,0.12), rgba(184,147,79,0.12));
  color: #C8A25C; padding: 2px 12px; border-radius: 12px; font-weight: 600;
}
.chat-title { font-weight: 700; font-size: 1.2rem; color: #3C3028; }
.chat-subtitle { font-size: 0.88rem; color: #A89880; }

/* Messages */
.chat-messages {
  flex: 1; overflow-y: auto; padding: 1rem 2rem;
  display: flex; flex-direction: column; gap: 0.7rem;
}
.chat-msg { display: flex; gap: 0.5rem; max-width: 100%; }
.chat-msg.user { align-self: flex-end; flex-direction: row-reverse; }
.chat-msg.assistant { align-self: flex-start; }

.chat-avatar {
  width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem;
}
.chat-bubble {
  padding: 0.8rem 1.1rem; border-radius: 14px; font-size: 1.05rem; line-height: 1.7;
}
.chat-msg.user .chat-bubble {
  background: linear-gradient(135deg, #C8A25C, #B8934F); color: #fff;
  border-bottom-right-radius: 4px;
}
.chat-msg.assistant .chat-bubble {
  background: #F5EDE0; color: #3C3028;
  border-bottom-left-radius: 4px;
}
.chat-bubble.typing {
  display: flex; gap: 4px; padding: 0.7rem 1rem; align-items: center;
}
.typing-dot {
  width: 7px; height: 7px; border-radius: 50%; background: #A89880;
  animation: typing-bounce 1.4s infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}

/* Markdown in assistant bubbles */
.chat-msg.assistant .chat-bubble :deep(p) { margin: 0.2rem 0; }
.chat-msg.assistant .chat-bubble :deep(ul),
.chat-msg.assistant .chat-bubble :deep(ol) { margin: 0.3rem 0; padding-left: 1.2rem; }
.chat-msg.assistant .chat-bubble :deep(li) { margin: 0.1rem 0; }

/* Input */
.chat-input-row {
  display: flex; gap: 0.6rem; padding: 1rem 1.5rem;
  border-top: 1px solid #E8E0D5; flex-shrink: 0;
}
.chat-input-row .el-input { flex: 1; }
.chat-input-row :deep(.el-input__inner) {
  font-size: 1.1rem !important; height: 48px !important; line-height: 48px !important;
}
.chat-input-row .el-button { height: 48px; font-size: 1.05rem; padding: 0 1.5rem; }

/* Profile done */
.profile-done {
  display: flex; flex-direction: column; align-items: center; gap: 0.6rem;
  padding: 1.2rem; border-top: 1px solid #E8E0D5; flex-shrink: 0;
}
.done-icon { font-size: 2rem; }
.done-text { font-weight: 600; color: #3C3028; font-size: 0.95rem; }
</style>
