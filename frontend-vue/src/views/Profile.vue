<template>
  <div class="profile-page">
    <!-- Compact header -->
    <div class="profile-topbar">
      <div class="topbar-left">
        <h1>🧠 学习画像</h1>
        <span v-if="store.profileVersion" class="version-badge">v{{ store.profileVersion }}</span>
      </div>
      <div class="topbar-right">
        <span class="pulse-dot"></span>
        <span class="auto-hint">随学习活动自动更新</span>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!hasProfile" class="no-profile-card">
      <div class="no-profile-icon">🧠</div>
      <h2>尚未构建学习画像</h2>
      <p>完成引导问卷或开始学习后，系统将自动为你构建专属学习画像</p>
      <el-button type="primary" size="large" @click="$router.push('/onboarding')">
        前往构建画像 →
      </el-button>
    </div>

    <!-- Main content: mind map (2/3) + detail panel (1/3) -->
    <div v-else class="profile-main">
      <div class="mindmap-panel" ref="mindmapRef">
        <svg class="mindmap-svg" viewBox="0 0 1000 700" preserveAspectRatio="xMidYMid meet">
          <defs>
            <linearGradient v-for="(dim, i) in dimensionsWithPos" :key="'grad'+i" :id="'lineGrad'+i" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" :stop-color="dim.color" stop-opacity="0.7" />
              <stop offset="100%" stop-color="#C8A25C" stop-opacity="0.7" />
            </linearGradient>
          </defs>
          <!-- Glow layer -->
          <g v-for="(dim, i) in dimensionsWithPos" :key="'glow'+i">
            <path
              :d="dim.pathD"
              :stroke="dim.color"
              stroke-width="6"
              fill="none"
              stroke-linecap="round"
              opacity="0.12"
            />
          </g>
          <!-- Connection lines -->
          <g v-for="(dim, i) in dimensionsWithPos" :key="'line'+i">
            <path
              :d="dim.pathD"
              :stroke="'url(#lineGrad'+i+')'"
              stroke-width="3"
              fill="none"
              stroke-linecap="round"
            />
          </g>
        </svg>

        <!-- Center node -->
        <div class="center-node" :style="centerStyle" @click="selectDim(null)">
          <div class="center-ring"></div>
          <div class="center-inner">
            <span class="center-emoji">🧠</span>
            <span class="center-label">学习画像</span>
          </div>
        </div>

        <!-- 6 dimension nodes -->
        <div
          v-for="(dim, i) in dimensionsWithPos"
          :key="i"
          :class="['dim-node', { 'dim-selected': selectedIndex === i }]"
          :style="{ left: dim.left, top: dim.top }"
          @click="selectDim(i)"
        >
          <div class="dim-node-card">
            <span class="dim-icon">{{ dim.icon }}</span>
            <span class="dim-title">{{ dim.label }}</span>
            <span class="dim-val">{{ dim.value }}</span>
            <div class="dim-sub">
              <span v-if="dim.sub1">{{ dim.sub1 }}</span>
              <span v-if="dim.sub2">{{ dim.sub2 }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right detail panel -->
      <div class="detail-panel">
        <template v-if="selectedDim">
          <div class="detail-header" :style="{ borderColor: selectedDim.color }">
            <span class="detail-header-icon">{{ selectedDim.icon }}</span>
            <div class="detail-header-text">
              <span class="detail-header-label">{{ selectedDim.label }}</span>
              <span class="detail-header-val">{{ selectedDim.value }}</span>
            </div>
          </div>
          <div class="detail-body">
            <div v-for="(item, j) in selectedDim.details" :key="j" class="detail-card">
              <span class="detail-card-key">{{ item.key }}</span>
              <span class="detail-card-val">{{ item.val }}</span>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="detail-header">
            <span class="detail-header-icon">📋</span>
            <div class="detail-header-text">
              <span class="detail-header-label">画像总览</span>
              <span class="detail-header-sub">6 维度学习特征</span>
            </div>
          </div>
          <div class="detail-body">
            <div
              v-for="(dim, i) in dimensions"
              :key="i"
              class="overview-card"
              :style="{ borderLeftColor: dim.color }"
              @click="selectDim(i)"
            >
              <div class="ov-card-top">
                <span class="ov-card-icon">{{ dim.icon }}</span>
                <div class="ov-card-info">
                  <span class="ov-card-label">{{ dim.label }}</span>
                  <span class="ov-card-val">{{ dim.value }}</span>
                </div>
                <span class="ov-card-arrow">→</span>
              </div>
              <div v-if="dim.sub1 || dim.sub2" class="ov-card-extra">
                <span v-if="dim.sub1">{{ dim.sub1 }}</span>
                <span v-if="dim.sub2">· {{ dim.sub2 }}</span>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStudentStore } from '../stores/student'

