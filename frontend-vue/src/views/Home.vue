<template>
  <div class="dashboard">
    <!-- Top bar -->
    <div class="dash-topbar">
      <div class="dash-greeting">
        <div class="greeting-ornament"></div>
        <div class="greeting-text">
          <h1>学习仪表盘</h1>
          <span class="today-label">{{ todayStr }}</span>
        </div>
      </div>
      <div class="dash-quick">
        <el-button size="default" @click="$router.push('/profile')">🧠 画像</el-button>
        <el-button size="default" @click="$router.push('/resources')">📄 生成资源</el-button>
        <el-button size="default" @click="$router.push('/learning-path')">🗺️ 规划路径</el-button>
        <el-button size="default" @click="$router.push('/tutoring')">🤖 辅导</el-button>
        <el-button size="default" class="intro-btn" @click="$router.push('/welcome')">📚 系统介绍</el-button>
      </div>
    </div>

    <!-- Stats row -->
    <div class="dash-stats">
      <div class="dash-stat" @click="$router.push('/profile')">
        <div class="stat-accent a1"></div>
        <span class="dash-stat-icon">🧠</span>
        <div class="dash-stat-info">
          <span class="dash-stat-val">{{ hasProfile ? '已构建' : '待构建' }}</span>
          <span class="dash-stat-lbl">学习画像</span>
        </div>
      </div>
      <div class="dash-stat" @click="$router.push('/resources')">
        <div class="stat-accent a2"></div>
        <span class="dash-stat-icon">📄</span>
        <div class="dash-stat-info">
          <span class="dash-stat-val">{{ resourceCount }}</span>
          <span class="dash-stat-lbl">学习资源</span>
        </div>
      </div>
      <div class="dash-stat" @click="$router.push('/learning-path')">
        <div class="stat-accent a3"></div>
        <span class="dash-stat-icon">🗺️</span>
        <div class="dash-stat-info">
          <span class="dash-stat-val">{{ pathCount }}</span>
          <span class="dash-stat-lbl">学习路径</span>
        </div>
      </div>
      <div class="dash-stat" @click="$router.push('/assessment')">
        <div class="stat-accent a4"></div>
        <span class="dash-stat-icon">📊</span>
        <div class="dash-stat-info">
          <span class="dash-stat-val" :class="{ 'val-green': profileLevel === 'advanced', 'val-amber': profileLevel !== 'advanced' }">{{ levelLabel }}</span>
          <span class="dash-stat-lbl">当前水平</span>
        </div>
      </div>
    </div>

    <!-- Main: Calendar + Plans -->
    <div class="dash-main">
      <div class="calendar-card">
        <div class="cal-header">
          <el-button size="small" circle @click="prevMonth" class="cal-nav-btn">◀</el-button>
          <span class="cal-month">{{ calYear }}年 {{ calMonth }}月</span>
          <el-button size="small" circle @click="nextMonth" class="cal-nav-btn">▶</el-button>
        </div>
        <div class="cal-weekdays">
          <span v-for="d in weekdays" :key="d" class="cal-wd">{{ d }}</span>
        </div>
        <div class="cal-grid">
          <div
            v-for="(day, i) in calDays"
            :key="i"
            :class="[
              'cal-cell',
              { 'cal-empty': !day, 'cal-today': day && isToday(day), 'cal-sel': day && isSelected(day), 'cal-has-plan': day && hasPlan(day) }
            ]"
            @click="day && selectDate(day)"
          >
            <span v-if="day" class="cal-day-num">{{ day }}</span>
            <span v-if="day && hasPlan(day)" class="cal-dot"></span>
          </div>
        </div>
      </div>

      <div class="plans-panel">
        <template v-if="selectedDate">
          <div class="plans-header">
            <div class="plans-header-left">
              <span class="plans-date-icon">📋</span>
              <span class="plans-date-text">{{ selectedDate }}</span>
              <span class="plans-date-weekday">（{{ weekdayLabel }}）</span>
            </div>
            <span class="plan-count">{{ dayPlans.length }} 项计划</span>
          </div>
          <div class="plan-list">
            <div v-for="(p, idx) in dayPlans" :key="p.id" :class="['plan-item', { done: p.completed }]">
              <div class="plan-accent" :style="{ background: accentColors[idx % 5] }"></div>
              <div class="plan-left" @click="togglePlan(p)">
                <span :class="['plan-check-dot', { checked: p.completed }]">{{ p.completed ? '✅' : '⭕' }}</span>
                <div class="plan-item-text">
                  <span :class="['plan-item-title', { 'plan-title-done': p.completed }]">{{ p.title }}</span>
                  <span v-if="p.description" class="plan-item-desc">{{ p.description }}</span>
                </div>
              </div>
              <div class="plan-right" @click="handlePlanDelete(p)">
                <span class="plan-del-icon">🗑️</span>
              </div>
            </div>
            <div v-if="dayPlans.length === 0" class="plan-empty">
              <span class="plan-empty-icon">✨</span>
              <span class="plan-empty-text">这天还没有计划</span>
              <span class="plan-empty-hint">输入标题后按回车添加</span>
            </div>
          </div>
          <div class="plan-add-row">
            <el-input v-model="newPlanTitle" placeholder="计划标题..." size="default" @keyup.enter="addNewPlan" class="plan-add-title" />
            <el-input v-model="newPlanDesc" placeholder="描述（可选）" size="default" @keyup.enter="addNewPlan" class="plan-add-desc" />
            <el-button size="default" @click="addNewPlan" :disabled="!newPlanTitle.trim()" class="plan-add-btn">+ 添加</el-button>
          </div>
        </template>
        <div v-else class="plans-panel-empty">
          <div class="empty-cal-icon-wrap">
            <span class="empty-cal-icon">📅</span>
          </div>
          <span class="empty-cal-text">点击日历中的日期</span>
          <span class="empty-cal-sub">查看或添加学习计划</span>
        </div>
      </div>
    </div>

    <!-- Today's Tasks -->
    <div class="today-section">
      <div class="today-section-header">
        <div class="today-title-row">
          <span class="today-icon">📌</span>
          <span class="today-title">今日任务</span>
          <span class="today-date-badge">{{ todayStr }}</span>
        </div>
        <span v-if="todayPlans.length > 0" class="today-progress-badge">
          {{ todayPlans.filter(p => p.completed).length }}/{{ todayPlans.length }} 完成
        </span>
      </div>

      <div v-if="todayPlans.length > 0" class="today-task-list">
        <div v-for="(p, idx) in todayPlans" :key="p.id" :class="['today-task-card', { 'task-done': p.completed }]">
          <div class="task-accent" :style="{ background: accentColors[idx % 5] }"></div>
          <div class="task-left" @click="togglePlan(p)">
            <span :class="['task-check-dot', { checked: p.completed }]">{{ p.completed ? '✅' : '⭕' }}</span>
            <div class="task-body">
              <span :class="['task-title', { 'task-title-done': p.completed }]">{{ p.title }}</span>
              <span v-if="p.description" class="task-desc">{{ p.description }}</span>
            </div>
          </div>
          <div class="task-right" @click="handlePlanDelete(p)">
            <span class="task-del-icon">🗑️</span>
          </div>
        </div>
      </div>

      <div v-else class="today-empty">
        <span class="today-empty-icon">🌤️</span>
        <span class="today-empty-text">今天还没有安排任务</span>
        <span class="today-empty-hint">点击日历添加今日计划吧</span>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStudentStore } from '../stores/student'
