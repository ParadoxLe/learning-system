<template>
  <div class="kg-page">
    <div class="page-header kg">
      <h1>🕸️ 知识图谱</h1>
      <p>基于学习画像自动构建 · 展示知识点关联与学习进度</p>
    </div>

    <div class="kg-main">
      <!-- Graph area -->
      <div class="kg-graph-area">
        <div ref="graphRef" class="kg-chart"></div>

        <!-- Legend -->
        <div class="kg-legend">
          <span v-for="cat in legendCats" :key="cat.name" class="legend-item">
            <span class="legend-dot" :style="{ background: cat.color }"></span>
            {{ cat.label }}
          </span>
        </div>

        <!-- Controls -->
        <div class="kg-controls">
          <el-button size="small" @click="resetView" circle title="重置视图">↺</el-button>
          <el-button size="small" @click="toggleLabels" circle title="切换标签">
            {{ showLabels ? '🏷️' : '◉' }}
          </el-button>
        </div>
      </div>

      <!-- Side info panel -->
      <div class="kg-side">
        <div class="side-card" v-if="selectedNode">
          <div class="side-card-header">
            <span class="node-indicator" :style="{ background: selectedNode.color }"></span>
            <span class="node-title">{{ selectedNode.name }}</span>
          </div>
          <div class="side-card-meta">
            <div class="meta-row">
              <span class="meta-label">类型</span>
              <span class="meta-val">{{ catLabel(selectedNode.category) }}</span>
            </div>
            <div class="meta-row" v-if="selectedNode.connections !== undefined">
              <span class="meta-label">关联节点</span>
              <span class="meta-val">{{ selectedNode.connections }}</span>
            </div>
          </div>
          <div class="side-card-related" v-if="relatedNodes.length > 0">
            <div class="related-title">关联节点</div>
            <div
              v-for="rn in relatedNodes"
              :key="rn.id"
              class="related-item"
              @click="highlightNode(rn.id)"
            >
              <span class="related-dot" :style="{ background: rn.color }"></span>
              <span class="related-name">{{ rn.name }}</span>
              <span class="related-cat">{{ catLabel(rn.category) }}</span>
            </div>
          </div>
        </div>

        <!-- Summary -->
        <div class="side-card" v-if="summary">
          <div class="side-card-header">
            <span>📋 图谱概览</span>
          </div>

          <!-- Mastery ring -->
          <div class="mastery-ring-wrap">
            <svg class="mastery-ring" viewBox="0 0 100 100">
              <circle class="ring-bg" cx="50" cy="50" r="42"
                fill="none" stroke="#E8DED0" stroke-width="8" />
              <circle class="ring-fill" cx="50" cy="50" r="42"
                fill="none"
                :stroke="masteryColor"
                stroke-width="8"
                stroke-linecap="round"
                :stroke-dasharray="masteryDasharray"
                :stroke-dashoffset="0"
                transform="rotate(-90 50 50)"
                style="transition: stroke-dasharray 0.8s ease;" />
              <text x="50" y="48" text-anchor="middle" class="ring-pct">
                {{ summary.mastery_pct || 0 }}%
              </text>
              <text x="50" y="64" text-anchor="middle" class="ring-label">
                掌握率
              </text>
            </svg>
          </div>

          <div class="summary-grid">
            <div class="summary-item mastered">
              <span class="summary-num">{{ summary.mastered_count || 0 }}</span>
              <span class="summary-lbl">已掌握</span>
            </div>
            <div class="summary-item weak">
              <span class="summary-num">{{ summary.weak_count || 0 }}</span>
              <span class="summary-lbl">薄弱点</span>
            </div>
            <div class="summary-item target">
              <span class="summary-num">{{ summary.target_count || 0 }}</span>
              <span class="summary-lbl">目标</span>
            </div>
          </div>

          <div class="mastery-formula">
            <span class="formula-text">
              {{ summary.mastered_count || 0 }} / {{ summary.total_topics || 0 }} 个知识点已掌握
            </span>
          </div>

          <div class="summary-level" v-if="summary.level">
            当前水平：<b>{{ levelLabel(summary.level) }}</b>
          </div>
        </div>

        <!-- Quiz trigger -->
        <div class="side-card quiz-trigger-card" v-if="summary && (summary.weak_count > 0 || summary.target_count > 0)">
          <div class="quiz-trigger-top">
            <div class="quiz-trigger-icon">✏️</div>
            <div class="quiz-trigger-info">
              <div class="quiz-trigger-title">刷题巩固</div>
              <div class="quiz-trigger-sub">
                针对 <b>{{ summary.weak_count || 0 }}</b> 个薄弱点 · 共 <b>5</b> 题
              </div>
            </div>
            <span v-if="lastScore !== null" class="quiz-score-badge" :class="lastScore >= 80 ? 'good' : lastScore < 50 ? 'poor' : 'ok'">
              上次 {{ lastScore }}分
            </span>
          </div>

          <!-- Weak point tags -->
          <div class="quiz-trigger-tags" v-if="weakTags.length > 0">
            <span v-for="t in weakTags" :key="t" class="quiz-weak-tag">{{ t }}</span>
          </div>

          <el-button type="primary" size="default" @click="startQuiz" class="quiz-start-btn">
            🎯 开始刷题
          </el-button>
        </div>

        <el-empty v-if="!graphData && !loading" description="请先完成学习画像构建" :image-size="60" />
      </div>
    </div>

    <!-- ====== Quiz Modal Overlay ====== -->
    <teleport to="body">
      <div v-if="quizModal" class="quiz-overlay" @click.self="closeQuiz">
        <div class="quiz-modal">
          <!-- Close button -->
          <button class="quiz-close" @click="closeQuiz">✕</button>

          <!-- Loading state -->
          <div v-if="quizLoading" class="quiz-modal-loading">
            <span class="loading-spin">⏳</span>
            <span>AI 正在为你出题...</span>
          </div>

          <!-- Question card -->
          <template v-if="quiz && !quizResult && !quizLoading">
            <div class="quiz-progress">
              <div class="quiz-progress-bar">
                <div class="quiz-progress-fill" :style="{ width: ((quizIndex + 1) / quiz.length * 100) + '%' }"></div>
              </div>
              <span class="quiz-progress-text">{{ quizIndex + 1 }} / {{ quiz.length }}</span>
            </div>

            <div class="quiz-card-inner">
              <div class="quiz-card-topic">{{ currentQ.topic }}</div>
              <div class="quiz-card-question">{{ currentQ.question }}</div>

              <div class="quiz-card-options">
                <div
                  v-for="opt in currentQ.options"
                  :key="opt.key"
                  :class="['quiz-card-option', { selected: userAnswers[currentQ.id] === opt.key }]"
                  @click="userAnswers[currentQ.id] = opt.key"
                >
                  <span class="qco-key">{{ opt.key }}</span>
                  <span class="qco-text">{{ opt.text }}</span>
                </div>
              </div>

              <div class="quiz-nav">
                <el-button
                  v-if="quizIndex > 0"
                  size="default"
                  @click="quizIndex--"
                >← 上一题</el-button>
                <div class="quiz-nav-spacer"></div>
                <el-button
                  v-if="quizIndex < quiz.length - 1"
                  type="primary"
                  size="default"
                  @click="quizIndex++"
                  :disabled="!userAnswers[currentQ.id]"
                >下一题 →</el-button>
                <el-button
                  v-if="quizIndex === quiz.length - 1"
                  type="primary"
                  size="default"
                  @click="submitAnswers"
                  :disabled="!allAnswered"
                  style="background:#3D7A5C;border-color:#3D7A5C;"
                >📝 提交答卷</el-button>
              </div>
            </div>
          </template>

          <!-- Results -->
          <template v-if="quizResult && !quizLoading">
            <div class="quiz-result-header">
              <span class="quiz-result-score" :class="quizScore >= 80 ? 'good' : quizScore < 50 ? 'poor' : 'ok'">
                {{ quizScore >= 80 ? '🎉' : quizScore < 50 ? '😞' : '👍' }}
                {{ quizResult.score }} / {{ quizResult.total }}
              </span>
              <span class="quiz-result-pct">正确率 {{ quizResult.score_pct }}%</span>
            </div>

            <div class="quiz-result-list">
              <div v-for="r in quizResult.results" :key="r.id" :class="['quiz-result-item', r.is_correct ? 'correct' : 'wrong']">
                <div class="result-q-title">
                  <span>{{ r.is_correct ? '✅' : '❌' }}</span>
                  <span>{{ r.id }}. {{ r.question }}</span>
                </div>
                <div class="result-answers">
                  <span v-if="!r.is_correct">你的答案：<b class="wrong-ans">{{ r.user_answer || '未答' }}</b> → </span>
                  <span>正确答案：<b class="correct-ans">{{ r.correct_answer }}</b></span>
                </div>
                <div class="result-explanation">{{ r.explanation }}</div>
              </div>
            </div>

            <div class="quiz-result-actions">
              <el-button size="default" @click="resetQuiz">🔄 重新出题</el-button>
              <el-button size="default" type="primary" @click="closeQuiz">✓ 完成</el-button>
            </div>
          </template>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed, reactive, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useStudentStore } from '../stores/student'
