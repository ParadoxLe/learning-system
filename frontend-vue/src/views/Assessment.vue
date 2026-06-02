<template>
  <div class="assessment-page">
    <div class="page-header assessment">
      <h1>📊 学习效果评估</h1>
      <p>基于学习画像自动评估 · 学习活动完成后自动更新</p>
    </div>

    <div class="assessment-main">
      <!-- ====== Left: Charts ====== -->
      <div class="charts-area">
        <!-- Bar chart: 各维度得分 -->
        <div class="chart-card">
          <div class="chart-card-header">
            <span>📊 能力维度得分</span>
            <span v-if="loading" style="font-size:0.75rem; color:#7A6E63;">评估中...</span>
          </div>
          <div ref="barChartRef" class="chart-box"></div>
        </div>

        <!-- Donut chart: 综合能力分布 -->
        <div class="chart-card">
          <div class="chart-card-header">
            <span>🎯 综合能力分布</span>
            <span v-if="overall > 0" class="overall-badge" :style="{ color: scoreColor }">
              {{ overall }}分
            </span>
          </div>
          <div ref="donutChartRef" class="chart-box donut"></div>
        </div>
      </div>

      <!-- ====== Right: Recommendations ====== -->
      <div class="side-area">
        <!-- Profile summary -->
        <div v-if="store.hasProfile" class="profile-summary">
          <div class="summary-row">
            <span class="summary-label">📌 水平</span>
            <span class="summary-val">{{ LEVEL[kb.level] || '未知' }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">🎯 目标</span>
            <span class="summary-val">{{ mf.primary_goal || '未设定' }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">⏱️ 周学时</span>
            <span class="summary-val">{{ lp.weekly_hours || '未知' }}h</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">🧠 风格</span>
            <span class="summary-val">{{ STYLE[cs.primary_style] || '未知' }}</span>
          </div>
        </div>
        <div v-else class="profile-summary empty">
          <span>⚠️ 请先完成学习画像构建</span>
        </div>

        <!-- Recommendations panel -->
        <template v-if="assessment">
          <!-- Books -->
          <div v-if="books.length > 0" class="recommend-section">
            <div class="section-label">📚 推荐书籍</div>
            <div v-for="(b, i) in books" :key="i" class="recommend-item book">
              <div class="item-title">{{ b.title }}</div>
              <div class="item-sub">{{ b.author }}</div>
              <div class="item-reason">{{ b.why }}</div>
            </div>
          </div>

          <!-- Links -->
          <div v-if="links.length > 0" class="recommend-section">
            <div class="section-label">🔗 推荐网站</div>
            <div v-for="(l, i) in links" :key="i" class="recommend-item link">
              <div class="item-title">
                <a :href="l.url" target="_blank" rel="noopener">{{ l.title }}</a>
              </div>
              <div class="item-reason">{{ l.why }}</div>
            </div>
          </div>

          <!-- Recommendations -->
          <div v-if="recommendations.length > 0" class="recommend-section">
            <div class="section-label">💡 改进建议</div>
            <div v-for="(r, i) in recommendations" :key="i" class="recommend-item action">
              <div class="item-title">
                <span :class="'priority-dot ' + (r.priority || 'medium')"></span>
                {{ r.action }}
              </div>
              <div class="item-reason">{{ r.reason }}</div>
            </div>
          </div>

          <!-- Next steps -->
          <div v-if="nextSteps.length > 0" class="recommend-section">
            <div class="section-label">👉 下一步计划</div>
            <div v-for="(s, i) in nextSteps" :key="i" class="next-step-item">
              <span class="step-num">{{ i + 1 }}</span>
              <span>{{ s }}</span>
            </div>
          </div>
        </template>

        <el-empty v-else-if="!loading" description="点击「刷新评估」基于画像生成报告" :image-size="60" />

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useStudentStore } from '../stores/student'
import { evaluateLearning } from '../api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const store = useStudentStore()
const loading = ref(false)
const assessment = ref(null)

const barChartRef = ref(null)
const donutChartRef = ref(null)
let barChart = null
let donutChart = null

const LEVEL = { beginner: '入门级', intermediate: '中级', advanced: '高级' }
const STYLE = { visual: '视觉型', verbal: '文字型', logical: '逻辑型', hands_on: '动手型', social: '社交型' }

const kb = computed(() => store.profile?.knowledge_base || {})
const cs = computed(() => store.profile?.cognitive_style || {})
const lp = computed(() => store.profile?.learning_pace || {})
const mf = computed(() => store.profile?.motivation_factors || {})

const overall = computed(() => assessment.value?.overall_score ?? 0)
const dims = computed(() => {
  const raw = assessment.value?.dimensions ?? {}
  const result = {}
  for (const [k, v] of Object.entries(raw)) {
    if (typeof v === 'object' && v !== null && !Array.isArray(v) && v.score !== undefined) {
      result[k] = v
    }
  }
  return result
})
const recommendations = computed(() => assessment.value?.recommendations ?? [])
const nextSteps = computed(() => assessment.value?.next_step_suggestions ?? [])
const books = computed(() => assessment.value?.books ?? [])
const links = computed(() => assessment.value?.links ?? [])

const scoreColor = computed(() => {
  const s = overall.value
  if (s >= 80) return '#3D7A5C'
  if (s < 60) return '#722F37'
  return '#7FA08E'
})

const DIM_COLORS = ['#C8A25C', '#3D7A5C', '#7FA08E', '#722F37', '#5D7A8A', '#D4A853']

function buildBarChart() {
  if (!barChartRef.value) return
  if (!barChart) barChart = echarts.init(barChartRef.value)

  const entries = Object.entries(dims.value)
  const names = entries.map(([, v]) => v.label || '')
  const scores = entries.map(([, v]) => v.score || 0)

  if (names.length === 0) return

  barChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const p = params[0]
        const entry = entries[p.dataIndex]
        const comment = entry?.[1]?.comment || ''
        return `<b>${p.name}</b><br/>得分：${p.value}<br/>${comment}`
      },
    },
    grid: { left: '3%', right: '8%', top: 20, bottom: 30 },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: { fontSize: 11, color: '#5C5045', rotate: names.length > 4 ? 15 : 0 },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: { fontSize: 10, color: '#7A6E63', formatter: '{value}' },
      splitLine: { lineStyle: { color: '#E8DED0', type: 'dashed' } },
    },
    series: [{
      type: 'bar',
      data: scores.map((v, i) => ({
        value: v,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: DIM_COLORS[i % DIM_COLORS.length] },
            { offset: 1, color: DIM_COLORS[i % DIM_COLORS.length] + '80' },
          ]),
          borderRadius: [6, 6, 0, 0],
        },
      })),
      barWidth: Math.max(36, 60 - names.length * 4),
      label: {
        show: true,
        position: 'top',
        fontSize: 11,
        fontWeight: 600,
        color: '#5C5045',
      },
      emphasis: {
        itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.15)' },
      },
    }],
  }, true)
}

