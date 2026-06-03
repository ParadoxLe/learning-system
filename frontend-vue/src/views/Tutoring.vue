<template>
  <div class="tutoring-page">
    <div class="page-header tutor">
      <h1>🤖 智能辅导</h1>
      <p>TutorAgent根据你的认知风格，提供多模态个性化答疑——文字解析 + 图解说明 + 举一反三</p>
    </div>

    <ProfileBanner />

    <el-row :gutter="20">
      <!-- 左侧：学习画像上下文 -->
      <el-col :span="7">
        <div class="tutor-sidebar">
          <h4 style="margin:0 0 0.8rem 0; color:#5C4F42;">🧠 辅导上下文</h4>

          <div v-if="!store.hasProfile" style="background:#FBF3E0; border-radius:10px; padding:1rem; font-size:0.85rem; color:#8B6F3D;">
            尚未构建学习画像，辅导将使用通用模式回答。建议先去 <router-link to="/profile">构建画像</router-link>。
          </div>

          <div v-else-if="profile" class="tutor-context-card">
            <div class="context-item">
              <span class="context-label">📊 知识水平</span>
              <span class="context-value">{{ LEVEL[kb.level] || kb.level || '—' }}</span>
            </div>
            <div class="context-item">
              <span class="context-label">🎨 认知风格</span>
              <span class="context-value">{{ STYLE[cs.primary_style] || cs.primary_style || '—' }}</span>
            </div>
            <div class="context-item">
              <span class="context-label">⏱️ 学习节奏</span>
              <span class="context-value">{{ PACE[lp.speed] || lp.speed || '—' }}</span>
            </div>
            <div class="context-item">
              <span class="context-label">📱 偏好模态</span>
              <span class="context-value">{{ modsText }}</span>
            </div>
            <div class="context-item">
              <span class="context-label">⏱️ 专注时长</span>
              <span class="context-value">{{ attentionLabel }}</span>
            </div>

            <div v-if="kb.mastered_topics?.length" style="margin-top:0.6rem;">
              <span style="font-size:0.75rem; color:#7A6E63;">✅ 已掌握</span>
              <p style="margin:0.15rem 0 0 0; font-size:0.82rem; color:#666; line-height:1.5;">
                {{ kb.mastered_topics.join('、') }}
              </p>
            </div>
            <div v-if="kb.weak_points?.length" style="margin-top:0.5rem;">
              <span style="font-size:0.75rem; color:#7A6E63;">⚠️ 薄弱点</span>
              <p style="margin:0.15rem 0 0 0; font-size:0.82rem; color:#666; line-height:1.5;">
                {{ kb.weak_points.join('、') }}
              </p>
            </div>
            <div v-if="kb.target_topics?.length" style="margin-top:0.5rem;">
              <span style="font-size:0.75rem; color:#7A6E63;">🎯 学习目标</span>
              <p style="margin:0.15rem 0 0 0; font-size:0.82rem; color:#666; line-height:1.5;">
                {{ kb.target_topics.join('、') }}
              </p>
            </div>
          </div>

          <div style="margin-top:0.8rem;">
            <span style="font-size:0.8rem; color:#7A6E63;">📝 课程上下文（可选）</span>
            <el-input
              v-model="context"
              type="textarea"
              :rows="3"
              placeholder="例如：正在学 Python 面向对象编程第三章..."
              style="margin-top:0.3rem;"
            />
          </div>

          <div style="background:#F5EDE0; border-radius:10px; padding:0.7rem; margin-top:0.8rem; font-size:0.78rem; color:#C8A25C; line-height:1.6;">
            💡 <b>辅导策略</b><br />
            <span v-if="cs.primary_style === 'visual'">🎨 重点使用图解说明</span>
            <span v-else-if="cs.primary_style === 'logical'">🧮 重点使用推导步骤</span>
            <span v-else-if="cs.primary_style === 'hands_on'">🛠️ 提供可操作的例子</span>
            <span v-else-if="cs.primary_style === 'verbal'">📝 重点使用文字类比</span>
            <span v-else>📚 综合使用多种讲解方式</span>
          </div>
        </div>
      </el-col>

      <!-- 右侧：辅导对话区 -->
      <el-col :span="17">
        <div class="chat-container" ref="chatContainer">
          <div v-if="messages.length === 0" style="background:#f9fafb; border-radius:12px; padding:1.5rem; color:#7A6E63; text-align:center; margin:2rem 0;">
            <div style="font-size:3rem;">🤖</div>
            <p style="margin-top:0.8rem;"><b>学习中遇到困难？</b><br />在下方输入问题，TutorAgent会根据你的学习画像提供个性化解答</p>
          </div>

          <div
            v-for="(msg, i) in messages"
            :key="i"
            :class="['chat-bubble', msg.role]"
          >
            <div v-if="msg.role === 'assistant'" class="markdown-content" v-html="renderMd(msg.content)" />
            <template v-else>{{ msg.content }}</template>
          </div>
        </div>

        <div style="display:flex; gap:0.5rem;">
          <el-input
            v-model="question"
            placeholder="输入你的学习问题..."
            @keyup.enter="askQuestion"
            :disabled="loading"
            size="large"
          />
          <el-button type="primary" @click="askQuestion" :loading="loading" size="large">
            提问
          </el-button>
        </div>

        <el-button @click="messages = []" style="margin-top:0.8rem;">🔄 清空辅导记录</el-button>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useStudentStore } from '../stores/student'
