<template>
  <div class="lp-page">
    <div class="page-header path">
      <h1>🗺️ 个性化学习路径规划</h1>
      <p>PathAgent 根据你的画像和资源，规划科学、动态的个性化学习路线图</p>
    </div>

    <ProfileBanner />

    <!-- Goal input -->
    <div class="goal-section">
      <div class="goal-input-row">
        <el-input
          v-model="courseGoal"
          placeholder="输入学习目标，如「掌握Python数据分析」..."
          size="large"
          clearable
          @keyup.enter="generate"
        >
          <template #prepend>🎯 学习目标</template>
        </el-input>
        <el-button type="primary" size="large" @click="generate" :loading="loading" class="goal-btn">
          🧭 生成路径
        </el-button>
      </div>
      <div v-if="hasProfile && suggestedGoals.length > 0" class="goal-suggestions">
        <span class="goal-suggest-label">💡 根据你的画像，试试这些目标：</span>
        <div class="goal-chips">
          <span
            v-for="(g, i) in suggestedGoals"
            :key="i"
            :class="['goal-chip', { active: courseGoal === g }]"
            @click="courseGoal = g"
          >{{ g }}</span>
        </div>
      </div>
    </div>

    <!-- Current path -->
    <template v-if="currentPath">
      <!-- Progress bar -->
      <div class="path-progress-bar">
        <div class="progress-info">
          <span class="progress-title">{{ currentPath.title || '当前路径' }}</span>
          <span class="progress-meta">
            共 {{ totalNodes }} 个节点 ·
            {{ completedNodes }} 已完成 ·
            预计 {{ currentPath.total_duration_hours || '?' }}h
          </span>
        </div>
        <el-progress
          :percentage="progressPercent"
          :color="progressPercent === 100 ? '#3D7A5C' : '#C8A25C'"
          :stroke-width="10"
          striped
          :striped-flow="true"
        />
      </div>

      <!-- Phase cards grid -->
      <div class="phase-grid">
        <div v-for="(phase, idx) in currentPath.phases || []" :key="idx" class="phase-card">
          <div class="phase-card-top">
            <div
              class="phase-badge"
              :style="{ background: phaseColors[idx % 5] }"
            >{{ phase.phase || idx + 1 }}</div>
            <div class="phase-card-top-right">
              <span class="phase-name">{{ phase.name }}</span>
              <span class="phase-duration">⏱️ {{ phase.duration_hours || 0 }}h · {{ (phase.nodes || []).length }}节点</span>
            </div>
          </div>
          <div class="phase-goal" :style="{ borderLeftColor: phaseColors[idx % 5] }">
            🎯 {{ phase.goal }}
          </div>

          <!-- Nodes -->
          <div class="phase-nodes" v-show="expandedPhases[idx] !== false">
            <template v-for="node in phase.nodes || []" :key="node.order">
              <div :class="['node-item', { 'node-done': node.completed }]">
                <div class="node-left">
                  <span class="node-icon">{{ node.completed ? '✅' : (nodeIcons[node.type] || '📌') }}</span>
                  <div class="node-info">
                    <div class="node-title-row">
                      <span class="node-order">{{ node.order }}.</span>
                      <span class="node-title">{{ node.title }}</span>
                    </div>
                    <div class="node-meta-row">
                      <span class="node-duration">{{ node.duration_min || 0 }}min</span>
                      <span :class="['res-tag', node.resource_type || 'doc']">{{ node.resource_type }}</span>
                    </div>
                  </div>
                </div>
                <div class="node-right">
                  <el-button
                    v-if="!node.completed"
                    size="small"
                    type="primary"
                    plain
                    :loading="completingNode === `${currentPathId}-${idx}-${node.order}`"
                    @click.stop="handleComplete(currentPathId, idx, node)"
                  >✓</el-button>
                  <span v-else class="node-done-badge">✓</span>
                </div>
              </div>

              <!-- Node extras: linked resources / books / links -->
              <div v-if="node.linked_resources && node.linked_resources.length > 0" class="node-extras">
                <router-link
                  v-for="lr in node.linked_resources"
                  :key="lr.id"
                  :to="`/resources?id=${lr.id}`"
                  class="extra-link"
                >📎 {{ lr.title }}</router-link>
              </div>
              <div v-if="node.books && node.books.length > 0" class="node-extras">
                <span v-for="(b, bi) in node.books" :key="'b'+bi" class="extra-tag book">
                  📚《{{ b.title }}》
                </span>
              </div>
              <div v-if="node.links && node.links.length > 0" class="node-extras">
                <a
                  v-for="(l, li) in node.links"
                  :key="'l'+li"
                  :href="l.url"
                  target="_blank"
                  rel="noopener"
                  class="extra-tag link"
                >🔗 {{ l.title }}</a>
              </div>
            </template>
          </div>

          <div class="phase-toggle-bar" @click="togglePhase(idx)">
            <span>{{ expandedPhases[idx] === false ? `展开 (${(phase.nodes || []).length}节点)` : '收起' }}</span>
          </div>
        </div>
      </div>

      <!-- Advice -->
      <div v-if="currentPath.advice" class="advice-box">
        <span class="advice-icon">💡</span>
        <span>{{ currentPath.advice }}</span>
      </div>
    </template>

    <!-- History -->
    <div class="history-section" v-if="historyPaths.length > 0">
      <div class="section-divider">
        <span class="divider-text">📋 历史路径 ({{ historyPaths.length }})</span>
      </div>
      <el-collapse>
        <el-collapse-item v-for="p in historyPaths" :key="p.id">
          <template #title>
            <div class="history-title-row">
              <div class="history-title-left">
                <span :class="['history-status-dot', p.status === 'completed' ? 'done' : 'active']" />
                <span class="history-title-text">{{ p.title }}</span>
                <span class="history-title-meta">{{ formatDate(p.created_at) }}</span>
              </div>
              <div class="history-title-right">
                <span :class="['history-status-tag', p.status === 'completed' ? 'done' : 'active']">
                  {{ p.status === 'completed' ? '已完成' : '进行中' }}
                </span>
                <el-button type="danger" size="small" text @click.stop="handleDeletePath(p)">🗑️</el-button>
              </div>
            </div>
          </template>
          <div class="history-body">
            <!-- Progress bar for history path -->
            <div class="history-progress-bar">
              <div class="history-progress-info">
                <span class="history-progress-meta">
                  共 {{ countAllNodes(p) }} 个节点 ·
                  {{ countCompletedNodes(p) }} 已完成 ·
                  预计 {{ (p.path && p.path.total_duration_hours) || '?' }}h
                </span>
                <span class="history-progress-pct" :style="{ color: pathProgressPercent(p) === 100 ? '#3D7A5C' : '#C8A25C' }">
                  {{ pathProgressPercent(p) }}%
                </span>
              </div>
              <el-progress
                :percentage="pathProgressPercent(p)"
                :color="pathProgressPercent(p) === 100 ? '#3D7A5C' : '#C8A25C'"
                :stroke-width="8"
                :striped="p.status !== 'completed'"
                :striped-flow="p.status !== 'completed'"
              />
            </div>
            <el-collapse>
              <el-collapse-item
                v-for="(phase, pidx) in (p.path && p.path.phases) || []"
                :key="phase.phase"
                :title="`📌 阶段${phase.phase}：${phase.name}（${phase.duration_hours || 0}h, ${(phase.nodes || []).length}个节点）`"
              >
                <div class="phase-goal small">🎯 {{ phase.goal }}</div>
                <template v-for="node in phase.nodes || []" :key="node.order">
                  <div :class="['node-item', { 'node-done': node.completed }]">
                    <div class="node-left">
                      <span class="node-icon">{{ node.completed ? '✅' : (nodeIcons[node.type] || '📌') }}</span>
                      <div class="node-info">
                        <div class="node-title-row">
                          <span class="node-order">{{ node.order }}.</span>
                          <span class="node-title">{{ node.title }}</span>
                          <span class="node-duration">{{ node.duration_min || 0 }}min</span>
                          <span :class="['res-tag', node.resource_type || 'doc']">{{ node.resource_type }}</span>
                        </div>
                      </div>
                    </div>
                    <div class="node-right">
                      <el-button
                        v-if="!node.completed"
                        size="small"
                        type="primary"
                        plain
                        :loading="completingNode === `${p.id}-${pidx}-${node.order}`"
                        @click.stop="handleComplete(p.id, pidx, node)"
                      >✓ 完成</el-button>
                      <span v-else class="node-done-badge">已完成</span>
                    </div>
                  </div>

                  <!-- Node extras -->
                  <div v-if="node.linked_resources && node.linked_resources.length > 0" class="node-extras">
                    <router-link
                      v-for="lr in node.linked_resources"
                      :key="lr.id"
                      :to="`/resources?id=${lr.id}`"
                      class="extra-link"
                    >📎 {{ lr.title }}</router-link>
                  </div>
                  <div v-if="node.books && node.books.length > 0" class="node-extras">
                    <span v-for="(b, bi) in node.books" :key="'b'+bi" class="extra-tag book">
                      📚《{{ b.title }}》
                    </span>
                  </div>
                  <div v-if="node.links && node.links.length > 0" class="node-extras">
                    <a
                      v-for="(l, li) in node.links"
                      :key="'l'+li"
                      :href="l.url"
                      target="_blank"
                      rel="noopener"
                      class="extra-tag link"
                    >🔗 {{ l.title }}</a>
                  </div>
                </template>
              </el-collapse-item>
            </el-collapse>
            <div v-if="p.path && p.path.advice" class="advice-box small">
              <span class="advice-icon">💡</span>
              <span>{{ p.path.advice }}</span>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>

    <div v-if="!currentPath && historyPaths.length === 0" class="empty-state">
      <span class="empty-icon">🗺️</span>
      <h3>还没有学习路径</h3>
      <p>输入学习目标，让 PathAgent 为你规划专属学习路线</p>
    </div>

    <!-- Loading overlay -->
    <teleport to="body">
      <div v-if="loading" class="path-overlay">
        <div class="path-modal">
          <span class="path-spin">🧭</span>
          <div class="path-title">正在规划学习路径...</div>
          <div class="path-sub">PathAgent 正在分析你的画像，匹配最佳学习资源，规划科学路线</div>
          <div class="path-dots">
            <span class="path-dot" v-for="i in 3" :key="i" :style="{ animationDelay: (i-1)*0.2 + 's' }"></span>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useStudentStore } from '../stores/student'