function buildDonutChart() {
  if (!donutChartRef.value) return
  if (!donutChart) donutChart = echarts.init(donutChartRef.value)

  const entries = Object.entries(dims.value)
  const data = entries.map(([, v], i) => ({
    name: v.label || '',
    value: v.score || 0,
    itemStyle: { color: DIM_COLORS[i % DIM_COLORS.length] },
  }))

  if (data.length === 0) return

  donutChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}分 ({d}%)',
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { fontSize: 11, color: '#5C5045' },
      itemWidth: 10,
      itemHeight: 10,
    },
    series: [{
      type: 'pie',
      radius: ['52%', '78%'],
      center: ['38%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 6,
        borderColor: '#fff',
        borderWidth: 3,
      },
      label: {
        show: true,
        position: 'inside',
        formatter: '{c}',
        fontSize: 12,
        fontWeight: 600,
        color: '#fff',
      },
      emphasis: {
        label: { fontSize: 18, fontWeight: 'bold' },
        scaleSize: 8,
      },
      data,
    }],
  }, true)
}

function renderCharts() {
  nextTick(() => {
    buildBarChart()
    buildDonutChart()
  })
}

watch(dims, () => {
  if (assessment.value) renderCharts()
}, { deep: true })

async function doEvaluate() {
  if (!store.currentStudentId) { ElMessage.warning('请先创建学生'); return }
  if (!store.hasProfile) { ElMessage.warning('请先完成学习画像构建'); return }

  loading.value = true
  try {
    const result = await evaluateLearning(store.currentStudentId, {})
    assessment.value = result.assessment
    renderCharts()
  } catch (e) {
    ElMessage.error('评估失败：' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

function handleResize() {
  barChart?.resize()
  donutChart?.resize()
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  if (store.hasProfile) {
    doEvaluate()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  barChart?.dispose()
  donutChart?.dispose()
})
</script>

<style scoped>
.assessment-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100px);
  padding: 0 1.2rem 0.8rem;
}

.assessment-main {
  flex: 1;
  display: flex;
  gap: 1rem;
  min-height: 0;
}

/* ===== Charts area ===== */
.charts-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}