import { askTutor } from '../api'
import ProfileBanner from '../components/ProfileBanner.vue'
import MarkdownIt from 'markdown-it'
import { ElMessage } from 'element-plus'

const store = useStudentStore()
const md = new MarkdownIt()
const messages = ref([])
const question = ref('')
const context = ref('')
const loading = ref(false)
const chatContainer = ref(null)

const LEVEL = { beginner: '入门级', intermediate: '中级', advanced: '高级' }
const STYLE = { visual: '视觉型', verbal: '文字型', logical: '逻辑型', hands_on: '动手型', social: '社交型' }
const PACE = { slow_and_deep: '慢而深', moderate: '中等', fast: '快速' }
const MODALITY = { text: '文字', video: '视频', audio: '音频', interactive: '交互', diagram: '图示', code_practice: '代码实操' }

const profile = computed(() => store.profile)
const kb = computed(() => profile.value?.knowledge_base || {})
const cs = computed(() => profile.value?.cognitive_style || {})
const lp = computed(() => profile.value?.learning_pace || {})
const pm = computed(() => profile.value?.preferred_modalities || {})

const modsText = computed(() => {
  const mods = (!Array.isArray(pm.value) && typeof pm.value === 'object') ? (pm.value.modalities || []) : (Array.isArray(pm.value) ? pm.value : [])
  return mods.map(m => MODALITY[m] || m).join('、') || '—'
})

const attentionLabel = computed(() => {
  const map = { short: '短（&lt;30分钟）', medium: '中等（30-90分钟）', long: '长（&gt;90分钟）' }
  return map[lp.value.attention_span] || lp.value.attention_span || '—'
})

function renderMd(content) {
  return md.render(content || '')
}

async function askQuestion() {
  const q = question.value.trim()
  if (!q || loading.value) return
  if (!store.currentStudentId) { ElMessage.warning('请先创建学生'); return }

  messages.value.push({ role: 'user', content: q })
  question.value = ''
  loading.value = true

  try {
    const result = await askTutor(store.currentStudentId, q, context.value)
    messages.value.push({ role: 'assistant', content: result.answer || '抱歉，未能生成解答。' })
  } catch (e) {
    ElMessage.error('请求失败：' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
    await nextTick()
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  }
}
</script>

<style scoped>
.tutoring-page {
  padding: 0.6rem 1.2rem 0.8rem;
}
</style>
