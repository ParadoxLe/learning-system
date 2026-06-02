<template>
  <div class="resources-page">
    <div class="page-header resources">
      <h1>📄 多智能体协作资源生成</h1>
      <p>6个专业智能体并行协作，为你量身打造多模态学习资料</p>
    </div>

    <div class="resources-main">
      <!-- ====== Left: Config panel ====== -->
      <div class="config-panel">
        <!-- Profile-driven topic suggestions -->
        <div v-if="hasProfile && suggestedTopics.length > 0" class="topic-suggestions">
          <div class="suggest-label">🎯 根据画像推荐主题</div>
          <div class="topic-chips">
            <span
              v-for="(t, i) in suggestedTopics"
              :key="i"
              :class="['topic-chip', { active: courseTopic === t }]"
              @click="courseTopic = t"
            >{{ t }}</span>
          </div>
        </div>

        <div class="config-card">
          <div class="config-card-title">⚙️ 生成配置</div>
          <el-form label-position="top" size="default">
            <el-form-item label="课程/知识点主题">
              <el-input
                v-model="courseTopic"
                placeholder="例如：数学应用计算、机器学习"
                size="large"
              />
            </el-form-item>

            <el-form-item label="资源类型（可多选）">
              <div class="type-check-grid">
                <div
                  v-for="rt in resourceTypeOptions"
                  :key="rt.value"
                  :class="['type-check-item', { checked: resourceTypes.includes(rt.value) }]"
                  @click="toggleType(rt.value)"
                >
                  <span class="type-emoji">{{ rt.emoji }}</span>
                  <span class="type-label">{{ rt.short }}</span>
                </div>
              </div>
            </el-form-item>

            <el-form-item v-if="resourceTypes.includes('code_case')" label="技术栈">
              <el-input v-model="techStack" placeholder="例如：Python, Java" />
            </el-form-item>

            <el-form-item label="难度等级">
              <div class="difficulty-selector">
                <span
                  v-for="(d, i) in difficulties"
                  :key="d"
                  :class="['diff-btn', { active: difficultyIndex === i }]"
                  @click="difficultyIndex = i"
                >{{ diffLabels[d] }}</span>
              </div>
            </el-form-item>

            <el-button
              type="primary"
              size="large"
              @click="generate"
              :loading="generating"
              :disabled="!courseTopic || resourceTypes.length === 0"
              style="width:100%; height:44px; font-size:1rem;"
            >
              🚀 开始生成
            </el-button>
          </el-form>
        </div>
      </div>

      <!-- ====== Right: Results ====== -->
      <div class="results-panel">
        <!-- Fresh results -->
        <template v-if="results.length > 0">
          <div class="section-title-row">
            <span>📦 本次生成结果</span>
            <span class="result-count">{{ results.length }} 个资源</span>
          </div>
          <div class="result-cards">
            <div
              v-for="(r, i) in results"
              :key="i"
              :class="['result-card', r.resource_type]"
            >
              <div class="result-card-header">
                <div class="result-card-title">
                  <span class="result-type-badge">{{ typeIcon(r.resource_type) }} {{ typeLabel(r.resource_type) }}</span>
                  <span class="result-name">{{ r.title }}</span>
                </div>
                <div class="result-card-actions">
                  <el-button size="small" text @click="doExport(r)">📥 导出</el-button>
                  <template v-if="r.resource_type === 'video_script' && r.id">
                    <template v-if="!getMeta(r).seedance_video_url && !videoTasks[r.id]?.loading">
                      <el-select v-model="videoDuration" size="small" style="width:72px;">
                        <el-option v-for="d in [5,10,15,20,30]" :key="d" :label="d+'s'" :value="d" />
                      </el-select>
                      <el-button size="small" type="warning" text @click="triggerVideoGen(r)">
                        🎬 生成视频
                      </el-button>
                    </template>
                    <el-button
                      v-if="videoTasks[r.id]?.loading"
                      size="small" type="warning" text :loading="true"
                    >
                      生成中...
                    </el-button>
                    <el-button
                      v-if="getMeta(r).seedance_video_url"
                      size="small" type="success" text
                      @click="playVideo(getMeta(r).seedance_video_url)"
                    >
                      ▶️ 播放
                    </el-button>
                  </template>
                  <el-button size="small" text @click="toggleResult(i)">
                    {{ expandedResults[i] ? '收起' : '展开' }}
                  </el-button>
                </div>
              </div>
              <div v-show="expandedResults[i]" class="result-card-body">
                <div class="markdown-content" v-html="getContent(r)" />
              </div>
            </div>
          </div>
        </template>

        <div v-if="results.length === 0 && historyResources.length === 0" class="empty-state">
          <span style="font-size:3rem;">📭</span>
          <p>配置主题和资源类型后点击生成</p>
        </div>

        <!-- History resources -->
        <template v-if="historyResources.length > 0">
          <el-divider v-if="results.length > 0" />
          <div class="section-title-row">
            <span>📚 历史资源</span>
            <span class="result-count">{{ historyResources.length }} 个</span>
          </div>
          <div class="result-cards">
            <div
              v-for="r in historyResources"
              :key="r.id"
              :class="['result-card', 'history', r.resource_type]"
              :id="`resource-${r.id}`"
            >
              <div class="result-card-header">
                <div class="result-card-title">
                  <span class="result-type-badge">{{ typeIcon(r.resource_type) }} {{ typeLabel(r.resource_type) }}</span>
                  <span class="result-name">{{ r.title }}</span>
                </div>
                <div class="result-card-actions">
                  <el-button size="small" text @click="doExport(r)">📥 导出</el-button>
                  <template v-if="r.resource_type === 'video_script'">
                    <template v-if="!getMeta(r).seedance_video_url && !videoTasks[r.id]?.loading">
                      <el-select v-model="videoDuration" size="small" style="width:72px;">
                        <el-option v-for="d in [5,10,15,20,30]" :key="d" :label="d+'s'" :value="d" />
                      </el-select>
                      <el-button size="small" type="warning" text @click="triggerVideoGen(r)">
                        🎬 生成视频
                      </el-button>
                    </template>
                    <el-button
                      v-if="videoTasks[r.id]?.loading"
                      size="small" type="warning" text :loading="true"
                    >
                      生成中...
                    </el-button>
                    <el-button
                      v-if="getMeta(r).seedance_video_url"
                      size="small" type="success" text
                      @click="playVideo(getMeta(r).seedance_video_url)"
                    >
                      ▶️ 播放
                    </el-button>
                  </template>
                  <el-button
                    v-if="!r._completed"
                    size="small"
                    type="success"
                    text
                    :loading="completingRes === r.id"
                    @click="handleResComplete(r)"
                  >
                    ✓ 完成
                  </el-button>
                  <span v-else class="done-badge">✅</span>
                  <el-button size="small" text @click="toggleHistoryExpand(r.id)">
                    {{ expandedHistory[r.id] ? '收起' : '展开' }}
                  </el-button>
                  <el-button
                    size="small"
                    type="danger"
                    text
                    @click="handleResDelete(r)"
                  >
                    🗑️
                  </el-button>
                </div>
              </div>
              <div v-show="expandedHistory[r.id]" class="result-card-body">
                <div class="markdown-content" v-html="getContent(r)" />
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Video playback dialog -->
    <el-dialog v-model="videoVisible" title="🎬 视频播放" width="720px" destroy-on-close>
      <video v-if="videoUrl" :src="videoUrl" controls autoplay style="width:100%; border-radius:8px;" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useStudentStore } from '../stores/student'
