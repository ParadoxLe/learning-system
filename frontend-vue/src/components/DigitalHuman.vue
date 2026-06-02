<template>
  <div class="dh-container">
    <div ref="playerContainer" class="dh-video-wrapper" />
    <div v-if="!ready" class="dh-loading">
      <div class="dh-loading-ring" />
      <span class="dh-loading-text">{{ error || '数字人连接中...' }}</span>
    </div>
    <div v-if="ready && statusText" class="dh-status">{{ statusText }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { RTCPlayer } from '../libs/rtcplayer/rtcplayer.esm.js'
import { startDigitalHuman, speakDigitalHuman, stopDigitalHuman } from '../api'

const playerContainer = ref(null)
const ready = ref(false)
const error = ref('')
const statusText = ref('')
let player = null
let statusTimer = null

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

onMounted(async () => {
  try {
    const data = await startDigitalHuman()
    if (!data.stream_url) {
      error.value = '未能获取视频流地址'
      return
    }

    const userId = generateId()
    const timeStr = Date.now().toString()

    player = new RTCPlayer()
    player.playerType = 12 // XRTC
    player.stream = {
      sid: data.sid || '',
      server: data.server || '',
      auth: data.stream_extend?.user_sign || '',
      appid: data.stream_extend?.appid || '',
      userId,
      roomId: data.room_id || '',
      timeStr,
    }
    player.videoSize = { width: 1080, height: 1920 }
    player.container = playerContainer.value

    player
      .on('play', () => { ready.value = true })
      .on('error', (e) => {
        error.value = '播放失败: ' + (e?.message || e)
        ready.value = false
      })
      .on('not-allowed', () => { player?.resume() })

    player.play()
  } catch (e) {
    error.value = e.response?.data?.detail || '数字人连接失败'
  }
})

onBeforeUnmount(() => {
  if (statusTimer) clearTimeout(statusTimer)
  if (player) {
    try { player.destroy() } catch (e) { /* ignore */ }
    player = null
  }
  try { stopDigitalHuman() } catch (e) { /* ignore */ }
})

function showStatus(text) {
  statusText.value = text
  if (statusTimer) clearTimeout(statusTimer)
  statusTimer = setTimeout(() => { statusText.value = '' }, 3000)
}

async function speak(text) {
  if (!ready.value) return
  try {
    await speakDigitalHuman(text)
  } catch (e) {
    showStatus('播报失败')
  }
}

defineExpose({ speak })
</script>

<style scoped>
.dh-container {
  width: 100%;
  height: 100%;
  border-radius: 16px;
  overflow: hidden;
  background: #fff;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dh-video-wrapper {
  width: 100%;
  height: 100%;
}

.dh-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  background: rgba(0, 0, 0, 0.5);
  pointer-events: none;
}

.dh-loading-ring {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.2);
  border-top-color: #C8A25C;
  border-radius: 50%;
  animation: dh-spin 0.8s linear infinite;
}

@keyframes dh-spin { to { transform: rotate(360deg); } }

.dh-loading-text {
  color: #ccc;
  font-size: 0.85rem;
}

.dh-status {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 0.78rem;
  padding: 4px 14px;
  border-radius: 12px;
  pointer-events: none;
  transition: opacity 0.3s;
}
</style>
