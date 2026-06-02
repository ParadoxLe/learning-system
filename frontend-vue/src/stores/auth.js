import { defineStore } from 'pinia'
import { login as apiLogin, register as apiRegister, me as apiMe } from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    studentId: null,
    hasProfile: false,
  }),
  getters: {
    isLoggedIn: (state) => !!state.token && !!state.user,
    needsOnboarding: (state) => state.isLoggedIn && !state.hasProfile,
  },
  actions: {
    async login(username, password, captchaId, captchaCode) {
      const data = await apiLogin(username, password, captchaId, captchaCode)
      this.token = data.token
      this.user = { id: data.user_id, username: data.username, avatar: '' }
      this.studentId = data.student_id
      localStorage.setItem('token', data.token)
      await this.checkProfile()
    },
    async register(username, password, captchaId, captchaCode) {
      const data = await apiRegister(username, password, captchaId, captchaCode)
      this.token = data.token
      this.user = { id: data.user_id, username: data.username }
      this.studentId = data.student_id
      localStorage.setItem('token', data.token)
      this.hasProfile = false
    },
    async checkProfile() {
      try {
        const data = await apiMe()
        this.hasProfile = data.has_profile
        this.studentId = data.student_id
      } catch {
        this.hasProfile = false
      }
    },
    logout() {
      this.token = null
      this.user = null
      this.studentId = null
      this.hasProfile = false
      localStorage.removeItem('token')
    },
    async fetchUser() {
      try {
        const data = await apiMe()
        this.user = { id: data.id, username: data.username, avatar: data.avatar || '' }
        this.studentId = data.student_id
        this.hasProfile = data.has_profile
      } catch {
        this.logout()
      }
    },
  },
})