import { generateResources, getResources, generateVideo, checkVideoStatus, deleteResource, completeResource } from '../api'
import MarkdownIt from 'markdown-it'
import mermaid from 'mermaid'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const store = useStudentStore()
const md = new MarkdownIt()

mermaid.initialize({ startOnLoad: false, theme: 'base', securityLevel: 'loose' })

async function renderMermaidBlock(code) {
  // Use DOM-based rendering for reliability
  const container = document.createElement('div')
  container.style.cssText = 'position:fixed;left:-9999px;top:0;'
  container.innerHTML = `<pre class="mermaid">${code}</pre>`
  document.body.appendChild(container)
  try {
    await mermaid.run({ nodes: [container.querySelector('.mermaid')] })
    const svgEl = container.querySelector('svg')
    return svgEl ? svgEl.outerHTML : null
  } finally {
    document.body.removeChild(container)
  }
}

const courseTopic = ref('')
const techStack = ref('')
const resourceTypes = ref(['doc'])
const difficultyIndex = ref(0)
const generating = ref(false)
const results = ref([])
const historyResources = ref([])
const expandedResults = reactive({})
const expandedHistory = reactive({})

const videoTasks = reactive({})
const completingRes = ref(null)
const videoDuration = ref(10)
const videoVisible = ref(false)
const videoUrl = ref('')