import { getPlans, addPlan, updatePlan, deletePlan, getResources, getPaths } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const store = useStudentStore()

const LEVEL = { beginner: '入门', intermediate: '中级', advanced: '高级' }
const weekdays = ['一', '二', '三', '四', '五', '六', '日']
const accentColors = ['#C8A25C', '#722F37', '#3D7A5C', '#7FA08E', '#5D7A8A']
const calYear = ref(new Date().getFullYear())
const calMonth = ref(new Date().getMonth() + 1)
const selectedDate = ref('')
const plansMap = ref({})
const datesWithPlans = ref([])
const todayPlans = ref([])
const resourceCount = ref(0)
const pathCount = ref(0)

const newPlanTitle = ref('')
const newPlanDesc = ref('')

const todayStr = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
})

const hasProfile = computed(() => store.hasProfile)
const profileLevel = computed(() => store.profile?.knowledge_base?.level || 'beginner')
const levelLabel = computed(() => LEVEL[profileLevel.value] || '未知')

const dayPlans = computed(() => {
  if (!selectedDate.value) return []
  return plansMap.value[selectedDate.value] || []
})

const weekdayLabel = computed(() => {
  if (!selectedDate.value) return ''
  const parts = selectedDate.value.split('-')
  const d = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]))
  return weekdays[d.getDay() === 0 ? 6 : d.getDay() - 1]
})