const store = useStudentStore()
const selectedIndex = ref(null)
const mindmapRef = ref(null)

const LEVEL = { beginner: '入门级', intermediate: '中级', advanced: '高级' }
const STYLE = { visual: '视觉型', verbal: '文字型', logical: '逻辑型', hands_on: '动手型', social: '社交型' }
const PACE = { slow_and_deep: '慢而深', moderate: '中等', fast: '快速' }
const MODALITY = { text: '文字', video: '视频', audio: '音频', interactive: '交互', diagram: '图示', code_practice: '代码实操', animation: '动画' }
const ERROR_TYPE = { '概念混淆': '概念混淆', '计算错误': '计算错误', '逻辑错误': '逻辑错误', '记忆遗忘': '记忆遗忘' }
const FREQ = { high: '高频', medium: '中频', low: '低频' }

const hasProfile = computed(() => store.hasProfile)
const profile = computed(() => store.profile)

const pm = computed(() => {
  const raw = profile.value?.preferred_modalities || {}
  if (Array.isArray(raw)) return raw
  return raw.modalities || []
})
const ep = computed(() => {
  const raw = profile.value?.error_patterns || {}
  if (Array.isArray(raw)) return raw
  return raw.patterns || []
})

const dimensions = computed(() => {
  if (!profile.value) return []
  const p = profile.value
  const kbData = p.knowledge_base || {}
  const csData = p.cognitive_style || {}
  const lpData = p.learning_pace || {}
  const mfData = p.motivation_factors || {}
  const mods = pm.value
  const epData = ep.value

  return [
    {
      icon: '🧠', label: '知识基础', color: '#C8A25C',
      value: LEVEL[kbData.level] || kbData.level || '—',
      sub1: (kbData.mastered_topics || []).slice(0, 2).join('、') || null,
      sub2: (kbData.weak_points || []).slice(0, 2).join('、') || null,
      details: [
        { key: '当前水平', val: LEVEL[kbData.level] || kbData.level || '—' },
        { key: '已掌握', val: (kbData.mastered_topics || []).join('、') || '暂无' },
        { key: '薄弱点', val: (kbData.weak_points || []).join('、') || '暂无' },
        { key: '学习目标', val: (kbData.target_topics || []).join('、') || '暂无' },
      ],
    },
    {
      icon: '🎨', label: '认知风格', color: '#D4953A',
      value: STYLE[csData.primary_style] || csData.primary_style || '—',
      sub1: csData.description || null,
      sub2: (csData.secondary_styles || []).map(s => STYLE[s] || s).join('、') || null,
      details: [
        { key: '主要风格', val: STYLE[csData.primary_style] || csData.primary_style || '—' },
        { key: '描述', val: csData.description || '暂无' },
        { key: '次要风格', val: (csData.secondary_styles || []).map(s => STYLE[s] || s).join('、') || '暂无' },
      ],
    },
    {
      icon: '⏱️', label: '学习节奏', color: '#3D7A5C',
      value: PACE[lpData.speed] || lpData.speed || '—',
      sub1: lpData.attention_span ? `专注: ${({ short: '较短', medium: '中等', long: '较长' })[lpData.attention_span] || lpData.attention_span}` : null,
      sub2: lpData.weekly_hours ? `每周 ${lpData.weekly_hours}h` : null,
      details: [
        { key: '学习速度', val: PACE[lpData.speed] || lpData.speed || '—' },
        { key: '专注时长', val: { short: '较短', medium: '中等', long: '较长' }[lpData.attention_span] || lpData.attention_span || '—' },
        { key: '每周学时', val: lpData.weekly_hours ? `${lpData.weekly_hours} 小时` : '—' },
      ],
    },
    {
      icon: '📱', label: '偏好模态', color: '#5D7A8A',
      value: mods.length ? `${mods.length} 种` : '—',
      sub1: mods.slice(0, 3).map(m => MODALITY[m] || m).join('、') || null,
      sub2: null,
      details: [
        { key: '偏好类型', val: mods.map(m => MODALITY[m] || m).join('、') || '暂无' },
      ],
    },
    {
      icon: '⚠️', label: '易错模式', color: '#722F37',
      value: epData.length ? `${epData.length} 个` : '暂无',
      sub1: epData.length > 0 ? epData[0].topic || '' : null,
      sub2: epData.length > 1 ? epData[1].topic || '' : null,
      details: epData.length > 0
        ? epData.map(e => ({
            key: e.topic || '未知',
            val: `${ERROR_TYPE[e.error_type] || e.error_type || '—'} · ${FREQ[e.frequency] || e.frequency || '—'}`,
          }))
        : [{ key: '暂无易错记录', val: '继续学习以发现薄弱点' }],
    },
    {
      icon: '🎯', label: '学习动机', color: '#7B5F8A',
      value: mfData.primary_goal || '—',
      sub1: mfData.intrinsic_motivation || null,
      sub2: mfData.extrinsic_motivation || null,
      details: [
        { key: '主要目标', val: mfData.primary_goal || '—' },
        { key: '内在动机', val: mfData.intrinsic_motivation || '暂无' },
        { key: '外在动机', val: mfData.extrinsic_motivation || '暂无' },
      ],
    },
  ]
})