import { getKnowledgeGraph, generateQuiz, submitQuiz } from '../api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const store = useStudentStore()
const loading = ref(false)
const graphData = ref(null)
const selectedNode = ref(null)
const relatedNodes = ref([])
const showLabels = ref(true)

const graphRef = ref(null)
let chart = null

// Quiz state
const quizModal = ref(false)
const quizLoading = ref(false)
const quiz = ref(null)
const quizResult = ref(null)
const quizIndex = ref(0)
const lastScore = ref(null)
const userAnswers = reactive({})

const currentQ = computed(() => {
  if (!quiz.value || quiz.value.length === 0) return null
  return quiz.value[quizIndex.value] || quiz.value[0]
})

const quizScore = computed(() => quizResult.value?.score_pct ?? null)
const allAnswered = computed(() => {
  if (!quiz.value) return false
  return quiz.value.every(q => userAnswers[q.id] !== undefined && userAnswers[q.id] !== '')
})

const LEVEL = { beginner: '入门级', intermediate: '中级', advanced: '高级' }

const CAT_MAP = {
  mastered: '已掌握',
  weak: '薄弱点',
  target: '目标主题',
  core: '核心',
  style: '认知风格',
  modality: '学习模态',
  error: '易错模式',
  goal: '学习目标',
}