import { generatePath, getPaths, completePathNode, deletePath } from '../api'
import ProfileBanner from '../components/ProfileBanner.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const store = useStudentStore()
const courseGoal = ref('')
const loading = ref(false)
const currentPath = ref(null)
const currentPathId = ref(null)
const historyPaths = ref([])
const completingNode = ref(null)
const expandedPhases = reactive({})

const phaseColors = ['#C8A25C', '#722F37', '#3D7A5C', '#7FA08E', '#5D7A8A']
const nodeIcons = { study: '📖', practice: '✏️', review: '🔄', project: '🛠️', assessment: '📊' }

const hasProfile = computed(() => store.hasProfile)
const profile = computed(() => store.profile)

const totalNodes = computed(() => {
  if (!currentPath.value?.phases) return 0
  return currentPath.value.phases.reduce((s, p) => s + (p.nodes || []).length, 0)
})

const completedNodes = computed(() => {
  if (!currentPath.value?.phases) return 0
  return currentPath.value.phases.reduce((s, p) => s + (p.nodes || []).filter(n => n.completed).length, 0)
})

const progressPercent = computed(() => {
  if (totalNodes.value === 0) return 0
  return Math.round((completedNodes.value / totalNodes.value) * 100)
})

const suggestedGoals = computed(() => {
  if (!profile.value) return []
  const goals = []
  const p = profile.value
  const mf = p.motivation_factors || {}
  const kb = p.knowledge_base || {}
  if (mf.primary_goal && mf.primary_goal !== '个人兴趣') goals.push(mf.primary_goal)
  const targets = kb.target_topics || []
  for (const t of targets) {
    const goal = `掌握${t}`
    if (!goals.includes(goal)) goals.push(goal)
  }
  const weaks = kb.weak_points || []
  for (const w of weaks) {
    const goal = `攻克${w}薄弱点`
    if (!goals.includes(goal)) goals.push(goal)
  }
  return goals
})

