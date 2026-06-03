<template>
  <div class="intro-page">
    <!-- ==== LEFT PANEL ==== -->
    <div class="left-panel">
      <div class="intro-top-ornament"></div>

      <!-- Hero -->
      <div class="intro-hero">
        <div class="hero-icon-ring">
          <span class="intro-hero-icon">📚</span>
        </div>
        <h2>多智能体个性化学习资源生成系统</h2>
        <p>十个专业 AI Agent 协作，打造完整的个性化学习闭环</p>
        <div class="hero-tags">
          <span>🤖 多智能体协同</span>
          <span>🎯 个性化生成</span>
          <span>🔄 完整闭环</span>
        </div>
      </div>

      <!-- Stats -->
      <div class="intro-stat-row">
        <div class="intro-stat clickable-card" v-for="s in stats" :key="s.label" @click="go(s.route)">
          <div class="stat-accent" :class="s.accent"></div>
          <span class="intro-stat-val">{{ s.val }}</span>
          <span class="intro-stat-lbl">{{ s.label }}</span>
        </div>
      </div>

      <div class="intro-divider"><span class="divider-diamond">◆</span></div>

      <!-- Core capabilities -->
      <div class="section-header">
        <h3>核心能力</h3>
        <p>五大智能模块覆盖学习全流程</p>
      </div>
      <div class="feature-grid">
        <div class="feature-card clickable-card" v-for="f in features" :key="f.icon" @click="go(f.route)">
          <div class="feat-icon-box" :style="{ background: f.bg }">
            <span>{{ f.icon }}</span>
          </div>
          <div class="feat-body">
            <h4>{{ f.title }}</h4>
            <p>{{ f.desc }}</p>
          </div>
        </div>
      </div>

      <!-- Quick start -->
      <div class="quickstart">
        <div class="quickstart-inner">
          <span class="quickstart-label">🚀 快速开始</span>
          <div class="quickstart-steps">
            <template v-for="(s, i) in steps" :key="i">
              <div class="qs-step">
                <span class="qs-num">{{ i + 1 }}</span>
                <span>{{ s }}</span>
              </div>
              <span v-if="i < steps.length - 1" class="qs-arrow">→</span>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- ==== RIGHT PANEL ==== -->
    <div class="right-panel">
      <div class="arch-section">
        <h3 class="arch-title">🤖 多智能体协作架构</h3>
        <p class="arch-subtitle">十个专业 Agent 四层协同</p>

        <div class="arch-flow">

          <div class="flow-row single">
            <div class="flow-tag gold">编排层</div>
            <div class="flow-node">
              <div class="node-card gold">
                <span class="node-icon">🎯</span>
                <div class="node-info">
                  <span class="node-name">Orchestrator</span>
                  <span class="node-role">主编排协调者</span>
                </div>
                <div class="node-badge">意图识别 · 任务分发 · 结果汇总</div>
              </div>
            </div>
          </div>

          <div class="flow-connect">
            <div class="connect-line"></div>
            <div class="connect-label">解析意图 · 分发任务</div>
            <div class="connect-line"></div>
          </div>

          <div class="flow-row single">
            <div class="flow-tag green">画像层</div>
            <div class="flow-node">
              <div class="node-card green clickable-card" @click="go('/profile')">
                <span class="node-icon">🧠</span>
                <div class="node-info">
                  <span class="node-name">ProfileAgent</span>
                  <span class="node-role">学习画像分析师</span>
                </div>
                <div class="node-badge">对话式采集 · 6维特征 · 画像持续更新</div>
              </div>
            </div>
          </div>

          <div class="flow-branch">
            <div class="branch-stem"></div>
            <div class="branch-label">提供画像 · 个性化参数注入</div>
            <div class="branch-row">
              <div class="branch-line left"></div>
              <div class="branch-line mid"></div>
              <div class="branch-line right"></div>
            </div>
          </div>

          <div class="flow-row">
            <div class="flow-tag blue">资源生成层</div>
            <div class="flow-grid">
              <div v-for="a in resourceAgents" :key="a.name" class="node-card blue clickable-card" @click="go(a.route)">
                <span class="node-icon">{{ a.icon }}</span>
                <div class="node-info">
                  <span class="node-name">{{ a.name }}</span>
                  <span class="node-role">{{ a.role }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="flow-connect reverse">
            <div class="connect-line"></div>
            <div class="connect-label">汇总资源 · 形成知识体系</div>
            <div class="connect-line"></div>
          </div>

          <div class="flow-row">
            <div class="flow-tag red">应用交付层</div>
            <div class="flow-cards">
              <div v-for="a in appAgents" :key="a.name" class="node-card red clickable-card" @click="go(a.route)">
                <span class="node-icon">{{ a.icon }}</span>
                <div class="node-info">
                  <span class="node-name">{{ a.name }}</span>
                  <span class="node-role">{{ a.role }}</span>
                </div>
                <div class="node-badge">{{ a.ability }}</div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function go(path) {
  if (path) router.push(path)
}

const stats = [
  { val: '10+', label: '专业智能体', accent: 'a1', route: '/welcome' },
  { val: '6', label: '资源类型', accent: 'a2', route: '/resources' },
  { val: '6维', label: '学习画像', accent: 'a3', route: '/profile' },
  { val: '6', label: '核心功能模块', accent: 'a4', route: '/welcome' },
]

const features = [
  { icon: '🧠', title: '对话式学习画像构建', desc: '摒弃传统表单，通过自然语言对话自动抽取6维学习特征。涵盖知识基础、认知风格、学习节奏、模态偏好、易错模式、动机因素。', bg: 'linear-gradient(135deg, #f5f0e8, #ede3d4)', route: '/profile' },
  { icon: '🤖', title: '多智能体协同资源生成', desc: '10+专业智能体各司其职，协作生成课程文档、思维导图、练习题、拓展阅读、视频脚本、代码案例等6类个性化资源。', bg: 'linear-gradient(135deg, #eef3f0, #dce8e0)', route: '/resources' },
  { icon: '🗺️', title: '个性化学习路径规划', desc: '基于学生画像和资源库，智能规划科学学习路径。分阶段、分类型安排学习节点，持续跟踪进度。', bg: 'linear-gradient(135deg, #eef1f4, #dce3e8)', route: '/learning-path' },
  { icon: '💡', title: '多模态智能辅导', desc: '文字解答 + 图解说明 + 类比讲解 + 举一反三。TutorAgent根据学生认知风格调整讲解方式。', bg: 'linear-gradient(135deg, #f5f0ee, #ede0dc)', route: '/tutoring' },
  { icon: '📊', title: '精准学习效果评估', desc: '多维度评估知识掌握度、进步趋势、薄弱环节、学习效率、资源适配度。自动生成改进建议。', bg: 'linear-gradient(135deg, #f5f0e8, #ede3d4)', route: '/assessment' },
  { icon: '🕸️', title: '知识图谱可视化', desc: '基于学习画像自动构建知识图谱，直观展示已掌握、薄弱点、目标主题的关联关系。一图看清学习全局。', bg: 'linear-gradient(135deg, #f0ede8, #e6dcd0)', route: '/knowledge-graph' },
]

const steps = ['构建画像 — 描述你的学习情况', '生成资源 — 选择课程主题一键生成', '规划路径 — 获取科学学习路线图', '开始学习 — 辅导+评估闭环提升']

const resourceAgents = [
  { icon: '📝', name: 'DocAgent', role: '课程文档专家', route: '/resources' },
  { icon: '🧩', name: 'MindMapAgent', role: '知识结构设计师', route: '/resources' },
  { icon: '✏️', name: 'ExerciseAgent', role: '题库设计专家', route: '/resources' },
  { icon: '📖', name: 'ReadingAgent', role: '拓展阅读推荐师', route: '/resources' },
  { icon: '🎬', name: 'VideoAgent', role: '教学视频编导', route: '/resources' },
  { icon: '💻', name: 'CodeAgent', role: '编程案例导师', route: '/resources' },
]

const appAgents = [
  { icon: '🗺️', name: 'PathAgent', role: '学习路径规划师', ability: '阶段化路径 · 资源匹配 · 时长规划', route: '/learning-path' },
  { icon: '🤖', name: 'TutorAgent', role: '智能辅导老师', ability: '多模态答疑 · 认知风格适配 · 举一反三', route: '/tutoring' },
  { icon: '🕸️', name: 'KnowledgeGraph', role: '知识图谱引擎', ability: '关系挖掘 · 图谱可视化 · 薄弱点诊断', route: '/knowledge-graph' },
  { icon: '📊', name: 'AssessmentAgent', role: '学习评估分析师', ability: '6维评估 · 趋势分析 · 改进建议', route: '/assessment' },
]
</script>

<style scoped>
/* ===== PAGE LAYOUT ===== */
.intro-page {
  display: flex;
  height: 100%;
  gap: 0;
}

/* ---- Left Panel ---- */
.left-panel {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem 2rem;
  display: flex;
  flex-direction: column;
}

.intro-top-ornament {
  height: 4px;
  background: linear-gradient(90deg, transparent 0%, #C8A25C 30%, #D4B86C 50%, #C8A25C 70%, transparent 100%);
  margin-bottom: 1.2rem;
  flex-shrink: 0;
}

/* ---- Right Panel ---- */
.right-panel {
  flex: 1;
  background: linear-gradient(180deg, #FBF7F0, #F5EDE0);
  border-left: 1px solid #E8E0D5;
  overflow-y: auto;
  padding: 1rem 1.8rem 2rem;
  display: flex;
}

.arch-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* ---- Hero ---- */
.intro-hero {
  text-align: center;
  padding: 1.8rem 2rem 1.4rem;
  background: linear-gradient(180deg, #FBF7F0 0%, #FFFEF9 60%, #FFFEF9 100%);
  border-radius: 12px;
  border: 1px solid #E8E0D5;
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
}

.intro-hero::after {
  content: '';
  position: absolute;
  bottom: 0; left: 50%;
  transform: translateX(-50%);
  width: 40%;
  height: 1px;
  background: linear-gradient(90deg, transparent, #D4C4A8, transparent);
}

.hero-icon-ring {
  width: 76px;
  height: 76px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FBF7F0, #EDE3D4);
  border: 2px solid #D4C4A8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 0.8rem;
  box-shadow: 0 2px 12px rgba(200, 162, 92, 0.12);
}

.intro-hero-icon {
  font-size: 2.2rem;
  line-height: 1;
}

.intro-hero h2 {
  font-size: 1.4rem;
  font-weight: 700;
  color: #3C3028;
  margin: 0 0 0.3rem;
  letter-spacing: 0.04em;
}

.intro-hero p {
  font-size: 0.88rem;
  color: #7A6E63;
  margin: 0 0 0.8rem;
}

.hero-tags {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  flex-wrap: wrap;
}

.hero-tags span {
  font-size: 0.74rem;
  color: #8B6F3D;
  background: rgba(200, 162, 92, 0.1);
  border: 1px solid rgba(200, 162, 92, 0.18);
  padding: 0.25rem 0.7rem;
  border-radius: 14px;
  font-weight: 500;
}

/* ---- Clickable cards ---- */
.clickable-card {
  cursor: pointer;
  transition: all 0.2s;
}
.clickable-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(60, 48, 40, 0.1);
}

/* ---- Stats ---- */
.intro-stat-row {
  display: flex;
  gap: 0.7rem;
  margin-top: 1rem;
  flex-shrink: 0;
}

.intro-stat {
  flex: 1;
  background: #FFFEF9;
  border-radius: 10px;
  padding: 0.9rem 0.6rem 0.7rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  border: 1px solid #E8E0D5;
  position: relative;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.intro-stat:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(60, 48, 40, 0.08);
}

.stat-accent {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 4px;
}

.stat-accent.a1 { background: linear-gradient(90deg, #C8A25C, #D4B86C); }
.stat-accent.a2 { background: linear-gradient(90deg, #3D7A5C, #5DA07C); }
.stat-accent.a3 { background: linear-gradient(90deg, #5D7A8A, #7D9AAA); }
.stat-accent.a4 { background: linear-gradient(90deg, #722F37, #924F57); }

.intro-stat-val {
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(135deg, #C8A25C, #B8934F);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-top: 0.1rem;
}

.intro-stat-lbl {
  font-size: 0.76rem;
  color: #7A6E63;
  font-weight: 500;
}

/* ---- Divider ---- */
.intro-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.2rem 0 0.8rem;
  flex-shrink: 0;
}

.divider-diamond {
  color: #D4C4A8;
  font-size: 0.45rem;
}

/* ---- Section header ---- */
.section-header {
  text-align: center;
  margin-bottom: 0.7rem;
  flex-shrink: 0;
}

.section-header h3 {
  font-size: 0.95rem;
  font-weight: 700;
  color: #3C3028;
  margin: 0 0 0.15rem;
}

.section-header p {
  font-size: 0.78rem;
  color: #A89880;
  margin: 0;
}

/* ---- Feature grid ---- */
.feature-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.6rem;
  flex-shrink: 0;
}

.feature-card {
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
  background: #FFFEF9;
  border-radius: 10px;
  padding: 0.8rem 0.9rem;
  border: 1px solid #EDE5D5;
  transition: all 0.2s;
}

.feature-card:hover {
  border-color: #D4C4A8;
  box-shadow: 0 4px 16px rgba(60, 48, 40, 0.06);
  transform: translateY(-2px);
}

.feat-icon-box {
  width: 46px;
  height: 46px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feat-icon-box span {
  font-size: 1.4rem;
  line-height: 1;
}

.feat-body {
  flex: 1;
  min-width: 0;
}

.feat-body h4 {
  margin: 0;
  font-size: 0.85rem;
  color: #3C3028;
  font-weight: 600;
}

.feat-body p {
  margin: 0.15rem 0 0 0;
  font-size: 0.74rem;
  color: #7A6E63;
  line-height: 1.5;
}

/* ---- Quick start ---- */
.quickstart {
  margin-top: 0.8rem;
  background: linear-gradient(135deg, #FBF7F0, #F5EDE0);
  border-radius: 10px;
  border: 1px solid #E8E0D5;
  flex-shrink: 0;
}

.quickstart-inner {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.6rem 1rem;
}

.quickstart-label {
  font-size: 0.84rem;
  font-weight: 700;
  color: #5C4F42;
  white-space: nowrap;
  flex-shrink: 0;
}

.quickstart-steps {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-wrap: wrap;
  flex: 1;
}

.qs-step {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.76rem;
  color: #5C4F42;
}

.qs-num {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #C8A25C, #B8934F);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.7rem;
  flex-shrink: 0;
}

.qs-arrow {
  color: #D4C4A8;
  font-size: 0.8rem;
  flex-shrink: 0;
}

/* ================================================ */
/* ===== RIGHT PANEL — Agent Architecture Flow ===== */
/* ================================================ */

.arch-title {
  text-align: center;
  font-size: 0.95rem;
  font-weight: 700;
  color: #3C3028;
  margin: 0 0 0.15rem;
}

.arch-subtitle {
  text-align: center;
  font-size: 0.72rem;
  color: #A89880;
  margin: 0 0 1rem;
}

/* ===== Keyframes ===== */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes flowDash {
  0%   { background-position: 0 0; }
  100% { background-position: 24px 0; }
}
@keyframes flowPulse {
  0%, 100% { opacity: 0.35; }
  50%      { opacity: 1; }
}
@keyframes iconBeat {
  0%, 100% { transform: scale(1); }
  15%      { transform: scale(1.13); }
  30%      { transform: scale(1); }
}
@keyframes glowBreathe {
  0%, 100% { box-shadow: 0 0 0 0 rgba(200, 162, 92, 0); }
  50%      { box-shadow: 0 0 0 5px rgba(200, 162, 92, 0.07); }
}

/* Flow layout */
.arch-flow {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0;
  flex: 1;
  justify-content: center;
  padding: 0 0.5rem;
}

.flow-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  width: 100%;
  animation: fadeInUp 0.5s ease-out both;
}

.flow-row:nth-child(1) { animation-delay: 0.08s; }
.flow-row:nth-child(3) { animation-delay: 0.45s; }
.flow-row:nth-child(5) { animation-delay: 0.82s; }
.flow-row:nth-child(7) { animation-delay: 1.2s; }

.flow-tag {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  padding: 0.2rem 0.8rem;
  border-radius: 4px;
}

.flow-tag.gold  { color: #8B6F3D; background: rgba(200, 162, 92, 0.12); }
.flow-tag.green { color: #4A7C63; background: rgba(127, 160, 142, 0.12); }
.flow-tag.blue  { color: #3D6A7A; background: rgba(93, 122, 138, 0.12); }
.flow-tag.red   { color: #8B3A40; background: rgba(114, 47, 55, 0.1); }

.flow-node {
  display: flex;
  justify-content: center;
  width: 100%;
}

.node-card {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  background: #FFFEF9;
  border-radius: 10px;
  padding: 0.7rem 1.1rem;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}

.node-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 4px;
}

.node-card.gold  { border: 1px solid #E0D5C0; }
.node-card.gold::before  { background: #C8A25C; }
.node-card.green { border: 1px solid #D5E0D8; }
.node-card.green::before { background: #7FA08E; }
.node-card.blue  { border: 1px solid #D5DCE0; }
.node-card.blue::before  { background: #5D7A8A; }
.node-card.red   { border: 1px solid #E0D2D4; }
.node-card.red::before   { background: #722F37; }

.node-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(60, 48, 40, 0.1);
}

.node-card:hover.gold  { border-color: #C8A25C; }
.node-card:hover.green { border-color: #7FA08E; }
.node-card:hover.blue  { border-color: #5D7A8A; }
.node-card:hover.red   { border-color: #722F37; }

.node-card:hover .node-icon {
  animation: iconBeat 0.45s ease-out;
}

.node-card.gold {
  animation: glowBreathe 3s ease-in-out infinite;
}

.node-icon {
  font-size: 1.8rem;
  flex-shrink: 0;
  line-height: 1;
  width: 2rem;
  text-align: center;
}

.node-info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  min-width: 0;
}

.node-name {
  font-size: 0.9rem;
  font-weight: 700;
  color: #3C3028;
  letter-spacing: 0.02em;
}

.node-role {
  font-size: 0.74rem;
  color: #7A6E63;
  font-weight: 500;
}

.node-badge {
  font-size: 0.7rem;
  color: #A89880;
  background: rgba(200, 162, 92, 0.06);
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
  white-space: nowrap;
}

.flow-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.6rem;
  width: 100%;
}

.flow-grid .node-card {
  padding: 0.55rem 0.7rem;
}

.flow-grid .node-icon {
  font-size: 1.35rem;
  width: 1.6rem;
}

.flow-grid .node-name {
  font-size: 0.78rem;
}

.flow-grid .node-role {
  font-size: 0.68rem;
}

.flow-grid .node-badge {
  display: none;
}

.flow-cards {
  display: flex;
  gap: 0.6rem;
  width: 100%;
}

.flow-cards .node-card {
  flex: 1;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.35rem;
  padding: 0.7rem 0.5rem;
}

.flow-cards .node-icon {
  font-size: 1.5rem;
  width: auto;
}

.flow-cards .node-info {
  align-items: center;
}

.flow-cards .node-badge {
  white-space: normal;
  text-align: center;
}

/* Connectors */
.flow-connect {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.2rem 0;
  width: 100%;
  justify-content: center;
  animation: fadeInUp 0.5s ease-out both;
}

.flow-connect:nth-child(2) { animation-delay: 0.28s; }
.flow-connect:nth-child(6) { animation-delay: 1.05s; }

.connect-line {
  flex: 1;
  height: 2px;
  background: repeating-linear-gradient(90deg,
    #C8A25C 0px, #C8A25C 5px,
    transparent 5px, transparent 14px
  );
  background-size: 28px 2px;
  animation: flowDash 0.6s linear infinite, flowPulse 2s ease-in-out infinite;
}

.connect-label {
  font-size: 0.68rem;
  color: #B8A088;
  font-style: italic;
  white-space: nowrap;
  flex-shrink: 0;
  animation: flowPulse 2s ease-in-out infinite;
}

.flow-connect.reverse {
  flex-direction: row-reverse;
}

.flow-branch {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.2rem 0;
  gap: 0.1rem;
  width: 100%;
  animation: fadeInUp 0.5s ease-out both;
  animation-delay: 0.65s;
}

.branch-stem {
  width: 2px;
  height: 12px;
  background: repeating-linear-gradient(0deg,
    #D4C4A8 0px, #D4C4A8 4px,
    transparent 4px, transparent 8px
  );
  background-size: 100% 8px;
  animation: flowDash 0.4s linear infinite;
}

.branch-label {
  font-size: 0.68rem;
  color: #B8A088;
  font-style: italic;
  margin-bottom: 0.05rem;
  animation: flowPulse 2s ease-in-out infinite;
}

.branch-row {
  display: flex;
  align-items: flex-start;
  width: 100%;
}

.branch-line {
  height: 2px;
  background: #D4C4A8;
  flex: 1;
}

.branch-line.left {
  background: linear-gradient(135deg, transparent 20%, #D4C4A8 90%);
}

.branch-line.mid {
  flex: 0;
  width: 70px;
  height: 16px;
  border-left: 2px solid #D4C4A8;
  border-right: 2px solid #D4C4A8;
  border-bottom: 2px solid #D4C4A8;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  background: transparent;
  margin: 0 3px;
}

.branch-line.right {
  background: linear-gradient(225deg, transparent 20%, #D4C4A8 90%);
}
</style>