function getDateKey(year, month, day) {
  return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
}

const calDays = computed(() => {
  const year = calYear.value
  const month = calMonth.value
  const firstDay = new Date(year, month - 1, 1)
  const lastDay = new Date(year, month, 0)
  const daysInMonth = lastDay.getDate()
  let startDow = firstDay.getDay() - 1
  if (startDow < 0) startDow = 6
  const cells = []
  for (let i = 0; i < startDow; i++) cells.push(null)
  for (let d = 1; d <= daysInMonth; d++) cells.push(d)
  return cells
})

function isToday(day) {
  const now = new Date()
  return calYear.value === now.getFullYear() && calMonth.value === now.getMonth() + 1 && day === now.getDate()
}

function isSelected(day) {
  return selectedDate.value === getDateKey(calYear.value, calMonth.value, day)
}

function hasPlan(day) {
  return datesWithPlans.value.includes(getDateKey(calYear.value, calMonth.value, day))
}

function selectDate(day) {
  selectedDate.value = getDateKey(calYear.value, calMonth.value, day)
  newPlanTitle.value = ''
  newPlanDesc.value = ''
}

function prevMonth() { if (calMonth.value === 1) { calYear.value--; calMonth.value = 12 } else calMonth.value--; selectedDate.value = ''; loadPlans() }
function nextMonth() { if (calMonth.value === 12) { calYear.value++; calMonth.value = 1 } else calMonth.value++; selectedDate.value = ''; loadPlans() }

async function loadPlans() {
  if (!store.currentStudentId) return
  try {
    const data = await getPlans(store.currentStudentId, calYear.value, calMonth.value)
    datesWithPlans.value = data.dates_with_plans || []
    const map = {}
    const today = getDateKey(new Date().getFullYear(), new Date().getMonth() + 1, new Date().getDate())
    const todayList = []
    for (const p of data.plans || []) {
      if (!map[p.plan_date]) map[p.plan_date] = []
      map[p.plan_date].push(p)
      if (p.plan_date === today) todayList.push(p)
    }
    plansMap.value = map
    todayPlans.value = todayList
  } catch { /* ignore */ }
}

async function loadStats() {
  if (!store.currentStudentId) return
  try {
    const [resData, pathData] = await Promise.all([
      getResources(store.currentStudentId),
      getPaths(store.currentStudentId),
    ])
    resourceCount.value = (resData.resources || []).length
    pathCount.value = (pathData.paths || []).length
  } catch { /* ignore */ }
}

async function addNewPlan() {
  const title = newPlanTitle.value.trim()
  if (!title || !selectedDate.value || !store.currentStudentId) return
  try {
    const result = await addPlan({ student_id: store.currentStudentId, plan_date: selectedDate.value, title, description: newPlanDesc.value.trim() })
    const d = selectedDate.value
    if (!plansMap.value[d]) plansMap.value[d] = []
    plansMap.value[d].push(result)
    if (!datesWithPlans.value.includes(d)) datesWithPlans.value.push(d)
    newPlanTitle.value = ''
    newPlanDesc.value = ''
    const today = getDateKey(new Date().getFullYear(), new Date().getMonth() + 1, new Date().getDate())
    if (d === today) todayPlans.value.push(result)
    ElMessage.success('计划已添加')
  } catch (e) { ElMessage.error('添加失败') }
}

async function togglePlan(p) {
  try {
    await updatePlan(p.id, { student_id: store.currentStudentId, completed: !p.completed })
    p.completed = !p.completed
  } catch { /* ignore */ }
}

