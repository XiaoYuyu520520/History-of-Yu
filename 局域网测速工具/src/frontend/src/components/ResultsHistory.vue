<template>
  <div class="history" v-if="results.length > 0">
    <h3>测速历史</h3>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>时间</th>
            <th>方向</th>
            <th>平均速度</th>
            <th>最大速度</th>
            <th>最小速度</th>
            <th>传输量</th>
            <th>时长</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(r, i) in results" :key="i">
            <td>{{ r.time }}</td>
            <td>
              <span class="dir-tag" :class="r.direction">
                {{ r.direction === 'down' ? '↓ 下载' : r.direction === 'up' ? '↑ 上传' : '⇄ 双向' }}
              </span>
            </td>
            <td class="num">{{ fmtSpeed(r.avgMbps) }}</td>
            <td class="num">{{ fmtSpeed(r.maxMbps) }}</td>
            <td class="num">{{ fmtSpeed(r.minMbps) }}</td>
            <td class="num">{{ fmtBytes(r.totalBytes) }}</td>
            <td class="num">{{ r.duration.toFixed(1) }}s</td>
          </tr>
        </tbody>
      </table>
    </div>
    <button class="clear-btn" @click="$emit('clear')">清空历史</button>
  </div>
</template>

<script setup>
defineProps({
  results: { type: Array, default: () => [] },
})
defineEmits(['clear'])

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

<style scoped>
.history {
  margin-top: 40px;
}
h3 {
  color: #8899aa;
  font-size: 16px;
  margin-bottom: 16px;
  text-align: center;
}
.table-wrap {
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
th {
  color: #667788;
  padding: 10px 14px;
  text-align: right;
  border-bottom: 1px solid #2a2a4e;
  font-weight: 500;
}
th:first-child {
  text-align: left;
}
td {
  color: #c0c0d0;
  padding: 10px 14px;
  text-align: right;
  border-bottom: 1px solid #1a1a2e;
}
td:first-child {
  text-align: left;
}
td.num {
  font-family: 'SF Mono', 'Consolas', monospace;
  font-size: 13px;
}
.dir-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}
.dir-tag.down {
  background: rgba(0, 212, 170, 0.15);
  color: #00d4aa;
}
.dir-tag.up {
  background: rgba(240, 165, 0, 0.15);
  color: #f0a500;
}
.dir-tag.bidirectional {
  background: rgba(0, 170, 255, 0.15);
  color: #00aaff;
}
.clear-btn {
  display: block;
  margin: 16px auto 0;
  background: transparent;
  color: #667788;
  border: 1px solid #2a2a4e;
  padding: 8px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}
.clear-btn:hover {
  border-color: #ff4444;
  color: #ff4444;
}
</style>