const legendCats = [
  { name: 'mastered', label: '已掌握', color: '#3D7A5C' },
  { name: 'weak', label: '薄弱点', color: '#722F37' },
  { name: 'target', label: '目标', color: '#C8A25C' },
  { name: 'core', label: '核心', color: '#5D3A2C' },
  { name: 'style', label: '认知', color: '#7FA08E' },
  { name: 'modality', label: '模态', color: '#5D7A8A' },
  { name: 'error', label: '易错', color: '#A0403D' },
  { name: 'goal', label: '目标', color: '#B8934F' },
]

const summary = computed(() => graphData.value?.summary || null)
const weakTags = computed(() => {
  const p = store.profile
  if (!p) return []
  const kb = p.knowledge_base || {}
  return (kb.weak_points || []).slice(0, 4)
})

const masteryPct = computed(() => summary.value?.mastery_pct || 0)
const masteryDasharray = computed(() => {
  const circum = 2 * Math.PI * 42  // ~263.9
  const filled = (masteryPct.value / 100) * circum
  return `${filled} ${circum}`
})
const masteryColor = computed(() => {
  const p = masteryPct.value
  if (p >= 80) return '#3D7A5C'
  if (p < 40) return '#722F37'
  return '#C8A25C'
})

function catLabel(c) { return CAT_MAP[c] || c }
function levelLabel(l) { return LEVEL[l] || l }

function buildChart() {
  if (!graphRef.value || !graphData.value) return
  if (!chart) chart = echarts.init(graphRef.value)

  const { nodes, edges, categories } = graphData.value

  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (p) => {
        if (p.dataType === 'node') {
          if (p.data.category === 'core' && summary.value) {
            return `<b>${p.name}</b><br/>掌握率：<b style="color:${masteryColor.value}">${masteryPct.value}%</b><br/>已掌握 ${summary.value.mastered_count} · 薄弱 ${summary.value.weak_count} · 目标 ${summary.value.target_count}`
          }
          return `<b>${p.name}</b><br/>类型：${catLabel(p.data.category)}`
        }
        return `${p.data.source} → ${p.data.target}<br/>${p.data.label || ''}`
      },
    },
    legend: { show: false },
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      draggable: true,
      categories,
      data: nodes,
      edges: edges,
      animation: true,
      force: {
        repulsion: 750,
        gravity: 0.06,
        edgeLength: [200, 420],
        layoutAnimation: true,
      },
      zoom: 1.6,
      label: {
        show: showLabels.value,
        position: 'right',
        fontSize: 11,
        color: '#3C3028',
        formatter: (p) => p.name.length > 6 ? p.name.slice(0, 6) + '…' : p.name,
      },
      emphasis: {
        focus: 'adjacency',
        label: { fontSize: 14, fontWeight: 'bold' },
        itemStyle: { shadowBlur: 16, shadowColor: 'rgba(60,48,40,0.3)' },
      },
      lineStyle: {
        color: '#D4C4A8',
        curveness: 0.2,
        opacity: 0.6,
      },
      edgeSymbol: ['none', 'none'],
      edgeLabel: {
        show: false,
        fontSize: 9,
        color: '#A89880',
      },
    }],
  }, true)

  // Click handler
  chart.off('click')
  chart.on('click', (params) => {
    if (params.dataType === 'node') {
      const n = params.data
      const connectedEdges = edges.filter(
        e => e.source === n.id || e.target === n.id
      )
      const connectedIds = new Set()
      connectedEdges.forEach(e => {
        if (e.source !== n.id) connectedIds.add(e.source)
        if (e.target !== n.id) connectedIds.add(e.target)
      })
      const related = nodes
        .filter(nd => connectedIds.has(nd.id) && nd.id !== n.id)
        .map(nd => ({
          id: nd.id,
          name: nd.name,
          category: nd.category,
          color: nd.itemStyle?.color || '#999',
        }))

      selectedNode.value = {
        id: n.id,
        name: n.name,
        category: n.category,
        color: n.itemStyle?.color || '#999',
        connections: connectedEdges.length,
      }
      relatedNodes.value = related
    }
  })
}