.chart-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  padding: 1rem 1rem 0.5rem;
  display: flex;
  flex-direction: column;
}

.chart-card:first-child {
  flex: 1;
  min-height: 0;
}

.chart-card:last-child {
  flex: 0 0 42%;
}

.chart-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 0.85rem;
  color: #444;
  flex-shrink: 0;
  margin-bottom: 0.3rem;
}

.overall-badge {
  font-size: 1.2rem;
  font-weight: 800;
}

.chart-box {
  flex: 1;
  min-height: 0;
}

.chart-box.donut {
  min-height: 220px;
}

/* ===== Side area ===== */
.side-area {
  width: 400px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  overflow-y: auto;
}

.profile-summary {
  background: linear-gradient(135deg, #FBF7F0, #FBF7F0);
  border-radius: 12px;
  padding: 0.6rem 0.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  flex-shrink: 0;
}

.profile-summary.empty {
  text-align: center;
  color: #7A6E63;
  font-size: 0.82rem;
  padding: 1rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-label {
  font-size: 0.75rem;
  color: #7A6E63;
}

.summary-val {
  font-size: 0.78rem;
  font-weight: 600;
  color: #444;
}

/* Recommendations panel */
.recommend-section {
  background: #fff;
  border-radius: 12px;
  padding: 0.6rem 0.8rem;
  box-shadow: 0 1px 8px rgba(0,0,0,0.03);
}

.section-label {
  font-weight: 700;
  font-size: 0.78rem;
  color: #444;
  margin-bottom: 0.4rem;
  padding-bottom: 0.3rem;
  border-bottom: 1px solid #E8DED0;
}

.recommend-item {
  padding: 0.35rem 0.4rem;
  border-radius: 8px;
  margin-bottom: 2px;
}

.recommend-item.book {
  border-left: 3px solid #D4953A;
  background: #FFFEF9;
}

.recommend-item.link {
  border-left: 3px solid #5D7A8A;
  background: #F5EDE0;
}

.recommend-item.action {
  border-left: 3px solid #C8A25C;
  background: #FBF7F0;
}

.item-title {
  font-size: 0.78rem;
  font-weight: 600;
  color: #3C3028;
}

.item-title a {
  color: #5D7A8A;
  text-decoration: none;
}

.item-title a:hover {
  text-decoration: underline;
}

.item-sub {
  font-size: 0.7rem;
  color: #7A6E63;
  margin-top: 1px;
}

.item-reason {
  font-size: 0.72rem;
  color: #7A6E63;
  margin-top: 2px;
  line-height: 1.4;
}

.priority-dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  margin-right: 4px;
  vertical-align: middle;
}

.priority-dot.high { background: #722F37; }
.priority-dot.medium { background: #C8963E; }
.priority-dot.low { background: #3D7A5C; }

.next-step-item {
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
  padding: 0.25rem 0;
  font-size: 0.75rem;
  color: #5C5045;
  line-height: 1.5;
}

.step-num {
  flex-shrink: 0;
  width: 17px;
  height: 17px;
  border-radius: 50%;
  background: linear-gradient(135deg, #C8A25C, #B8934F);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1px;
}
</style>