const selectedDim = computed(() => {
  if (selectedIndex.value === null || selectedIndex.value === undefined) return null
  return dimensions.value[selectedIndex.value] || null
})

function selectDim(i) {
  selectedIndex.value = i
}

// SVG viewBox: 1000 x 700, center at (500, 350)
// 6 nodes in oval/ellipse layout to fill space better
const dimensionsWithPos = computed(() => {
  const cx = 500, cy = 360
  const rx = 310, ry = 220
  const dimR = 82   // approximate radius of dimension node card
  const centerR = 58 // radius of center node

  return dimensions.value.map((dim, i) => {
    const angleDeg = -90 + i * 60
    const angleRad = (angleDeg * Math.PI) / 180
    const cosA = Math.cos(angleRad)
    const sinA = Math.sin(angleRad)
    const tx = cx + rx * cosA
    const ty = cy + ry * sinA

    // Offset start from dim node edge, end at center node edge
    const sx = tx - dimR * cosA
    const sy = ty - dimR * sinA
    const ex = cx + centerR * cosA
    const ey = cy + centerR * sinA

    // Curved bezier: start at dim edge, end at center edge
    const mx = (sx + ex) / 2 + (i - 2.5) * 30
    const my = (sy + ey) / 2 + (i - 2.5) * 15
    const pathD = `M${sx},${sy} Q${mx},${my} ${ex},${ey}`

    return {
      ...dim,
      left: `${(tx / 1000) * 100}%`,
      top: `${(ty / 700) * 100}%`,
      pathD,
    }
  })
})

const centerStyle = computed(() => ({
  left: `${50}%`,
  top: `${(360 / 700) * 100}%`,
}))

onMounted(() => {
  if (store.currentStudentId) {
    store.loadProfile()
  }
})
</script>

<style scoped>
/* ===== Page layout ===== */
.profile-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100px);
  padding: 0.6rem 1.2rem 0.8rem;
  gap: 0;
}

.profile-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.3rem 0 0.4rem;
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.topbar-left h1 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #3C3028;
  margin: 0;
}

.version-badge {
  background: linear-gradient(135deg, #C8A25C, #B8934F);
  color: #fff;
  font-size: 0.72rem;
  padding: 2px 10px;
  border-radius: 10px;
  font-weight: 600;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  color: #7A6E63;
}

.pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #3D7A5C;
  animation: dotPulse 2s ease-in-out infinite;
}

@keyframes dotPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* ===== Empty state ===== */
.no-profile-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #FFFEF9;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(60, 48, 40, 0.08);
  border: 1px solid #E8E0D5;
}

.no-profile-icon { font-size: 4rem; margin-bottom: 0.5rem; }
.no-profile-card h2 { font-size: 1.3rem; color: #3C3028; margin: 0 0 0.5rem; }
.no-profile-card p { color: #7A6E63; margin: 0 0 1.5rem; font-size: 0.9rem; }

/* ===== Main area: mind map + detail panel ===== */
.profile-main {
  flex: 1;
  display: flex;
  gap: 0.8rem;
  min-height: 0;
}

/* ===== Mind map panel (2/3) ===== */
.mindmap-panel {
  flex: 5;
  position: relative;
  background: #FFFEF9;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(60, 48, 40, 0.08);
  overflow: hidden;
  min-width: 0;
  border: 1px solid #E8E0D5;
}

.mindmap-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

/* Center node */
.center-node {
  position: absolute;
  transform: translate(-50%, -50%);
  width: 120px;
  height: 120px;
  cursor: pointer;
  z-index: 10;
  transition: transform 0.3s ease;
}

.center-node:hover {
  transform: translate(-50%, -50%) scale(1.06);
}

.center-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: linear-gradient(135deg, #C8A25C, #B8934F);
  animation: centerPulse 3s ease-in-out infinite;
}

@keyframes centerPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(200, 162, 92, 0.4); }
  50% { box-shadow: 0 0 0 22px rgba(200, 162, 92, 0); }
}