function highlightNode(nodeId) {
  if (!chart) return
  chart.dispatchAction({ type: 'highlight', seriesIndex: 0 })
  chart.dispatchAction({ type: 'showTip', seriesIndex: 0, dataIndex: nodeId })
}

function resetView() {
  if (!chart) return
  chart.dispatchAction({ type: 'restore' })
  chart.dispatchAction({ type: 'unselect', seriesIndex: 0 })
  selectedNode.value = null
  relatedNodes.value = []
  buildChart()
}

function toggleLabels() {
  showLabels.value = !showLabels.value
  if (!chart) return
  chart.setOption({
    series: [{ label: { show: showLabels.value } }],
  })
}

async function loadData() {
  if (!store.currentStudentId) return
  loading.value = true
  try {
    const result = await getKnowledgeGraph(store.currentStudentId)
    if (result.nodes && result.nodes.length > 0) {
      graphData.value = result
      nextTick(() => buildChart())
    } else {
      graphData.value = null
    }
  } catch (e) {
    ElMessage.error('加载知识图谱失败：' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

async function startQuiz() {
  if (!store.currentStudentId) return
  quizModal.value = true
  quizLoading.value = true
  quizResult.value = null
  quizIndex.value = 0
  Object.keys(userAnswers).forEach(k => delete userAnswers[k])
  try {
    const result = await generateQuiz(store.currentStudentId, 5)
    quiz.value = result.quiz?.questions || []
    if (quiz.value.length === 0) {
      ElMessage.warning('暂无可生成的题目，请先完善学习画像')
      quizModal.value = false
    }
  } catch (e) {
    ElMessage.error('出题失败：' + (e.response?.data?.detail || e.message))
    quizModal.value = false
  } finally {
    quizLoading.value = false
  }
}

async function submitAnswers() {
  if (!store.currentStudentId || !quiz.value) return
  try {
    const result = await submitQuiz(store.currentStudentId, { ...userAnswers }, quiz.value)
    quizResult.value = result
    lastScore.value = result.score_pct
  } catch (e) {
    ElMessage.error('提交失败：' + (e.response?.data?.detail || e.message))
  }
}

function resetQuiz() {
  quizResult.value = null
  quizIndex.value = 0
  Object.keys(userAnswers).forEach(k => delete userAnswers[k])
  // Regenerate
  startQuiz()
}

function closeQuiz() {
  quizModal.value = false
  quiz.value = null
  quizResult.value = null
  quizIndex.value = 0
  Object.keys(userAnswers).forEach(k => delete userAnswers[k])
}

function handleResize() {
  chart?.resize()
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  if (store.hasProfile) loadData()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>

<style scoped>
.kg-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100px);
  padding: 0.6rem 1.2rem 0.8rem;
}

.kg-main {
  flex: 1;
  display: flex;
  gap: 1rem;
  min-height: 0;
}

/* Graph area */
.kg-graph-area {
  flex: 1;
  position: relative;
  background: #FFFEF9;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(60, 48, 40, 0.05);
  border: 1px solid #E8E0D5;
  min-width: 0;
}

.kg-chart {
  width: 100%;
  height: 100%;
}

.kg-legend {
  position: absolute;
  top: 12px;
  left: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  background: rgba(255, 254, 249, 0.85);
  padding: 0.5rem 0.8rem;
  border-radius: 6px;
  border: 1px solid #E8E0D5;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.7rem;
  color: #7A6E63;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.kg-controls {
  position: absolute;
  bottom: 16px;
  right: 16px;
  display: flex;
  gap: 0.3rem;
}

/* Side panel */
.kg-side {
  width: 300px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  overflow-y: auto;
}

.side-card {
  background: #FFFEF9;
  border-radius: 10px;
  padding: 0.7rem 0.9rem;
  box-shadow: 0 1px 4px rgba(60, 48, 40, 0.05);
  border: 1px solid #E8E0D5;
}

.side-card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  font-size: 0.85rem;
  color: #3C3028;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #E8DED0;
  margin-bottom: 0.4rem;
}

.node-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.node-title {
  font-size: 0.9rem;
}

.side-card-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meta-label {
  font-size: 0.72rem;
  color: #A89880;
}

.meta-val {
  font-size: 0.78rem;
  font-weight: 600;
  color: #5C5045;
}

.side-card-related {
  border-top: 1px solid #E8DED0;
  padding-top: 0.4rem;
}

.related-title {
  font-size: 0.72rem;
  color: #A89880;
  margin-bottom: 0.3rem;
}

.related-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.4rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
}

