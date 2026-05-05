<template>
  <div class="app">
    <header class="header">
      <h1>NetSpeed</h1>
      <p class="subtitle">网络速度测试工具</p>
    </header>

    <main class="main">
      <TestControls
        :connected="connected"
        :testing="testing"
        :elapsed="elapsed"
        @start="handleStart"
        @stop="handleStop"
      />

      <SpeedGauge
        :speed="downSpeed"
        :up-speed="upSpeed"
        :total="downTotal"
        :up-total="upTotal"
        :is-active="testing"
        :show-down="currentMode !== 'upload'"
        :show-up="currentMode === 'upload' || currentMode === 'bidirectional'"
      />

      <div class="result-panel" v-if="lastResult">
        <div class="result-item">
          <span class="result-label">测试结果</span>
          <span class="result-val">{{ lastResult.direction === 'down' ? '下载' : lastResult.direction === 'up' ? '上传' : '双向' }}</span>
        </div>
        <div class="result-item">
          <span class="result-label">平均速度</span>
          <span class="result-val highlight">{{ fmtSpeed(lastResult.avgMbps) }}</span>
        </div>
        <div class="result-item" v-if="lastResult.maxMbps">
          <span class="result-label">最大速度</span>
          <span class="result-val">{{ fmtSpeed(lastResult.maxMbps) }}</span>
        </div>
        <div class="result-item" v-if="lastResult.minMbps">
          <span class="result-label">最小速度</span>
          <span class="result-val">{{ fmtSpeed(lastResult.minMbps) }}</span>
        </div>
        <div class="result-item">
          <span class="result-label">传输数据</span>
          <span class="result-val">{{ fmtBytes(lastResult.totalBytes) }}</span>
        </div>
        <div class="result-item">
          <span class="result-label">测试时长</span>
          <span class="result-val">{{ lastResult.duration.toFixed(1) }}s</span>
        </div>
      </div>

      <ResultsHistory
        :results="history"
        @clear="clearHistory"
      />

      <div class="debug-section">
        <button class="debug-toggle" @click="showDebug = !showDebug">
          {{ showDebug ? '隐藏调试' : '显示调试' }} ({{ logs.length }})
        </button>
        <div class="debug-panel" v-if="showDebug">
          <div class="debug-header">
            <span>调试日志</span>
            <button class="debug-clear" @click="logs.splice(0, logs.length)">清空</button>
          </div>
          <div class="debug-entries" ref="debugContainer">
            <div
              v-for="entry in logs"
              :key="entry.id"
              class="debug-entry"
              :class="'level-' + entry.level.toLowerCase()"
            >
              <span class="debug-time">{{ entry.time }}</span>
              <span class="debug-level">[{{ entry.level }}]</span>
              <span class="debug-msg">{{ entry.msg }}</span>
              <span class="debug-data" v-if="entry.data">{{ entry.data }}</span>
            </div>
          </div>
        </div>
      </div>
    </main>

    <footer class="footer">
      NetSpeed v1.0 | Go + Vue3
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TestControls from './components/TestControls.vue'
import SpeedGauge from './components/SpeedGauge.vue'
import ResultsHistory from './components/ResultsHistory.vue'
import { useSpeedTest } from './composables/useSpeedTest.js'

const {
  logs,
  connected,
  testing,
  currentMode,
  downSpeed,
  upSpeed,
  downTotal,
  upTotal,
  elapsed,
  lastResult,
  history,
  connect,
  startTest,
  stopTest,
} = useSpeedTest()

const showDebug = ref(false)

onMounted(() => {
  connect()
})

function handleStart({ mode, duration, threads }) {
  startTest(mode, duration, threads)
}

function handleStop() {
  stopTest()
}

function clearHistory() {
  history.splice(0, history.length)
  localStorage.removeItem('netspeed_history')
}

function fmtSpeed(mbps) {
  if (mbps >= 1000) return (mbps / 1000).toFixed(2) + ' Gbps'
  return mbps.toFixed(2) + ' Mbps'
}

function fmtBytes(bytes) {
  if (bytes >= 1073741824) return (bytes / 1073741824).toFixed(2) + ' GB'
  if (bytes >= 1048576) return (bytes / 1048576).toFixed(2) + ' MB'
  if (bytes >= 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return bytes + ' B'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  background: #0a0a1a;
  color: #e0e0e0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans SC', sans-serif;
  min-height: 100vh;
}
.app {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.header {
  text-align: center;
  margin-bottom: 40px;
}
.header h1 {
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4aa, #00aaff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.subtitle {
  color: #667788;
  font-size: 14px;
  margin-top: 8px;
}
.main {
  flex: 1;
}
.result-panel {
  background: #1a1a2e;
  border-radius: 12px;
  padding: 20px 28px;
  margin-top: 24px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.result-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.result-label {
  color: #667788;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.result-val {
  font-size: 18px;
  font-weight: 600;
}
.result-val.highlight {
  color: #00d4aa;
  font-size: 24px;
}
.footer {
  text-align: center;
  color: #444466;
  font-size: 12px;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #1a1a2e;
}
.debug-section {
  margin-top: 24px;
}
.debug-toggle {
  background: #1a1a2e;
  color: #8899aa;
  border: 1px solid #2a2a4e;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  width: 100%;
}
.debug-toggle:hover {
  border-color: #00d4aa;
  color: #e0e0e0;
}
.debug-panel {
  background: #111122;
  border: 1px solid #2a2a4e;
  border-radius: 8px;
  margin-top: 8px;
  max-height: 400px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.debug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #1a1a2e;
  font-size: 12px;
  color: #667788;
  border-bottom: 1px solid #2a2a4e;
}
.debug-clear {
  background: none;
  border: 1px solid #2a2a4e;
  color: #667788;
  padding: 2px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
}
.debug-clear:hover {
  border-color: #ff4444;
  color: #ff4444;
}
.debug-entries {
  overflow-y: auto;
  padding: 4px 0;
  font-family: 'Courier New', monospace;
  font-size: 11px;
  line-height: 1.5;
}
.debug-entry {
  padding: 2px 12px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.debug-entry:hover {
  background: #1a1a2e;
}
.debug-time {
  color: #444466;
  flex-shrink: 0;
}
.debug-level {
  flex-shrink: 0;
  font-weight: 600;
  min-width: 45px;
}
.debug-msg {
  color: #c0c0d0;
}
.debug-data {
  color: #667788;
  font-size: 10px;
}
.level-info .debug-level { color: #00d4aa; }
.level-warn .debug-level { color: #f0a500; }
.level-error .debug-level { color: #ff4444; }
.level-debug .debug-level { color: #667788; }
</style>
