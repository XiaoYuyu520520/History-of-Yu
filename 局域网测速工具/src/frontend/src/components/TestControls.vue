<template>
  <div class="controls">
    <div class="status-bar">
      <span class="status-dot" :class="{ connected: connected }"></span>
      {{ connected ? '已连接' : '正在连接...' }}
    </div>

    <div class="mode-selector">
      <button
        v-for="opt in modeOptions"
        :key="opt.value"
        :class="{ active: mode === opt.value, disabled: testing }"
        @click="selectMode(opt.value)"
      >
        {{ opt.label }}
      </button>
    </div>

    <div class="duration-selector">
      <span class="label">测速时长:</span>
      <button
        v-for="d in durationOptions"
        :key="d"
        :class="{ active: duration === d, disabled: testing }"
        @click="selectDuration(d)"
      >
        {{ d }}s
      </button>
    </div>

    <div class="thread-selector">
      <span class="label">线程数:</span>
      <button
        v-for="t in threadOptions"
        :key="t"
        :class="{ active: threads === t, disabled: testing }"
        @click="selectThreads(t)"
      >
        {{ t }}
      </button>
    </div>

    <button
      class="action-btn"
      :class="{ testing: testing }"
      @click="handleClick"
      :disabled="!connected"
    >
      {{ testing ? '⏹ 停止' : '▶ 开始测速' }}
    </button>

    <div class="elapsed" v-if="testing">
      已用时: {{ elapsed.toFixed(1) }}s
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['start', 'stop'])
const props = defineProps({
  connected: { type: Boolean, default: false },
  testing: { type: Boolean, default: false },
  elapsed: { type: Number, default: 0 },
})

const mode = ref('download')
const duration = ref(10)
const threads = ref(1)

const modeOptions = [
  { value: 'download', label: '下载测速' },
  { value: 'upload', label: '上传测速' },
  { value: 'bidirectional', label: '双向测速' },
]

const durationOptions = [5, 10, 30]
const threadOptions = [1, 2, 4, 8]

function selectMode(val) {
  if (props.testing) return
  mode.value = val
}

function selectDuration(val) {
  if (props.testing) return
  duration.value = val
}

function selectThreads(val) {
  if (props.testing) return
  threads.value = val
}

function handleClick() {
  if (props.testing) {
    emit('stop')
  } else {
    emit('start', { mode: mode.value, duration: duration.value, threads: threads.value })
  }
}
</script>

<style scoped>
.controls {
  text-align: center;
}
.status-bar {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #667788;
  font-size: 14px;
  margin-bottom: 24px;
}
.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ff4444;
  transition: background 0.3s;
}
.status-dot.connected {
  background: #00d4aa;
  box-shadow: 0 0 8px rgba(0, 212, 170, 0.5);
}
.mode-selector {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-bottom: 16px;
}
.mode-selector button,
.duration-selector button,
.thread-selector button {
  background: #1a1a2e;
  color: #8899aa;
  border: 1px solid #2a2a4e;
  padding: 10px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}
.mode-selector button:hover:not(.disabled),
.duration-selector button:hover:not(.disabled),
.thread-selector button:hover:not(.disabled) {
  border-color: #00d4aa;
  color: #e0e0e0;
}
.mode-selector button.active,
.duration-selector button.active,
.thread-selector button.active {
  background: #00d4aa;
  color: #0a0a1a;
  border-color: #00d4aa;
  font-weight: 600;
}
.mode-selector button.disabled,
.duration-selector button.disabled,
.thread-selector button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.duration-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  margin-bottom: 28px;
}
.duration-selector .label,
.thread-selector .label {
  color: #667788;
  font-size: 14px;
  margin-right: 8px;
}

.thread-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  margin-bottom: 28px;
}
.thread-selector .label {
  color: #667788;
  font-size: 14px;
  margin-right: 8px;
}
.action-btn {
  background: linear-gradient(135deg, #00d4aa, #00aaff);
  color: #0a0a1a;
  border: none;
  padding: 14px 48px;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 20px rgba(0, 212, 170, 0.3);
}
.action-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(0, 212, 170, 0.4);
}
.action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}
.action-btn.testing {
  background: linear-gradient(135deg, #ff6b6b, #ff4444);
  box-shadow: 0 4px 20px rgba(255, 68, 68, 0.3);
}
.elapsed {
  color: #667788;
  font-size: 14px;
  margin-top: 16px;
}
</style>