function playVideo(url) {
  videoUrl.value = url
  videoVisible.value = true
}

const difficulties = ['easy', 'medium', 'hard']
const diffLabels = { easy: '🟢 入门', medium: '🟡 中等', hard: '🔴 困难' }

const resourceTypeOptions = [
  { value: 'doc', emoji: '📝', short: '课程文档' },
  { value: 'code_case', emoji: '💻', short: '代码案例' },
  { value: 'exercise', emoji: '✏️', short: '练习题' },
  { value: 'reading', emoji: '📖', short: '拓展阅读' },
  { value: 'mindmap', emoji: '🧩', short: '思维导图' },
  { value: 'video_script', emoji: '🎬', short: '视频脚本' },
]

const hasProfile = computed(() => store.hasProfile)
const profile = computed(() => store.profile)

const suggestedTopics = computed(() => {
  if (!profile.value) return []
  const topics = []
  const kb = profile.value?.knowledge_base || {}
  const mf = profile.value?.motivation_factors || {}
  if (mf.primary_goal && mf.primary_goal !== '个人兴趣') topics.push(mf.primary_goal)
  for (const t of kb.target_topics || []) { if (!topics.includes(t)) topics.push(t) }
  for (const w of kb.weak_points || []) { if (!topics.includes(w)) topics.push(w) }
  return topics
})

function typeIcon(type) {
  const map = { doc: '📝', mindmap: '🧩', exercise: '✏️', reading: '📖', video_script: '🎬', code_case: '💻' }
  return map[type] || '📄'
}

function typeLabel(type) {
  const map = { doc: '文档', mindmap: '导图', exercise: '练习', reading: '阅读', video_script: '视频', code_case: '代码' }
  return map[type] || type
}

const renderedMap = reactive(new Map())
let _ridCounter = 0

function assignRid(r) {
  if (!r._rid) r._rid = ++_ridCounter
}

function renderMd(content) { return md.render(content || '') }

function getContent(r) {
  return renderedMap.get(r._rid) || renderMd(r.content)
}

async function renderWithMermaid(r) {
  const raw = r.content || ''
  const key = r._rid
  try {
    let processed = raw
    const blocks = []
    // Match ```mermaid fences (case insensitive on "mermaid")
    processed = processed.replace(/```mermaid\s*\n([\s\S]*?)```/gi, (_, code) => {
      blocks.push(code.trim())
      return `\n%%MERMAID_${blocks.length - 1}%%\n`
    })
    // If no fenced blocks, detect raw mermaid content
    if (blocks.length === 0) {
      const trimmed = raw.trim()
      if (/^(mindmap|graph\s|flowchart|sequenceDiagram|classDiagram|erDiagram|gantt|pie|stateDiagram)/i.test(trimmed)) {
        blocks.push(trimmed)
        processed = `%%MERMAID_0%%`
      } else if (trimmed.includes('root((') || trimmed.includes('root[')) {
        blocks.push(trimmed.startsWith('mindmap') ? trimmed : 'mindmap\n' + trimmed)
        processed = `%%MERMAID_0%%`
      }
    }
    if (blocks.length === 0) { renderedMap.set(key, md.render(raw)); return }
    let html = md.render(processed)
    for (let i = 0; i < blocks.length; i++) {
      const token = `%%MERMAID_${i}%%`
      try {
        const svg = await renderMermaidBlock(blocks[i])
        const replacement = `<div class="mermaid-diagram">${svg}</div>`
        // Replace token whether it's wrapped in <p> tags or not
        if (html.includes(`<p>${token}</p>`)) {
          html = html.replace(`<p>${token}</p>`, replacement)
        } else {
          html = html.replace(token, replacement)
        }
      } catch (e) {
        console.warn('Mermaid render failed for block', i, ':', e.message || e)
        const fallback = `<div class="mermaid-fallback"><pre><code>${blocks[i].replace(/</g, '&lt;')}</code></pre></div>`
        if (html.includes(`<p>${token}</p>`)) {
          html = html.replace(`<p>${token}</p>`, fallback)
        } else {
          html = html.replace(token, fallback)
        }
      }
    }
    renderedMap.set(key, html)
  } catch (e) {
    console.warn('renderWithMermaid error:', e)
    renderedMap.set(key, md.render(raw))
  }
}