function togglePhase(idx) {
  expandedPhases[idx] = expandedPhases[idx] === false ? true : false
}

function formatDate(d) {
  if (!d) return ''
  try { return new Date(d).toLocaleDateString('zh-CN') } catch { return d }
}

function countAllNodes(p) {
  if (!p.path?.phases) return 0
  return p.path.phases.reduce((s, ph) => s + (ph.nodes || []).length, 0)
}

function countCompletedNodes(p) {
  if (!p.path?.phases) return 0
  return p.path.phases.reduce((s, ph) => s + (ph.nodes || []).filter(n => n.completed).length, 0)
}

function pathProgressPercent(p) {
  const total = countAllNodes(p)
  if (total === 0) return 0
  return Math.round((countCompletedNodes(p) / total) * 100)
}

async function generate() {
  if (!store.currentStudentId) { ElMessage.warning('请先创建学生'); return }
  if (!courseGoal.value.trim()) { ElMessage.warning('请输入学习目标'); return }
  loading.value = true
  try {
    const result = await generatePath(store.currentStudentId, courseGoal.value)
    if (result.path) {
      currentPath.value = result.path
      currentPathId.value = result.path_id
      // Reset expanded state
      Object.keys(expandedPhases).forEach(k => delete expandedPhases[k])
      ElMessage.success('学习路径已生成！')
    }
  } catch (e) {
    ElMessage.error('生成失败：' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

async function handleComplete(pathId, phaseIdx, node) {
  if (!store.currentStudentId) return
  try {
    await ElMessageBox.confirm(
      `<div class="export-msg">
        <span class="export-msg-icon">✅</span>
        <div class="export-msg-body">
          <div class="export-msg-title">${node.title}</div>
          <div class="export-msg-meta">确认完成该节点？知识点将更新到学习画像中。</div>
        </div>
      </div>`,
      '确认完成',
      { confirmButtonText: '✅ 确认完成', cancelButtonText: '取消', dangerouslyUseHTMLString: true, customClass: 'export-confirm-dialog' }
    )
  } catch { return }

  const key = `${pathId}-${phaseIdx}-${node.order}`
  completingNode.value = key
  try {
    const result = await completePathNode(store.currentStudentId, pathId, phaseIdx, node.order)
    if (result.ok) {
      node.completed = true
      ElMessage.success(`「${node.title}」已完成！`)
      await store.loadProfile()
    } else {
      ElMessage.warning(result.message || '操作失败')
    }
  } catch (e) {
    ElMessage.error('操作失败：' + (e.response?.data?.detail || e.message))
  } finally {
    completingNode.value = null
  }
}

async function handleDeletePath(p) {
  try {
    await ElMessageBox.confirm(
      `<div class="export-msg">
        <span class="export-msg-icon">🗑️</span>
        <div class="export-msg-body">
          <div class="export-msg-title">${p.title}</div>
          <div class="export-msg-meta">确认删除该学习路径？<b>此操作不可恢复</b>。</div>
        </div>
      </div>`,
      '删除路径',
      { confirmButtonText: '🗑️ 删除', cancelButtonText: '取消', dangerouslyUseHTMLString: true, customClass: 'export-confirm-dialog' }
    )
  } catch { return }
  try {
    await deletePath(p.id, store.currentStudentId)
    historyPaths.value = historyPaths.value.filter(x => x.id !== p.id)
    ElMessage.success('已删除')
  } catch (e) {
    ElMessage.error('删除失败：' + (e.response?.data?.detail || e.message))
  }
}

onMounted(async () => {
  if (store.currentStudentId) {
    try {
      const data = await getPaths(store.currentStudentId)
      historyPaths.value = data.paths || []
    } catch { /* ignore */ }
  }
})
</script>

<style scoped>
.lp-page { padding: 0.6rem 1.2rem 0.8rem; }

/* Goal section */
.goal-section {
  background: #FFFEF9;
  border-radius: 8px;
  padding: 0.85rem 1.1rem;
  box-shadow: 0 1px 4px rgba(60, 48, 40, 0.05);
  margin-top: 0.5rem;
  border: 1px solid #E8E0D5;
}

.goal-input-row { display: flex; gap: 0.6rem; margin-bottom: 0; }
.goal-input { flex: 1; }
.goal-btn { flex-shrink: 0; min-width: 130px; }

.goal-suggestions {
  margin-top: 0.7rem;
  padding-top: 0.7rem;
  border-top: 1px dashed #D4C4A8;
}
.goal-suggest-label { font-size: 0.75rem; color: #7A6E63; display: block; margin-bottom: 0.4rem; }
.goal-chips { display: flex; flex-wrap: wrap; gap: 0.35rem; }

.goal-chip {
  background: #FBF7F0; color: #5C4F42;
  padding: 0.3rem 0.75rem; border-radius: 4px; font-size: 0.8rem;
  cursor: pointer; transition: all 0.2s;
  border: 1.5px solid #D4C4A8; user-select: none;
}
.goal-chip:hover { background: #F5EDE0; border-color: #C8A25C; }
.goal-chip.active {
  background: rgba(200,162,92,0.1);
  color: #8B6F3D; border-color: #C8A25C; font-weight: 600;
}

/* Progress bar */
.path-progress-bar {
  margin-top: 0.8rem;
  background: #FFFEF9;
  border-radius: 8px;
  padding: 0.85rem 1.2rem;
  box-shadow: 0 1px 4px rgba(60, 48, 40, 0.05);
  border: 1px solid #E8E0D5;
}
.progress-info { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.45rem; }
.progress-title { font-weight: 700; font-size: 0.9rem; color: #3C3028; }
.progress-meta { font-size: 0.75rem; color: #7A6E63; }

/* Phase grid */
.phase-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.65rem;
  margin-top: 0.65rem;
}

/* Phase card */
.phase-card {
  background: #FFFEF9; border-radius: 10px;
  box-shadow: 0 1px 4px rgba(60, 48, 40, 0.05);
  border: 1px solid #E8E0D5;
  overflow: hidden; display: flex; flex-direction: column;
  transition: box-shadow 0.2s;
}
.phase-card:hover { box-shadow: 0 4px 16px rgba(60, 48, 40, 0.1); }

.phase-card-top {
  display: flex; align-items: flex-start; gap: 0.5rem;
  padding: 0.6rem 0.8rem;
  background: linear-gradient(135deg, #FBF7F0, #F5EDE0);
}
.phase-badge {
  width: 32px; height: 32px; border-radius: 50%; color: white;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.85rem; flex-shrink: 0;
}
.phase-card-top-right { flex: 1; min-width: 0; }
.phase-name { font-weight: 700; font-size: 0.95rem; color: #3C3028; display: block; }
.phase-duration { font-size: 0.72rem; color: #7A6E63; margin-top: 2px; display: block; }

.phase-goal {
  padding: 0.4rem 1rem; font-size: 0.8rem; color: #5C4F42;
  border-left: 3px solid #C8A25C;
  background: #FBF7F0; margin: 0;
}
.phase-goal.small { margin: 0.4rem 0; font-size: 0.78rem; padding: 0.3rem 0.8rem; }

/* Phase nodes */
.phase-nodes { padding: 0.5rem; flex: 1; }

.node-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.4rem 0.6rem; margin: 2px 0;
  background: #FBF7F0; border-radius: 6px;
  transition: all 0.2s;
  border: 1px solid transparent;
}
.node-item:hover { background: #F5EDE0; border-color: #E8E0D5; }
.node-item.node-done { opacity: 0.7; background: #f3f8f5; }

.node-left { display: flex; align-items: flex-start; gap: 0.4rem; flex: 1; min-width: 0; }
.node-icon { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }
.node-info { min-width: 0; flex: 1; }
.node-title-row { display: flex; align-items: center; gap: 0.25rem; }
.node-order { font-size: 0.7rem; color: #A89880; font-weight: 600; flex-shrink: 0; }
.node-title { font-weight: 600; font-size: 0.82rem; color: #3C3028; }
.node-meta-row { display: flex; align-items: center; gap: 0.4rem; margin-top: 2px; }
.node-duration { font-size: 0.68rem; color: #A89880; }
.node-right { flex-shrink: 0; margin-left: 0.3rem; }
.node-done-badge { font-size: 0.85rem; color: #3D7A5C; font-weight: 700; }

/* Toggle bar */
.phase-toggle-bar {
  text-align: center; padding: 0.35rem; font-size: 0.72rem; color: #A89880;
  cursor: pointer; user-select: none; border-top: 1px solid #E8E0D5;
  transition: color 0.2s;
}
.phase-toggle-bar:hover { color: #C8A25C; }

/* Node extras */
.node-extras {
  display: flex; flex-wrap: wrap; gap: 0.3rem;
  padding: 0.2rem 0.4rem 0.2rem 2.2rem;
}
.extra-link {
  font-size: 0.68rem; background: rgba(200,162,92,0.1); color: #C8A25C;
  border: 1px solid rgba(200,162,92,0.2); border-radius: 10px; padding: 1px 6px;
  text-decoration: none; transition: background 0.2s;
}
.extra-link:hover { background: rgba(200,162,92,0.15); }
.extra-tag { font-size: 0.68rem; padding: 1px 6px; border-radius: 8px; }
.extra-tag.book { color: #8b6914; background: #fffdf5; border: 1px solid #f0e6c0; }
.extra-tag.link { color: #2a6eb0; background: #f5f9ff; border: 1px solid #d0e2f5; text-decoration: none; transition: background 0.2s; }
.extra-tag.link:hover { background: #e6f0ff; text-decoration: underline; }

/* Advice */
.advice-box {
  background: linear-gradient(135deg, #FBF7F0, #F5EDE0); border-radius: 8px;
  padding: 0.7rem 1.2rem; border: 1px solid rgba(200,162,92,0.15); margin-top: 0.6rem;
  display: flex; align-items: flex-start; gap: 0.4rem; font-size: 0.82rem; color: #5C4F42;
}
.advice-box.small { padding: 0.5rem 0.8rem; font-size: 0.78rem; margin-top: 0.4rem; }
.advice-icon { flex-shrink: 0; }

/* History */
.history-section { margin-top: 1.5rem; }
.section-divider { text-align: center; margin-bottom: 0.8rem; }
.divider-text { font-weight: 700; font-size: 0.9rem; color: #7A6E63; background: #FBF7F0; padding: 0.4rem 1rem; border-radius: 4px; }

.history-title-row {
  display: flex; justify-content: space-between; align-items: center;
  width: 100%; padding: 0.15rem 0.5rem 0.15rem 0;
}
.history-title-left { display: flex; align-items: center; gap: 0.6rem; }
.history-status-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.history-status-dot.done { background: #3D7A5C; }
.history-status-dot.active { background: #C8A25C; animation: pulse-dot 2s infinite; }
.history-title-text { font-weight: 600; font-size: 0.9rem; color: #3C3028; }
.history-title-meta { font-size: 0.78rem; color: #A89880; }
.history-title-right { display: flex; align-items: center; gap: 0.5rem; }
.history-status-tag { font-size: 0.75rem; padding: 3px 10px; border-radius: 4px; font-weight: 500; }
.history-status-tag.done { background: #f3f8f5; color: #3D7A5C; }
.history-status-tag.active { background: rgba(200,162,92,0.1); color: #8B6F3D; }

.history-body { padding: 0.3rem 0.7rem; }
.history-summary { font-size: 0.88rem; color: #7A6E63; margin: 0.3rem 0 0.6rem; }

.history-progress-bar {
  background: #FBF7F0;
  border-radius: 6px;
  padding: 0.6rem 0.8rem;
  margin-bottom: 0.6rem;
  border: 1px solid #E8E0D5;
}
.history-progress-info {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.4rem;
}
.history-progress-meta {
  font-size: 0.75rem;
  color: #7A6E63;
}
.history-progress-pct {
  font-size: 0.85rem;
  font-weight: 700;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* History collapse items */
.history-section :deep(.el-collapse-item__header) {
  height: auto !important;
  min-height: 44px;
  padding: 0.5rem 0.8rem;
  font-size: 0.88rem;
  line-height: 1.5;
}
.history-section :deep(.el-collapse-item__wrap) {
  border-bottom: none;
}
.history-body :deep(.el-collapse-item__header) {
  height: auto !important;
  min-height: 38px;
  padding: 0.35rem 0.6rem;
  font-size: 0.82rem;
  line-height: 1.5;
}
.history-body :deep(.el-collapse-item__content) {
  padding: 0.3rem 0;
}

/* Empty state */
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 4rem 2rem; color: #A89880;
}
.empty-icon { font-size: 3.5rem; margin-bottom: 0.5rem; }
.empty-state h3 { margin: 0.5rem 0 0.2rem; color: #7A6E63; }
.empty-state p { font-size: 0.85rem; color: #A89880; }

/* Loading overlay */
.path-overlay {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(30, 20, 14, 0.5);
  backdrop-filter: blur(5px);
  animation: fadeIn 0.25s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.path-modal {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.7rem;
  background: #FFFEF9;
  border-radius: 14px;
  padding: 2.5rem 3rem;
  box-shadow: 0 12px 48px rgba(30, 20, 14, 0.25);
  border: 1px solid #E8E0D5;
  text-align: center;
}

.path-spin {
  font-size: 3rem;
  animation: pathPulse 1.5s ease-in-out infinite;
}

@keyframes pathPulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.15); opacity: 0.7; }
}

.path-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #3C3028;
}

.path-sub {
  font-size: 0.82rem;
  color: #7A6E63;
  max-width: 300px;
  line-height: 1.5;
}

.path-dots {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.2rem;
}

.path-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #C8A25C;
  animation: dotBounce 0.8s ease-in-out infinite;
}

@keyframes dotBounce {
  0%, 100% { transform: translateY(0); opacity: 0.4; }
  50% { transform: translateY(-8px); opacity: 1; }
}
</style>
