<template>
  <div class="gauge-container">
    <div class="gauge-card" v-if="showDown">
      <div class="gauge-label">下载速度</div>
      <div class="gauge-value" :class="{ active: isActive }">
        {{ formatSpeed(speed) }}
        <span class="gauge-unit">Mbps</span>
      </div>
      <div class="gauge-bar">
        <div class="gauge-fill down" :style="{ width: barPercent + '%' }"></div>
      </div>
      <div class="gauge-sub">已传输: {{ formatSize(total) }}</div>
    </div>
    <div class="gauge-card" v-if="showUp">
      <div class="gauge-label">上传速度</div>
      <div class="gauge-value" :class="{ active: isActive }">
        {{ formatSpeed(upSpeed) }}
        <span class="gauge-unit">Mbps</span>
      </div>
      <div class="gauge-bar">
        <div class="gauge-fill up" :style="{ width: upBarPercent + '%' }"></div>
      </div>
      <div class="gauge-sub">已传输: {{ formatSize(upTotal) }}</div>
    </div>
    <div class="gauge-card" v-if="latency !== null">
      <div class="gauge-label">延迟</div>
      <div class="gauge-value small" :class="{ good: latency < 50, ok: latency >= 50 && latency < 150 }">
        {{ latency }} <span class="gauge-unit">ms</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  speed: { type: Number, default: 0 },
  upSpeed: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  upTotal: { type: Number, default: 0 },
  isActive: { type: Boolean, default: false },
  showDown: { type: Boolean, default: true },
  showUp: { type: Boolean, default: false },
  latency: { type: Number, default: null },
})

const barPercent = computed(() => {
  return Math.min((props.speed / 1000) * 100, 100)
})

const upBarPercent = computed(() => {
  return Math.min((props.upSpeed / 1000) * 100, 100)
})

function formatSpeed(mbps) {
  if (mbps >= 1000) return (mbps / 1000).toFixed(2)
  if (mbps >= 1) return mbps.toFixed(2)
  if (mbps > 0) return mbps.toFixed(2)
  return '0.00'
}

function formatSize(mb) {
  if (mb >= 1024) return (mb / 1024).toFixed(2) + ' GB'
  if (mb >= 1) return mb.toFixed(2) + ' MB'
  return (mb * 1024).toFixed(0) + ' KB'
}
</script>

<style scoped>
.gauge-container {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}
.gauge-card {
  background: #1a1a2e;
  border-radius: 16px;
  padding: 30px 40px;
  min-width: 280px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
.gauge-label {
  color: #8899aa;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 12px;
}
.gauge-value {
  font-size: 48px;
  font-weight: 700;
  color: #e0e0e0;
  transition: color 0.3s;
}
.gauge-value.active {
  color: #00d4aa;
}
.gauge-value.small {
  font-size: 36px;
}
.gauge-value.good {
  color: #00d4aa;
}
.gauge-value.ok {
  color: #f0a500;
}
.gauge-unit {
  font-size: 18px;
  font-weight: 400;
  color: #667788;
  margin-left: 4px;
}
.gauge-bar {
  height: 6px;
  background: #2a2a4e;
  border-radius: 3px;
  margin: 16px 0;
  overflow: hidden;
}
.gauge-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}
.gauge-fill.down {
  background: linear-gradient(90deg, #00d4aa, #00aaff);
}
.gauge-fill.up {
  background: linear-gradient(90deg, #f0a500, #ff6b6b);
}
.gauge-sub {
  color: #667788;
  font-size: 13px;
}
</style>