.center-inner {
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  background: #FFFEF9;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.center-emoji { font-size: 2rem; }
.center-label { font-size: 0.78rem; font-weight: 700; color: #5C4F42; }

/* Dimension nodes */
.dim-node {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 5;
  transition: transform 0.3s ease, filter 0.3s ease;
}

.dim-node:hover {
  transform: translate(-50%, -50%) scale(1.06);
  filter: brightness(1.02);
}

.dim-node.dim-selected .dim-node-card {
  border-color: #C8A25C;
  box-shadow: 0 6px 28px rgba(200, 162, 92, 0.22);
  background: #fdf8f0;
}

.dim-node-card {
  background: #FFFEF9;
  border: 2px solid #E8E0D5;
  border-radius: 12px;
  padding: 0.8rem 1.1rem;
  min-width: 155px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  box-shadow: 0 2px 16px rgba(60, 48, 40, 0.06);
  transition: border-color 0.3s, box-shadow 0.3s, background 0.3s;
}

.dim-icon { font-size: 1.5rem; line-height: 1; }

.dim-title {
  font-weight: 700;
  font-size: 0.85rem;
  color: #3C3028;
}

.dim-val {
  font-size: 0.8rem;
  color: #8B6F3D;
  font-weight: 600;
  text-align: center;
}

.dim-sub {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  margin-top: 2px;
}

.dim-sub span {
  font-size: 0.66rem;
  color: #7A6E63;
  text-align: center;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ===== Detail panel ===== */
.detail-panel {
  flex: 4;
  background: #FFFEF9;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(60, 48, 40, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 280px;
  border: 1px solid #E8E0D5;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.9rem 1.2rem 0.7rem;
  border-bottom: 1.5px solid #E8E0D5;
  border-left: 4px solid transparent;
  transition: border-color 0.3s;
}

.detail-header-icon {
  font-size: 2rem;
  line-height: 1;
}

.detail-header-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-header-label {
  font-size: 1.1rem;
  font-weight: 700;
  color: #3C3028;
}

.detail-header-val {
  font-size: 0.85rem;
  color: #C8A25C;
  font-weight: 600;
}

.detail-header-sub {
  font-size: 0.78rem;
  color: #7A6E63;
}

.detail-body {
  flex: 1;
  overflow-y: auto;
  padding: 0.7rem 1.2rem;
}

/* Detail cards */
.detail-card {
  background: #FBF7F0;
  border-radius: 8px;
  padding: 0.9rem 1.1rem;
  margin-bottom: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 3px;
  transition: background 0.2s;
  border: 1px solid #EDE5D5;
}

.detail-card:hover {
  background: #F5EDE0;
}

.detail-card-key {
  font-weight: 700;
  font-size: 0.72rem;
  color: #7A6E63;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.detail-card-val {
  font-size: 0.9rem;
  color: #3C3028;
  line-height: 1.6;
  word-break: break-all;
}

/* Overview cards */
.overview-card {
  background: #FBF7F0;
  border-radius: 8px;
  padding: 0.9rem 1.1rem;
  margin-bottom: 0.45rem;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s, transform 0.15s;
  border-left: 3px solid transparent;
  border: 1px solid #EDE5D5;
}

.overview-card:hover {
  background: #F5EDE0;
  box-shadow: 0 2px 12px rgba(200, 162, 92, 0.1);
  transform: translateX(3px);
}

.ov-card-top {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}

.ov-card-icon {
  font-size: 1.3rem;
  flex-shrink: 0;
}

.ov-card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.ov-card-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #3C3028;
}

.ov-card-val {
  font-size: 0.78rem;
  color: #8B6F3D;
  font-weight: 500;
}

.ov-card-arrow {
  font-size: 0.9rem;
  color: #B8A99A;
  flex-shrink: 0;
  transition: color 0.2s, transform 0.2s;
}

.overview-card:hover .ov-card-arrow {
  color: #C8A25C;
  transform: translateX(2px);
}

.ov-card-extra {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px dashed #D4C4A8;
  font-size: 0.7rem;
  color: #A89888;
  display: flex;
  gap: 0.3rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ===== Responsive ===== */
@media (max-width: 900px) {
  .profile-page { height: auto; padding: 0 0.8rem 1rem; }

  .profile-main {
    flex-direction: column;
  }

  .mindmap-panel {
    flex: none;
    aspect-ratio: 1000 / 700;
  }

  .detail-panel {
    max-height: 360px;
  }

  .dim-node-card {
    min-width: 100px;
    padding: 0.5rem 0.7rem;
    border-radius: 14px;
  }

  .dim-icon { font-size: 1.1rem; }
  .dim-title { font-size: 0.7rem; }
  .dim-val { font-size: 0.65rem; }
  .dim-sub span { font-size: 0.58rem; max-width: 80px; }

  .center-node { width: 80px; height: 80px; }
  .center-emoji { font-size: 1.3rem; }
  .center-label { font-size: 0.6rem; }
}
</style>
