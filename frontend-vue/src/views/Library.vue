<template>
  <div class="library-page">
    <div class="page-header library">
      <h1>📚 资源库</h1>
      <p>上传 PDF 文档，选中文字让 AI 帮你解释</p>
    </div>

    <div class="library-main">
      <!-- ====== Left: upload + file list ====== -->
      <div class="library-sidebar">
        <!-- Upload area -->
        <div class="upload-section">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".pdf"
            :on-change="handleFileChange"
            :show-file-list="false"
            drag
          >
            <div class="upload-dropzone">
              <span style="font-size:2rem;">📄</span>
              <p>拖拽或点击上传 PDF</p>
              <p style="font-size:0.7rem;color:#A89888;">单个文件不超过 50MB</p>
            </div>
          </el-upload>
          <el-button
            v-if="pendingFile"
            type="primary"
            @click="doUpload"
            :loading="uploading"
            style="width:100%; margin-top:0.5rem;"
          >
            📤 上传 {{ pendingFile.name }}
          </el-button>
        </div>

        <el-divider style="margin:0.8rem 0;" />

        <!-- File list -->
        <div class="file-list">
          <div v-if="files.length === 0" class="empty-files">
            <span style="font-size:2rem;">📭</span>
            <p>暂无上传文件</p>
          </div>
          <div
            v-for="f in files"
            :key="f.id"
            :class="['file-item', { active: selectedFile?.id === f.id }]"
            @click="openFile(f)"
          >
            <div class="file-item-top">
              <span class="file-item-icon">📄</span>
              <div class="file-item-info">
                <span class="file-item-name">{{ f.filename }}</span>
                <span class="file-item-meta">{{ formatDate(f.created_at) }} · {{ f.text_length }} 字</span>
              </div>
            </div>
            <el-button
              text
              type="danger"
              size="small"
              @click.stop="handleDelete(f)"
            >
              🗑️
            </el-button>
          </div>
        </div>
      </div>

      <!-- ====== Right: PDF viewer + text + AI ====== -->
      <div class="library-content">
        <template v-if="!selectedFile">
          <div class="no-file-selected">
            <span style="font-size:4rem;">📂</span>
            <h3>选择一个文件开始阅读</h3>
            <p>上传 PDF 后，点击左侧文件即可查看</p>
          </div>
        </template>

        <template v-else>
          <!-- PDF viewer -->
          <div class="pdf-viewer-section">
            <div class="section-header">
              <span>📖 {{ selectedFile.filename }}</span>
              <el-button size="small" @click="selectedFile = null">关闭</el-button>
            </div>
            <div class="pdf-viewer">
              <iframe
                :src="pdfViewUrl"
                frameborder="0"
                class="pdf-iframe"
              />
            </div>
          </div>

          <!-- Text selection + AI explain -->
          <div class="explain-section">
            <div class="section-header">
              <span>📝 选中文字 → AI 解释</span>
              <el-button
                type="primary"
                size="small"
                :disabled="!selectedText || explaining"
                :loading="explaining"
                @click="doExplain"
              >
                🤖 AI 解释
              </el-button>
            </div>
            <div class="text-area-wrapper">
              <textarea
                v-model="selectedText"
                class="explain-textarea"
                placeholder="在 PDF 中选中文字后粘贴到此处，点击下方按钮让 AI 解释..."
                rows="4"
              ></textarea>
            </div>

            <!-- Explanation result -->
            <div v-if="explanation" class="explain-result">
              <div class="explain-result-header">
                <span>💡 AI 解释结果</span>
                <el-button text size="small" @click="explanation = ''">清除</el-button>
              </div>
              <div class="markdown-content" v-html="renderMd(explanation)" />
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
import { useAuthStore } from '../stores/auth'
import { listFiles, deleteFile, explainText, getPdfUrl } from '../api'
import MarkdownIt from 'markdown-it'
import { ElMessage, ElMessageBox } from 'element-plus'

const store = useStudentStore()
const auth = useAuthStore()
const md = new MarkdownIt()

const uploadRef = ref(null)
const pendingFile = ref(null)
const uploading = ref(false)
const files = ref([])
const selectedFile = ref(null)
const selectedText = ref('')
const explaining = ref(false)
const explanation = ref('')

const pdfViewUrl = computed(() => {
  if (!selectedFile.value || !store.currentStudentId) return ''
  const baseUrl = import.meta.env.DEV ? 'http://127.0.0.1:8000' : ''
  const token = auth.token || localStorage.getItem('token')
  const url = getPdfUrl(selectedFile.value.id, store.currentStudentId)
  return `${baseUrl}${url}&token=${encodeURIComponent(token || '')}`
})

function formatDate(d) {
  if (!d) return ''
  try { return new Date(d).toLocaleDateString('zh-CN') } catch { return d }
}

function handleFileChange(file) {
  pendingFile.value = file.raw
}

async function doUpload() {
  if (!pendingFile.value || !store.currentStudentId) return
  uploading.value = true
  try {
    const token = auth.token || localStorage.getItem('token')
    const form = new FormData()
    form.append('file', pendingFile.value)
    form.append('student_id', String(store.currentStudentId))

    const baseUrl = import.meta.env.DEV ? 'http://127.0.0.1:8000' : ''
    const resp = await fetch(`${baseUrl}/api/library/upload`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: form,
    })

    if (!resp.ok) {
      const err = await resp.json()
      throw new Error(err.detail || '上传失败')
    }

    await resp.json()
    ElMessage.success('上传成功')
    pendingFile.value = null
    await loadFiles()
  } catch (e) {
    ElMessage.error('上传失败：' + (e.response?.data?.detail || e.message))
  } finally {
    uploading.value = false
  }
}

