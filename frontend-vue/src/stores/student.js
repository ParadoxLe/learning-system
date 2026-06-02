import { defineStore } from 'pinia'
import { getStudents, createStudent } from '../api'
import { getProfile } from '../api'

export const useStudentStore = defineStore('student', {
  state: () => ({
    students: [],
    currentStudentId: null,
    profile: null,
    profileVersion: 0,
  }),
  getters: {
    currentStudent: (state) => state.students.find(s => s.id === state.currentStudentId),
    hasProfile: (state) => state.profile && typeof state.profile === 'object' && Object.keys(state.profile).length > 2,
  },
  actions: {
    syncWithUser(studentId) {
      this.currentStudentId = studentId
      if (studentId) {
        this.loadProfile()
      }
    },
    async loadStudents() {
      try {
        this.students = await getStudents()
        if (this.students.length > 0 && !this.currentStudentId) {
          this.currentStudentId = this.students[0].id
          await this.loadProfile()
        }
      } catch (e) {
        console.error('Failed to load students', e)
      }
    },
    async addStudent(name, major, grade) {
      const s = await createStudent({ name, major, grade })
      this.students.push(s)
      this.currentStudentId = s.id
      this.profile = null
      return s
    },
    async loadProfile() {
      if (!this.currentStudentId) return
      try {
        const data = await getProfile(this.currentStudentId)
        this.profile = data?.profile ?? null
        this.profileVersion = data?.version ?? 0
      } catch (e) {
        this.profile = null
        this.profileVersion = 0
      }
    },
    clearProfile() {
      this.profile = null
    },
  },
})
