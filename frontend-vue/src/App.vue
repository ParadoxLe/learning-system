<template>
  <AppLayout v-if="auth.isLoggedIn && !auth.needsOnboarding" />
  <router-view v-else />
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useAuthStore } from './stores/auth'
import { useStudentStore } from './stores/student'
import AppLayout from './components/AppLayout.vue'

const auth = useAuthStore()
const store = useStudentStore()

onMounted(() => {
  if (auth.studentId) {
    store.syncWithUser(auth.studentId)
  }
})

// Keep student store in sync with auth
watch(() => auth.studentId, (id) => {
  if (id) store.syncWithUser(id)
})
</script>