.related-item:hover {
  background: #FBF7F0;
}

.related-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.related-name {
  flex: 1;
  font-size: 0.78rem;
  color: #3C3028;
}

.related-cat {
  font-size: 0.65rem;
  color: #A89880;
}

/* Summary */
.summary-grid {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.summary-item {
  flex: 1;
  text-align: center;
  padding: 0.4rem 0.3rem;
  border-radius: 6px;
}

.summary-item.mastered { background: #f3f8f5; }
.summary-item.weak { background: #fdf5f5; }
.summary-item.target { background: rgba(200, 162, 92, 0.08); }

.summary-num {
  display: block;
  font-size: 1.3rem;
  font-weight: 800;
}

.summary-item.mastered .summary-num { color: #3D7A5C; }
.summary-item.weak .summary-num { color: #722F37; }
.summary-item.target .summary-num { color: #C8A25C; }

.summary-lbl {
  font-size: 0.65rem;
  color: #7A6E63;
}

.summary-level {
  font-size: 0.75rem;
  color: #7A6E63;
  text-align: center;
  padding-top: 0.3rem;
  border-top: 1px solid #E8DED0;
}

.summary-level b {
  color: #C8A25C;
}

/* Mastery ring */
.mastery-ring-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.mastery-ring {
  width: 120px;
  height: 120px;
}

.ring-pct {
  font-size: 1.5rem;
  font-weight: 800;
  fill: #3C3028;
}

.ring-label {
  font-size: 0.62rem;
  fill: #A89880;
}

.mastery-formula {
  text-align: center;
  margin-bottom: 0.5rem;
}

.formula-text {
  font-size: 0.7rem;
  color: #7A6E63;
}

/* Quiz trigger card */
.quiz-trigger-card {
  background: linear-gradient(160deg, #FFFEF9 0%, #FBF7F0 50%, #F9F3E8 100%);
  border: 1px solid #E8E0D5;
}

.quiz-trigger-top {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.5rem;
}

.quiz-trigger-icon {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, #C8A25C, #B8934F);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(200,162,92,0.25);
}

.quiz-trigger-info {
  flex: 1;
  min-width: 0;
}

.quiz-trigger-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #3C3028;
  line-height: 1.3;
}

.quiz-trigger-sub {
  font-size: 0.68rem;
  color: #A89880;
  margin-top: 1px;
}

.quiz-trigger-sub b {
  color: #C8A25C;
  font-weight: 700;
}

/* Weak tags */
.quiz-trigger-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin-bottom: 0.6rem;
  padding: 0.4rem 0.5rem;
  background: rgba(200,162,92,0.05);
  border-radius: 6px;
  border: 1px dashed rgba(200,162,92,0.15);
}

.quiz-weak-tag {
  font-size: 0.64rem;
  background: rgba(114,47,55,0.08);
  color: #8B4A52;
  padding: 0.12rem 0.5rem;
  border-radius: 10px;
  font-weight: 500;
}

/* Score badge */
.quiz-score-badge {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  flex-shrink: 0;
}
.quiz-score-badge.good { color: #3D7A5C; background: #EDF7F1; }
.quiz-score-badge.ok { color: #B8934F; background: rgba(200,162,92,0.1); }
.quiz-score-badge.poor { color: #722F37; background: #FDF0F0; }

.quiz-start-btn {
  width: 100%;
  font-weight: 600;
  height: 36px;
}

/* Quiz modal overlay */
.quiz-overlay {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(30, 20, 14, 0.55);
  backdrop-filter: blur(4px);
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.quiz-modal {
  position: relative;
  width: 600px;
  max-width: 92vw;
  max-height: 85vh;
  background: #FFFEF9;
  border-radius: 14px;
  box-shadow: 0 12px 48px rgba(30, 20, 14, 0.25);
  overflow-y: auto;
  padding: 2rem 2rem 1.5rem;
  border: 1px solid #E8E0D5;
}

.quiz-close {
  position: absolute;
  top: 12px;
  right: 14px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid #E8DED0;
  background: #FBF7F0;
  color: #A89880;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}
.quiz-close:hover { background: #F5EDE0; color: #3C3028; }

.quiz-modal-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.8rem;
  padding: 3rem 1rem;
  font-size: 1rem;
  color: #7A6E63;
}

.loading-spin {
  animation: spin 1.2s linear infinite;
  font-size: 2.5rem;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Progress bar */
.quiz-progress {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 1.5rem;
}

.quiz-progress-bar {
  flex: 1;
  height: 5px;
  background: #E8DED0;
  border-radius: 3px;
  overflow: hidden;
}

.quiz-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #C8A25C, #B8934F);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.quiz-progress-text {
  font-size: 0.78rem;
  font-weight: 600;
  color: #7A6E63;
  white-space: nowrap;
}

/* Question card */
.quiz-card-inner {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.quiz-card-topic {
  display: inline-block;
  align-self: flex-start;
  font-size: 0.7rem;
  color: #C8A25C;
  background: rgba(200,162,92,0.08);
  border: 1px solid rgba(200,162,92,0.2);
  padding: 0.15rem 0.6rem;
  border-radius: 12px;
}

.quiz-card-question {
  font-size: 1.1rem;
  font-weight: 700;
  color: #3C3028;
  line-height: 1.7;
}

.quiz-card-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.quiz-card-option {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border: 2px solid #E8E0D5;
  background: #FBF7F0;
  cursor: pointer;
  transition: all 0.18s;
  font-size: 0.92rem;
  color: #5C5045;
  line-height: 1.5;
}
.quiz-card-option:hover { border-color: #D4C4A8; background: #F5EDE0; }
.quiz-card-option.selected {
  border-color: #C8A25C;
  background: rgba(200,162,92,0.08);
  box-shadow: 0 0 0 1px rgba(200,162,92,0.2);
}

.qco-key {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #E8DED0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
  color: #7A6E63;
  transition: all 0.18s;
}
.quiz-card-option.selected .qco-key {
  background: #C8A25C;
  color: #fff;
}

.qco-text { flex: 1; }

/* Navigation */
.quiz-nav {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-top: 0.5rem;
}

.quiz-nav-spacer { flex: 1; }

/* Result in modal */
.quiz-result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid #E8DED0;
}

.quiz-result-score {
  font-size: 1.5rem;
  font-weight: 800;
}
.quiz-result-score.good { color: #3D7A5C; }
.quiz-result-score.ok { color: #C8A25C; }
.quiz-result-score.poor { color: #722F37; }

.quiz-result-pct {
  font-size: 0.82rem;
  color: #7A6E63;
}

.quiz-result-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 50vh;
  overflow-y: auto;
  margin-bottom: 0.8rem;
}

.quiz-result-item {
  padding: 0.5rem 0.6rem;
  border-radius: 8px;
  font-size: 0.78rem;
}

.quiz-result-item.correct {
  background: #f3f8f5;
  border-left: 3px solid #3D7A5C;
}

.quiz-result-item.wrong {
  background: #fdf5f5;
  border-left: 3px solid #722F37;
}

.result-q-title {
  display: flex;
  align-items: flex-start;
  gap: 0.3rem;
  font-weight: 600;
  color: #3C3028;
  margin-bottom: 0.2rem;
  line-height: 1.4;
}

.result-answers {
  font-size: 0.72rem;
  color: #7A6E63;
  margin-bottom: 0.15rem;
}

.wrong-ans { color: #A0403D; }
.correct-ans { color: #3D7A5C; }

.result-explanation {
  font-size: 0.72rem;
  color: #A89880;
  line-height: 1.5;
  margin-top: 0.15rem;
  padding-top: 0.15rem;
  border-top: 1px dashed #E8DED0;
}

.quiz-result-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}
</style>
