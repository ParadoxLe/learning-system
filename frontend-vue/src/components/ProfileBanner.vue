<template>
  <div v-if="hasProfile && profile" class="profile-banner">
    <span style="font-size:1.3rem;">🧠</span>
    <span class="badge">当前画像驱动</span>
    <span v-for="dim in dimensions" :key="dim.label" style="font-size:0.82rem;color:#555;white-space:nowrap;">
      {{ dim.label }}: <strong>{{ dim.value }}</strong>
    </span>
  </div>
  <div v-else class="profile-warning">
    <span style="font-size:1.5rem;">⚠️</span>
    <div>
      <b>尚未构建学习画像</b> — 当前生成的内容<b>未经过个性化适配</b>。<br />
      <span style="font-size:0.82rem;">建议先去 <b>「🧠 学习画像构建」</b> 页面用自然语言描述你的学习情况。</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStudentStore } from '../stores/student'

const store = useStudentStore()

const LEVEL = { beginner: '入门级', intermediate: '中级', advanced: '高级' }
const STYLE = { visual: '视觉型', verbal: '文字型', logical: '逻辑型', hands_on: '动手型', social: '社交型' }
const PACE = { slow_and_deep: '慢而深', moderate: '中等', fast: '快速' }
const MODALITY = { text: '文字', video: '视频', audio: '音频', interactive: '交互', diagram: '图示', code_practice: '代码实操' }

const hasProfile = computed(() => store.hasProfile)
const profile = computed(() => store.profile)

const dimensions = computed(() => {
  if (!profile.value) return []
  const p = profile.value
  const kb = p.knowledge_base || {}
  const cs = p.cognitive_style || {}
  const lp = p.learning_pace || {}
  const pm = p.preferred_modalities || {}
  const mf = p.motivation_factors || {}

  const mods = typeof pm === 'object' && !Array.isArray(pm) ? (pm.modalities || []) : (Array.isArray(pm) ? pm : [])

  return [
    { label: '知识水平', value: LEVEL[kb.level] || kb.level || '—' },
    { label: '认知风格', value: STYLE[cs.primary_style] || cs.primary_style || '—' },
    { label: '学习节奏', value: PACE[lp.speed] || lp.speed || '—' },
    { label: '偏好', value: mods.map(m => MODALITY[m] || m).join(', ') || '—' },
    { label: '目标', value: (mf && mf.primary_goal) || '—' },
  ]
})
</script>
