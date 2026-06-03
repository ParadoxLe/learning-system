import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

// Attach token to every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 globally
api.interceptors.response.use(
  r => r,
  error => {
    if (error.response?.status === 401) {
      const path = window.location.pathname
      // Don't redirect on login/register — let those pages show the error
      if (path !== '/login' && path !== '/register') {
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

// Auth
export function login(username, password, captchaId, captchaCode) {
  return api.post('/auth/login', { username, password, captcha_id: captchaId, captcha_code: captchaCode }).then(r => r.data)
}

export function getCaptcha() {
  return api.get('/auth/captcha').then(r => r.data)
}

export function register(username, password, captchaId, captchaCode) {
  return api.post('/auth/register', { username, password, captcha_id: captchaId, captcha_code: captchaCode }).then(r => r.data)
}

export function me() {
  return api.get('/auth/me').then(r => r.data)
}

export function updatePassword(oldPassword, newPassword) {
  return api.put('/auth/password', { old_password: oldPassword, new_password: newPassword }).then(r => r.data)
}

export function updateAvatar(avatarData) {
  return api.put('/auth/avatar', { avatar: avatarData }).then(r => r.data)
}

// Students
export function getStudents() {
  return api.get('/students/').then(r => r.data)
}

export function createStudent(data) {
  return api.post('/students/', data).then(r => r.data)
}

// Profile
export function profileChat(studentId, message) {
  return api.post('/profile/chat', { student_id: studentId, message }).then(r => r.data)
}

export function getProfile(studentId) {
  return api.get(`/profile/${studentId}`).then(r => r.data)
}

export function updateProfile(studentId, message) {
  return api.post(`/profile/${studentId}/update`, { message }).then(r => r.data)
}

// Resources
export function generateResources(data) {
  return api.post('/resources/generate', data).then(r => r.data)
}

export function getResources(studentId, resourceType) {
  const params = resourceType ? `?resource_type=${resourceType}` : ''
  return api.get(`/resources/${studentId}${params}`).then(r => r.data)
}

export function deleteResource(resourceId, studentId) {
  return api.delete(`/resources/${resourceId}`, { params: { student_id: studentId } }).then(r => r.data)
}

export function completeResource(studentId, resourceId) {
  return api.post('/resources/complete', { student_id: studentId, resource_id: resourceId }).then(r => r.data)
}

// Learning Path
export function generatePath(studentId, courseGoal) {
  return api.post('/learning-path/generate', { student_id: studentId, course_goal: courseGoal }).then(r => r.data)
}

export function getPaths(studentId) {
  return api.get(`/learning-path/${studentId}`).then(r => r.data)
}

export function completePathNode(studentId, pathId, phaseIdx, nodeOrder) {
  return api.post('/learning-path/complete-node', {
    student_id: studentId, path_id: pathId, phase_idx: phaseIdx, node_order: nodeOrder,
  }).then(r => r.data)
}

export function deletePath(pathId, studentId) {
  return api.delete(`/learning-path/${pathId}`, { params: { student_id: studentId } }).then(r => r.data)
}

// Tutor
export function askTutor(studentId, question, context = '') {
  return api.post('/tutor/ask', { student_id: studentId, question, context }).then(r => r.data)
}

// Assessment
export function evaluateLearning(studentId, learningData = {}) {
  return api.post('/assessment/evaluate', { student_id: studentId, learning_data: learningData }).then(r => r.data)
}

// Knowledge Graph
export function getKnowledgeGraph(studentId) {
  return api.get(`/knowledge-graph/${studentId}`).then(r => r.data)
}

// Quiz
export function generateQuiz(studentId, count = 5) {
  return api.post('/quiz/generate', { student_id: studentId, count }).then(r => r.data)
}

export function submitQuiz(studentId, answers, questions) {
  return api.post('/quiz/submit', { student_id: studentId, answers, questions }).then(r => r.data)
}

// Library
export function uploadPdf(studentId, file) {
  const form = new FormData()
  form.append('file', file)
  form.append('student_id', studentId)
  const token = localStorage.getItem('token')
  return fetch('/api/library/upload', {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  }).then(r => {
    if (!r.ok) return r.json().then(e => Promise.reject({ response: { data: e } }))
    return r.json()
  })
}

export function listFiles(studentId) {
  return api.get('/library/', { params: { student_id: studentId } }).then(r => r.data)
}

export function getFile(fileId, studentId) {
  return api.get(`/library/${fileId}`, { params: { student_id: studentId } }).then(r => r.data)
}

export function deleteFile(fileId, studentId) {
  return api.delete(`/library/${fileId}`, { params: { student_id: studentId } }).then(r => r.data)
}

export function explainText(studentId, fileId, selectedText) {
  return api.post('/library/explain', { student_id: studentId, file_id: fileId, selected_text: selectedText }).then(r => r.data)
}

export function getPdfUrl(fileId, studentId) {
  return `/api/library/${fileId}/pdf?student_id=${studentId}`
}

// Study Plans
export function getPlans(studentId, year, month) {
  return api.get(`/plans/${studentId}`, { params: { year, month } }).then(r => r.data)
}

export function addPlan(data) {
  return api.post('/plans/', data).then(r => r.data)
}

export function updatePlan(planId, data) {
  return api.put(`/plans/${planId}`, data).then(r => r.data)
}

export function deletePlan(planId, studentId) {
  return api.delete(`/plans/${planId}`, { params: { student_id: studentId } }).then(r => r.data)
}

// Video (Seedance)
export function generateVideo(resourceId, duration = 5) {
  return api.post('/video/generate', { resource_id: resourceId, duration }).then(r => r.data)
}

export function checkVideoStatus(resourceId) {
  return api.get(`/video/status/${resourceId}`).then(r => r.data)
}

// Blind Box
export function getDailyBlindBox(studentId) {
  return api.get('/blind-box/daily', { params: { student_id: studentId } }).then(r => r.data)
}

// Digital Human (iFlytek)
export function startDigitalHuman() {
  return api.post('/digital-human/start').then(r => r.data)
}

export function speakDigitalHuman(text) {
  return api.post('/digital-human/speak', { text }).then(r => r.data)
}

export function stopDigitalHuman() {
  return api.post('/digital-human/stop').then(r => r.data)
}

