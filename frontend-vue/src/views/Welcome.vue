<template>
  <div>
    <div class="page-header home">
      <h1>📚 多智能体个性化学习资源生成系统</h1>
      <p>基于 DeepSeek 大模型 · 10+ 智能体协作 · 6维动态画像 · 多模态资源生成</p>
    </div>

    <div class="stat-cards">
      <div class="stat-card">
        <div class="value">10+</div>
        <div class="label">专业智能体</div>
      </div>
      <div class="stat-card">
        <div class="value">6</div>
        <div class="label">资源类型</div>
      </div>
      <div class="stat-card">
        <div class="value">6维</div>
        <div class="label">学习画像</div>
      </div>
      <div class="stat-card">
        <div class="value">5</div>
        <div class="label">核心功能模块</div>
      </div>
    </div>

    <div class="section-title">🎯 核心功能</div>

    <div class="feature-grid">
      <div class="feature-card">
        <div class="icon">🧠</div>
        <h4>对话式学习画像构建</h4>
        <p>摒弃传统表单，通过自然语言对话自动抽取6维学习特征。涵盖知识基础、认知风格、学习节奏、模态偏好、易错模式、动机因素，支持随学随新。</p>
      </div>
      <div class="feature-card">
        <div class="icon">🤖</div>
        <h4>多智能体协同资源生成</h4>
        <p>10+专业智能体各司其职，协作生成课程文档、思维导图、练习题、拓展阅读、视频脚本、代码案例等6类个性化资源。</p>
      </div>
      <div class="feature-card">
        <div class="icon">🗺️</div>
        <h4>个性化学习路径规划</h4>
        <p>基于学生画像和资源库，智能规划科学学习路径。分阶段、分类型安排学习节点，持续跟踪进度。</p>
      </div>
      <div class="feature-card">
        <div class="icon">💡</div>
        <h4>多模态智能辅导</h4>
        <p>文字解答 + 图解说明 + 类比讲解 + 举一反三。TutorAgent根据学生认知风格调整讲解方式。</p>
      </div>
      <div class="feature-card">
        <div class="icon">📊</div>
        <h4>精准学习效果评估</h4>
        <p>多维度评估知识掌握度、进步趋势、薄弱环节、学习效率、资源适配度。自动生成改进建议。</p>
      </div>
    </div>

    <div class="section-title">🚀 快速开始</div>
    <div class="step-row">
      <div class="step-item"><div class="step-num">1</div><div><b>构建画像</b><br><span style="font-size:0.8rem;color:#888;">描述你的学习情况</span></div></div>
      <div class="step-arrow">→</div>
      <div class="step-item"><div class="step-num">2</div><div><b>生成资源</b><br><span style="font-size:0.8rem;color:#888;">选择课程主题一键生成</span></div></div>
      <div class="step-arrow">→</div>
      <div class="step-item"><div class="step-num">3</div><div><b>规划路径</b><br><span style="font-size:0.8rem;color:#888;">获取科学学习路线图</span></div></div>
      <div class="step-arrow">→</div>
      <div class="step-item"><div class="step-num">4</div><div><b>开始学习</b><br><span style="font-size:0.8rem;color:#888;">辅导+评估闭环提升</span></div></div>
    </div>

    <el-collapse style="margin-top:1.5rem;">
      <el-collapse-item title="🔍 多智能体架构一览">
        <el-table :data="agents" stripe size="small">
          <el-table-column prop="icon" label="" width="50" />
          <el-table-column prop="name" label="智能体" width="200" />
          <el-table-column prop="role" label="角色定位" />
          <el-table-column prop="ability" label="核心能力" />
        </el-table>
      </el-collapse-item>
    </el-collapse>

  </div>
</template>

<script setup>
const agents = [
  { icon: '🎯', name: 'Orchestrator', role: '主编排协调者', ability: '意图识别、任务分发、结果汇总' },
  { icon: '🧠', name: 'ProfileAgent', role: '学习画像分析师', ability: '对话式画像采集、6维特征提取、画像更新' },
  { icon: '📝', name: 'DocAgent', role: '课程文档专家', ability: '自适应难度、根据认知风格调整讲解方式' },
  { icon: '🧩', name: 'MindMapAgent', role: '知识结构设计师', ability: 'Mermaid思维导图、模块化知识拆解' },
  { icon: '✏️', name: 'ExerciseAgent', role: '题库设计专家', ability: '4种题型、针对易错点、难度分级' },
  { icon: '📖', name: 'ReadingAgent', role: '拓展阅读推荐师', ability: '三级阅读推荐、个性化阅读路线' },
  { icon: '🎬', name: 'VideoAgent', role: '教学视频编导', ability: '分镜脚本、可视化方案、互动设计' },
  { icon: '💻', name: 'CodeAgent', role: '编程案例导师', ability: '实战项目、分步实现、扩展挑战' },
  { icon: '🗺️', name: 'PathAgent', role: '学习路径规划师', ability: '阶段化路径、资源匹配、时长规划' },
  { icon: '🤖', name: 'TutorAgent', role: '智能辅导老师', ability: '多模态答疑、认知风格适配' },
  { icon: '📊', name: 'AssessmentAgent', role: '学习评估分析师', ability: '6维评估、趋势分析、改进建议' },
]
</script>

<style scoped>
</style>