async function handlePlanDelete(p) {
  try {
    await ElMessageBox.confirm(
      `<div class="export-msg">
        <span class="export-msg-icon">🗑️</span>
        <div class="export-msg-body">
          <div class="export-msg-title">${p.title}</div>
          <div class="export-msg-meta">确认删除该学习计划？<b>此操作不可恢复</b>。</div>
        </div>
      </div>`,
      '删除计划',
      { confirmButtonText: '🗑️ 删除', cancelButtonText: '取消', dangerouslyUseHTMLString: true, customClass: 'export-confirm-dialog' }
    )
    await deletePlan(p.id, store.currentStudentId)
    const d = p.plan_date
    plansMap.value[d] = plansMap.value[d].filter(x => x.id !== p.id)
    if (plansMap.value[d].length === 0) datesWithPlans.value = datesWithPlans.value.filter(x => x !== d)
    todayPlans.value = todayPlans.value.filter(x => x.id !== p.id)
    ElMessage.success('已删除')
  } catch { /* cancelled */ }
}

onMounted(async () => {
  if (store.currentStudentId) {
    await store.loadProfile()
    await Promise.all([loadPlans(), loadStats()])
  }
})

</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  padding: 0.6rem 1.5rem 1rem;
  gap: 1rem;
  min-height: 100%;
}

/* ===== Top bar ===== */
.dash-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.2rem 0 0;
}

.dash-greeting {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}