async function loadFiles() {
  if (!store.currentStudentId) return
  try {
    const data = await listFiles(store.currentStudentId)
    files.value = data.files || []
  } catch (e) { /* ignore */ }
}

async function openFile(f) {
  selectedFile.value = f
  selectedText.value = ''
  explanation.value = ''
}

async function handleDelete(f) {
  try {
    await ElMessageBox.confirm(`确认删除「${f.filename}」？`, '删除文件', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteFile(f.id, store.currentStudentId)
    ElMessage.success('已删除')
    if (selectedFile.value?.id === f.id) {
      selectedFile.value = null
    }
    await loadFiles()
  } catch { /* cancelled */ }
}

async function doExplain() {
  if (!selectedText.value.trim() || !selectedFile.value) return
  explaining.value = true
  explanation.value = ''
  try {
    const result = await explainText(store.currentStudentId, selectedFile.value.id, selectedText.value)
    explanation.value = result.explanation || '未能生成解释'
  } catch (e) {
    ElMessage.error('解释失败：' + (e.response?.data?.detail || e.message))
  } finally {
    explaining.value = false
  }
}

function renderMd(content) {
  return md.render(content || '')
}

onMounted(() => {
  loadFiles()
})
</script>

<style scoped>
.library-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100px);
  padding: 0 1.2rem 0.8rem;
}

/* ===== Main split ===== */
.library-main {
  flex: 1;
  display: flex;
  gap: 1rem;
  min-height: 0;
}

/* ===== Left sidebar ===== */
.library-sidebar {
  width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #fff 0%, #FFFEF9 100%);
  border-radius: 16px;
  padding: 1rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  overflow: hidden;
}

.upload-section {
  flex-shrink: 0;
}

.upload-dropzone {
  text-align: center;
  padding: 0.5rem 0;
  cursor: pointer;
}

.upload-dropzone p {
  margin: 0.2rem 0 0;
  font-size: 0.78rem;
  color: #7A6E63;
}

.file-list {
  flex: 1;
  overflow-y: auto;
}

.empty-files {
  text-align: center;
  padding: 1.5rem 0;
  color: #7A6E63;
  font-size: 0.82rem;
}

.empty-files p { margin: 0.3rem 0 0; }

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 0.6rem;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 2px;
}

.file-item:hover { background: linear-gradient(135deg, #F5EDE0, #F5EDE0); }
.file-item.active { background: linear-gradient(135deg, #F5EDE0, #FBF7F0); }

.file-item-top {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
  flex: 1;
}

.file-item-icon { font-size: 1.2rem; flex-shrink: 0; }

.file-item-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.file-item-name {
  font-size: 0.78rem;
  font-weight: 600;
  color: #3C3028;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-item-meta {
  font-size: 0.65rem;
  color: #7A6E63;
}

/* ===== Right content ===== */
.library-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  min-width: 0;
  min-height: 0;
}

.no-file-selected {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #FBF7F0 0%, #FBF7F0 100%);
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  color: #7A6E63;
}

.no-file-selected h3 { margin: 0.5rem 0 0.2rem; color: #7A6E63; }
.no-file-selected p { font-size: 0.82rem; margin: 0; color: #7A6E63; }

/* PDF viewer */
.pdf-viewer-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  overflow: hidden;
  min-height: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 1rem;
  border-bottom: 1px solid #D8D0C4;
  font-weight: 600;
  font-size: 0.85rem;
  color: #3C3028;
  flex-shrink: 0;
  background: linear-gradient(135deg, #FBF7F0, #FBF7F0);
}

/* Fix element-plus upload drag area gray bg */
.upload-section :deep(.el-upload-dragger) {
  background: linear-gradient(135deg, #FBF7F0 0%, #FBF7F0 100%);
  border-color: #C8BFA8;
}

.upload-section :deep(.el-upload-dragger:hover) {
  border-color: #C8A25C;
  background: linear-gradient(135deg, #F5EDE0 0%, #FBF7F0 100%);
}

.pdf-viewer {
  flex: 1;
  overflow: hidden;
  background: #3C3028;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

/* Explain section */
.explain-section {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 46%;
  flex-shrink: 0;
}

.text-area-wrapper {
  padding: 0.6rem 1rem;
}

.explain-textarea {
  width: 100%;
  border: 1px solid #C8BFA8;
  border-radius: 10px;
  padding: 0.6rem;
  font-size: 0.85rem;
  font-family: inherit;
  color: #3C3028;
  background: #fff;
  resize: vertical;
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.2s;
}

.explain-textarea:focus {
  border-color: #C8A25C;
}

/* Explanation result */
.explain-result {
  border-top: 1px solid #E8DED0;
  padding: 0;
}

.explain-result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  font-weight: 600;
  font-size: 0.82rem;
  color: #444;
  background: linear-gradient(135deg, #F5EDE0, #F5EDE0);
}

.markdown-content {
  padding: 0 1rem 0.8rem;
  font-size: 0.82rem;
  line-height: 1.7;
  color: #3C3028;
  max-height: 240px;
  overflow-y: auto;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  font-size: 0.95rem;
  color: #3C3028;
  margin: 0.5rem 0 0.3rem;
}

.markdown-content :deep(p) { margin: 0.3rem 0; }
.markdown-content :deep(li) { margin: 0.15rem 0; }
.markdown-content :deep(code) {
  background: #EDE5D8;
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 0.8rem;
}
</style>