function toggleType(val) {
  const idx = resourceTypes.value.indexOf(val)
  if (idx >= 0) resourceTypes.value.splice(idx, 1)
  else resourceTypes.value.push(val)
}

function toggleResult(i) {
  expandedResults[i] = !expandedResults[i]
}

function toggleHistoryExpand(id) {
  expandedHistory[id] = !expandedHistory[id]
}

function doExport(r) {
  if (r.resource_type === 'mindmap') {
    exportMindmapJpg(r)
  } else {
    exportMd(r.content, r.title)
  }
}

function exportMd(content, filename) {
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename.endsWith('.md') ? filename : `${filename}.md`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('已导出')
}

function exportMindmapJpg(r) {
  const renderedHtml = renderedMap.get(r._rid) || ''
  const match = renderedHtml.match(/<svg[\s\S]*?<\/svg>/)
  if (!match) {
    ElMessage.warning('请先展开思维导图以渲染图形，然后再导出')
    return
  }
  const blob = new Blob([match[0]], { type: 'image/svg+xml;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `${r.title || '思维导图'}.svg`
  a.click()
  ElMessage.success('已导出为 SVG')
}

async function generate() {
  if (!store.currentStudentId) { ElMessage.warning('请先创建学生'); return }
  generating.value = true
  try {
    const result = await generateResources({
      student_id: store.currentStudentId,
      resource_types: resourceTypes.value,
      course_topic: courseTopic.value,
      tech_stack: techStack.value,
      difficulty: difficulties[difficultyIndex.value],
    })
    if (result.resources) {
      for (const r of result.resources) assignRid(r)
      results.value = result.resources
      for (const r of result.resources) renderWithMermaid(r)
      ElMessage.success(`成功生成 ${result.resources.length} 个资源！`)
    }
  } catch (e) {
    ElMessage.error('生成失败：' + (e.response?.data?.detail || e.message))
  } finally {
    generating.value = false
  }
}

async function triggerVideoGen(r) {
  const rid = r.id
  videoTasks[rid] = { loading: true, status: '提交中...', videoUrl: null, progress: 0 }
  try {
    const result = await generateVideo(rid, videoDuration.value)
    if (result.success) {
      videoTasks[rid].status = '生成中...'
      ElMessage.success('视频任务已提交')
      pollVideoStatus(rid)
    } else {
      videoTasks[rid].status = '失败'
      videoTasks[rid].loading = false
      ElMessage.error(result.error || '失败')
    }
  } catch (e) {
    videoTasks[rid].status = '失败'
    videoTasks[rid].loading = false
    ElMessage.error('视频生成失败：' + (e.response?.data?.error || e.response?.data?.detail || e.message || '未知错误'))
  }
}

async function pollVideoStatus(rid) {
  const t = videoTasks[rid]
  if (!t) return
  try {
    const result = await checkVideoStatus(rid)
    t.progress = result.progress || 0
    t.status = result.status === 'completed' ? '完成' : result.status
    if (result.video_url) {
      t.videoUrl = result.video_url
      t.loading = false
      t.status = '完成'
      // Also update the resource's metadata so the template shows the video
      const r = [...results.value, ...historyResources.value].find(x => x.id === rid)
      if (r) {
        if (!r.metadata) r.metadata = {}
        r.metadata.seedance_video_url = result.video_url
      }
      ElMessage.success('视频生成完成！')
    } else if (result.status === 'failed') {
      t.loading = false
      t.status = '失败'
    } else {
      setTimeout(() => pollVideoStatus(rid), 5000)
    }
  } catch {
    t.loading = false
    t.status = '查询失败'
  }
}

function getMeta(r) { return r.metadata || {} }

async function handleResComplete(r) {
  try {
    await ElMessageBox.confirm(
      `确认已完成「${r.title}」的学习？该知识点将更新到画像中。`,
      '确认完成',
      { confirmButtonText: '确认', cancelButtonText: '取消', type: 'success' }
    )
  } catch { return }

  completingRes.value = r.id
  try {
    const result = await completeResource(store.currentStudentId, r.id)
    if (result.ok) {
      r._completed = true
      ElMessage.success('已完成！画像已更新')
      await store.loadProfile()
    }
  } catch (e) {
    ElMessage.error('操作失败：' + (e.response?.data?.detail || e.message))
  } finally {
    completingRes.value = null
  }
}

async function handleResDelete(r) {
  try {
    await ElMessageBox.confirm(
      `确认删除「${r.title}」？此操作不可恢复。`,
      '删除资源',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch { return }

  try {
    await deleteResource(r.id, store.currentStudentId)
    historyResources.value = historyResources.value.filter(x => x.id !== r.id)
    ElMessage.success('已删除')
  } catch (e) {
    ElMessage.error('删除失败：' + (e.response?.data?.detail || e.message))
  }
}

onMounted(async () => {
  if (store.currentStudentId) {
    try {
      const data = await getResources(store.currentStudentId)
      historyResources.value = data.resources || []
      for (const r of historyResources.value) { assignRid(r); renderWithMermaid(r) }
      for (const r of historyResources.value) {
        const meta = getMeta(r)
        if (meta.seedance_video_url) {
          videoTasks[r.id] = { loading: false, status: '完成', videoUrl: meta.seedance_video_url, progress: 100 }
        } else if (meta.seedance_task_id && meta.seedance_status !== 'failed') {
          videoTasks[r.id] = { loading: true, status: meta.seedance_status || 'queued', videoUrl: null, progress: 0 }
          pollVideoStatus(r.id)
        }
      }
      const targetId = route.query.id
      if (targetId) {
        expandedHistory[Number(targetId)] = true
        await nextTick()
        const el = document.getElementById(`resource-${targetId}`)
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' })
          el.classList.add('resource-highlight')
          setTimeout(() => el.classList.remove('resource-highlight'), 3000)
        }
      }
    } catch { /* ignore */ }
  }
})
</script>

<style scoped>
.resources-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100px);
  padding: 0 1.2rem 0.8rem;
}

.resources-main {
  flex: 1;
  display: flex;
  gap: 1rem;
  min-height: 0;
}

/* ===== Left: Config ===== */
.config-panel {
  width: 300px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  overflow-y: auto;
}

.topic-suggestions {
  background: linear-gradient(135deg, #FBF7F0, #F5EDE0);
  border-radius: 10px;
  padding: 0.6rem 0.8rem;
  border: 1px solid #E8E0D5;
}

.suggest-label {
  font-size: 0.75rem;
  color: #7A6E63;
  margin-bottom: 0.35rem;
}

.topic-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.topic-chip {
  font-size: 0.75rem;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  background: #FFFEF9;
  color: #5C4F42;
  border: 1px solid #D4C4A8;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.topic-chip:hover { background: #F5EDE0; border-color: #C8A25C; }
.topic-chip.active {
  background: rgba(200,162,92,0.12);
  border-color: #C8A25C;
  color: #8B6F3D;
  font-weight: 600;
}

.config-card {
  background: #FFFEF9;
  border-radius: 8px;
  padding: 0.85rem 1rem;
  box-shadow: 0 1px 4px rgba(60, 48, 40, 0.05);
  flex: 1;
  border: 1px solid #E8E0D5;
}

.config-card-title {
  font-weight: 700;
  font-size: 0.9rem;
  color: #3C3028;
  margin-bottom: 0.5rem;
}

/* Type check grid */
.type-check-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.4rem;
}

.type-check-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.45rem 0.6rem;
  border-radius: 6px;
  border: 1.5px solid #D4C4A8;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.8rem;
  user-select: none;
  background: #FBF7F0;
}

.type-check-item:hover { border-color: #C8A25C; background: #FFFEF9; }
.type-check-item.checked {
  border-color: #C8A25C;
  background: rgba(200,162,92,0.08);
  box-shadow: 0 0 0 2px rgba(200,162,92,0.1);
}

.type-emoji { font-size: 1rem; }
.type-label { font-weight: 500; color: #3C3028; }

/* Difficulty */
.difficulty-selector {
  display: flex;
  gap: 0.4rem;
}

.diff-btn {
  flex: 1;
  text-align: center;
  padding: 0.5rem 0.3rem;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 500;
  border: 1.5px solid #D4C4A8;
  cursor: pointer;
  transition: all 0.2s;
  color: #7A6E63;
  white-space: nowrap;
  background: #FBF7F0;
}

.diff-btn:hover { border-color: #C8A25C; background: #FFFEF9; }
.diff-btn.active {
  border-color: #C8A25C;
  background: rgba(200,162,92,0.08);
  color: #8B6F3D;
  font-weight: 600;
}

/* ===== Right: Results ===== */
.results-panel {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  min-width: 0;
}

.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 700;
  font-size: 0.88rem;
  color: #3C3028;
  flex-shrink: 0;
}

.result-count {
  font-size: 0.72rem;
  color: #A89880;
  font-weight: 400;
}

.result-cards {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.result-card {
  background: #FFFEF9;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(60, 48, 40, 0.05);
  overflow: hidden;
  border: 1px solid #E8E0D5;
  border-left: 4px solid #D4C4A8;
}

.result-card.doc { border-left-color: #C8A25C; }
.result-card.mindmap { border-left-color: #B8934F; }
.result-card.exercise { border-left-color: #3D7A5C; }
.result-card.reading { border-left-color: #7FA08E; }
.result-card.video_script { border-left-color: #722F37; }
.result-card.code_case { border-left-color: #5D7A8A; }

.result-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.45rem 0.7rem;
  gap: 0.4rem;
  background: #FBF7F0;
}

.result-card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
  flex: 1;
}

.result-type-badge {
  font-size: 0.72rem;
  font-weight: 600;
  color: #7A6E63;
  white-space: nowrap;
  flex-shrink: 0;
}

.result-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #3C3028;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-card-actions {
  display: flex;
  gap: 0.2rem;
  flex-shrink: 0;
}

.result-card-body {
  border-top: 1px solid #E8E0D5;
  padding: 0.8rem 1rem;
  overflow-y: auto;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #A89880;
  font-size: 0.85rem;
}

/* Markdown in results */
.result-card-body :deep(.markdown-content h1),
.result-card-body :deep(.markdown-content h2),
.result-card-body :deep(.markdown-content h3) {
  font-size: 1rem;
  margin: 0.5rem 0 0.3rem;
}

.result-card-body :deep(.markdown-content p) { margin: 0.3rem 0; font-size: 0.85rem; line-height: 1.7; }
.result-card-body :deep(.markdown-content code) {
  background: #F5EDE0;
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #8B6F3D;
}
.result-card-body :deep(.markdown-content pre) {
  background: #2d2d2d !important;
  color: #f8f8f2;
  padding: 0.8rem;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 0.78rem;
}
.result-card-body :deep(.markdown-content pre code) {
  background: none;
  color: #f8f8f2;
  padding: 0;
}

.done-badge { font-size: 0.85rem; }

/* Mermaid diagram */
.result-card-body :deep(.mermaid-diagram) {
  display: flex;
  justify-content: flex-start;
  padding: 0.5rem 0;
  overflow-x: auto;
  overflow-y: hidden;
  min-height: 200px;
  background: #faf7f0;
  border-radius: 8px;
}

.result-card-body :deep(.mermaid-diagram svg) {
  max-width: none;
  min-width: 100%;
  height: auto;
}

.result-card-body :deep(.mermaid-fallback) {
  padding: 0.5rem;
  background: #fff3cd;
  border-radius: 8px;
  overflow-x: auto;
}

.result-card-body :deep(.mermaid-fallback pre) {
  margin: 0;
  font-size: 0.8rem;
}
</style>