.greeting-ornament {
  width: 5px;
  height: 44px;
  border-radius: 2px;
  background: linear-gradient(180deg, #C8A25C, #8B6F3D);
  flex-shrink: 0;
}

.greeting-text {
  display: flex;
  flex-direction: column;
}

.greeting-text h1 {
  font-size: 1.6rem;
  font-weight: 700;
  color: #3C3028;
  margin: 0;
  letter-spacing: 0.03em;
}

.today-label {
  font-size: 0.85rem;
  color: #A89880;
}

.dash-quick {
  display: flex;
  gap: 0.45rem;
}

.dash-quick :deep(.el-button) {
  border-radius: 6px;
  font-size: 0.88rem;
  font-weight: 500;
  height: 38px;
  border: 1px solid #D4C4A8;
  color: #5C4F42;
  background: #FFFEF9;
  transition: all 0.2s;
}

.dash-quick :deep(.el-button:hover) {
  border-color: #C8A25C;
  color: #8B6F3D;
  background: rgba(200, 162, 92, 0.06);
}

.dash-quick :deep(.el-button.intro-btn) {
  background: linear-gradient(135deg, #C8A25C, #B8934F) !important;
  border-color: transparent !important;
  color: #fff !important;
}

.dash-quick :deep(.el-button.intro-btn:hover) {
  background: linear-gradient(135deg, #B8934F, #A07D3E) !important;
}

/* ===== Stats row ===== */
.dash-stats {
  display: flex;
  gap: 1rem;
}

.dash-stat {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  background: #FFFEF9;
  border-radius: 10px;
  padding: 0.95rem 1.1rem;
  box-shadow: 0 1px 3px rgba(60, 48, 40, 0.04);
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  border: 1px solid #E8E0D5;
  position: relative;
  overflow: hidden;
}

.dash-stat:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(60, 48, 40, 0.1);
}

.stat-accent {
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  border-radius: 4px 0 0 4px;
}

.stat-accent.a1 { background: #C8A25C; }
.stat-accent.a2 { background: #3D7A5C; }
.stat-accent.a3 { background: #5D7A8A; }
.stat-accent.a4 { background: #722F37; }

.dash-stat-icon {
  font-size: 1.6rem;
  flex-shrink: 0;
  margin-left: 0.2rem;
}

.dash-stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dash-stat-val {
  font-size: 1.15rem;
  font-weight: 700;
  color: #3C3028;
}

.dash-stat-val.val-green { color: #3D7A5C; }
.dash-stat-val.val-amber { color: #C8963E; }

.dash-stat-lbl {
  font-size: 0.82rem;
  color: #7A6E63;
}

/* ===== Main: calendar + plans ===== */
.dash-main {
  display: flex;
  gap: 1.5rem;
}

/* Calendar */
.calendar-card {
  background: #FFFEF9;
  border-radius: 10px;
  padding: 1rem 1.1rem;
  box-shadow: 0 1px 4px rgba(60, 48, 40, 0.05);
  width: 360px;
  flex-shrink: 0;
  align-self: flex-start;
  border: 1px solid #E8E0D5;
}

.cal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.7rem;
}

.cal-nav-btn {
  width: 30px !important;
  height: 30px !important;
  min-width: 30px !important;
  border: 1px solid #D4C4A8 !important;
  color: #7A6E63 !important;
  background: #FBF7F0 !important;
  font-size: 0.72rem !important;
}

.cal-nav-btn:hover {
  border-color: #C8A25C !important;
  color: #C8A25C !important;
  background: #FFFEF9 !important;
}

.cal-month {
  font-size: 0.98rem;
  font-weight: 700;
  color: #3C3028;
  letter-spacing: 0.03em;
}

.cal-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  margin-bottom: 0.25rem;
}

.cal-wd {
  font-size: 0.72rem;
  font-weight: 600;
  color: #B8A088;
  padding: 0.25rem 0;
}

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.cal-cell {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  transition: background 0.15s;
  font-size: 0.85rem;
  color: #5C4F42;
}

.cal-cell:hover {
  background: #F5EDE0;
}

.cal-empty {
  cursor: default;
}

.cal-empty:hover {
  background: transparent;
}

.cal-today .cal-day-num {
  color: #C8A25C;
  font-weight: 800;
}

.cal-sel {
  background: linear-gradient(135deg, #C8A25C, #B8934F);
  color: #fff;
}

.cal-sel .cal-day-num {
  color: #fff;
  font-weight: 700;
}

.cal-sel:hover {
  background: linear-gradient(135deg, #C8A25C, #B8934F);
}

.cal-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #C8A25C;
  position: absolute;
  bottom: 3px;
}

.cal-sel .cal-dot {
  background: #fff;
}

/* Plans panel */
.plans-panel {
  flex: 1;
  background: #FFFEF9;
  border-radius: 10px;
  padding: 1rem 1.3rem;
  box-shadow: 0 1px 4px rgba(60, 48, 40, 0.05);
  display: flex;
  flex-direction: column;
  border: 1px solid #E8E0D5;
}

.plans-panel-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.empty-cal-icon-wrap {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FBF7F0, #F5EDE0);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.3rem;
  border: 1px solid #E8E0D5;
}

.empty-cal-icon {
  font-size: 2.4rem;
}

.empty-cal-text {
  font-size: 1rem;
  color: #7A6E63;
  font-weight: 500;
}

.empty-cal-sub {
  font-size: 0.85rem;
  color: #B8A088;
}

/* Plans header */
.plans-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.6rem;
  padding-bottom: 0.6rem;
  border-bottom: 1.5px solid #F5EDE0;
}

.plans-header-left {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
}

.plans-date-icon {
  font-size: 1.3rem;
}

.plans-date-text {
  font-size: 1.15rem;
  font-weight: 700;
  color: #3C3028;
}

.plans-date-weekday {
  font-size: 0.85rem;
  color: #A89880;
  font-weight: 400;
}

.plan-count {
  font-size: 0.82rem;
  color: #8B6F3D;
  background: rgba(200, 162, 92, 0.1);
  padding: 0.25rem 0.8rem;
  border-radius: 10px;
  font-weight: 500;
}

/* Plan list */
.plan-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.plan-item {
  display: flex;
  align-items: center;
  padding: 0.55rem 0.65rem 0.55rem 0;
  border-radius: 6px;
  background: #FBF7F0;
  gap: 0.5rem;
  transition: all 0.15s;
  overflow: hidden;
  border: 1px solid transparent;
}

.plan-item:hover {
  background: #F5EDE0;
  border-color: #E8E0D5;
  transform: translateX(2px);
}

.plan-item.done {
  opacity: 0.5;
  background: #f2f8f4;
}

.plan-accent {
  width: 3px;
  height: 32px;
  border-radius: 0 3px 3px 0;
  flex-shrink: 0;
}

.plan-left {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  flex: 1;
  min-width: 0;
  cursor: pointer;
  user-select: none;
}

.plan-check-dot {
  font-size: 1rem;
  flex-shrink: 0;
  opacity: 0.5;
  transition: opacity 0.15s;
}

.plan-check-dot.checked {
  opacity: 1;
}

.plan-item-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.plan-item-title {
  font-size: 0.92rem;
  font-weight: 600;
  color: #3C3028;
}

.plan-title-done {
  text-decoration: line-through;
  color: #A89880;
}

.plan-item-desc {
  font-size: 0.78rem;
  color: #A89880;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.plan-right {
  flex-shrink: 0;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.15s;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.plan-right:hover {
  background: rgba(114, 47, 55, 0.08);
}

.plan-item:hover .plan-right {
  opacity: 1;
}

.plan-del-icon {
  font-size: 0.95rem;
}

/* Plan empty */
.plan-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  padding: 3rem 0;
}

.plan-empty-icon {
  font-size: 2.5rem;
}

.plan-empty-text {
  font-size: 0.92rem;
  color: #B8A088;
}

.plan-empty-hint {
  font-size: 0.8rem;
  color: #D4C4A8;
}

/* Plan add row */
.plan-add-row {
  display: flex;
  gap: 0.5rem;
  padding-top: 0.6rem;
  border-top: 1.5px solid #F5EDE0;
  margin-top: 0.5rem;
}

.plan-add-title {
  flex: 2;
}

.plan-add-desc {
  flex: 3;
}

.plan-add-btn {
  flex-shrink: 0;
  min-width: 90px;
  background: linear-gradient(135deg, #C8A25C, #B8934F);
  border: none;
  color: #fff;
  font-weight: 500;
  border-radius: 6px;
  font-size: 0.88rem;
  transition: all 0.2s;
}

.plan-add-btn:hover {
  background: linear-gradient(135deg, #B8934F, #A07D3E);
  transform: translateY(-1px);
}

.plan-add-btn:disabled {
  background: #D4C4A8;
  color: #A89880;
}

/* ===== Today's Tasks ===== */
.today-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #FFFEF9;
  border-radius: 10px;
  padding: 1.1rem 1.4rem;
  box-shadow: 0 1px 4px rgba(60, 48, 40, 0.05);
  min-height: 160px;
  border: 1px solid #E8E0D5;
}

.today-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.6rem;
  padding-bottom: 0.6rem;
  border-bottom: 1.5px solid #F5EDE0;
}

.today-title-row {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.today-icon {
  font-size: 1.4rem;
}

.today-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #3C3028;
}

.today-date-badge {
  font-size: 0.82rem;
  color: #7A6E63;
  background: #F5EDE0;
  padding: 0.2rem 0.7rem;
  border-radius: 4px;
}

.today-progress-badge {
  font-size: 0.85rem;
  font-weight: 600;
  color: #8B6F3D;
  background: rgba(200, 162, 92, 0.12);
  padding: 0.35rem 0.9rem;
  border-radius: 10px;
  border: 1px solid rgba(200, 162, 92, 0.2);
}

.today-task-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.today-task-card {
  display: flex;
  align-items: center;
  padding: 0.7rem 0.8rem 0.7rem 0;
  border-radius: 6px;
  background: #FBF7F0;
  gap: 0.55rem;
  transition: all 0.15s;
  overflow: hidden;
  border: 1px solid #EDE5D5;
}

.today-task-card:hover {
  border-color: #D4C4A8;
  box-shadow: 0 2px 8px rgba(200, 162, 92, 0.06);
  transform: translateY(-1px);
}

.today-task-card.task-done {
  opacity: 0.5;
  background: #f3f8f5;
  border-color: #d8e8dc;
}

.task-accent {
  width: 4px;
  height: 30px;
  border-radius: 0 3px 3px 0;
  flex-shrink: 0;
}

.task-left {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  flex: 1;
  min-width: 0;
  cursor: pointer;
  user-select: none;
}

.task-check-dot {
  font-size: 1rem;
  flex-shrink: 0;
  opacity: 0.5;
  transition: opacity 0.15s;
}

.task-check-dot.checked {
  opacity: 1;
}

.task-body {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
  gap: 0.12rem;
}

.task-title {
  font-size: 0.92rem;
  font-weight: 600;
  color: #3C3028;
}

.task-title-done {
  text-decoration: line-through;
  color: #A89880;
}

.task-desc {
  font-size: 0.78rem;
  color: #A89880;
}

.task-right {
  flex-shrink: 0;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.15s;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.task-right:hover {
  background: rgba(114, 47, 55, 0.08);
}

.today-task-card:hover .task-right {
  opacity: 1;
}

.task-del-icon {
  font-size: 1rem;
}

/* Today empty */
.today-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
}

.today-empty-icon {
  font-size: 3rem;
}

.today-empty-text {
  font-size: 1rem;
  color: #B8A088;
  font-weight: 500;
}

.today-empty-hint {
  font-size: 0.85rem;
  color: #D4C4A8;
}
</style>
