import { ref, reactive, computed, onUnmounted } from 'vue'

const WS_PROTO = location.protocol === 'https:' ? 'wss:' : 'ws:'
const WS_URL = `${WS_PROTO}//${location.host}/ws`
const UPLOAD_CHUNK_SIZE = 65536
const HISTORY_KEY = 'netspeed_history'

const logs = reactive([])
let logId = 0

function addLog(level, msg, data) {
  const entry = {
    id: ++logId,
    time: new Date().toLocaleTimeString(),
    level,
    msg,
    data: data ? JSON.stringify(data) : '',
  }
  logs.unshift(entry)
  if (logs.length > 200) logs.length = 200
  const prefix = `[${entry.time}][${level}]`
  if (data) console.log(prefix, msg, data)
  else console.log(prefix, msg)
}

function logInfo(msg, data) { addLog('INFO', msg, data) }
function logWarn(msg, data) { addLog('WARN', msg, data) }
function logError(msg, data) { addLog('ERROR', msg, data) }
function logDebug(msg, data) { addLog('DEBUG', msg, data) }

let uploadChunk = null
function getUploadChunk() {
  if (!uploadChunk) {
    uploadChunk = new Uint8Array(UPLOAD_CHUNK_SIZE)
    for (let i = 0; i < uploadChunk.length; i += 4096) {
      const view = new Uint8Array(4096)
      crypto.getRandomValues(view)
      uploadChunk.set(view, i)
    }
    logDebug('Upload chunk generated', { size: uploadChunk.length })
  }
  return uploadChunk
}

export function useSpeedTest() {
  const ws = ref(null)
  const connected = ref(false)
  const testing = ref(false)
  const currentMode = ref('download')
  const threadCount = ref(1)

  const threads = reactive([])

  const downSpeed = ref(0)
  const upSpeed = ref(0)
  const downTotal = ref(0)
  const upTotal = ref(0)
  const elapsed = ref(0)

  const lastResult = ref(null)
  const history = reactive(loadHistory())

  function loadHistory() {
    try {
      const data = localStorage.getItem(HISTORY_KEY)
      const h = data ? JSON.parse(data) : []
      logInfo('Loaded history from localStorage', { count: h.length })
      return h
    } catch {
      return []
    }
  }

  function saveHistory() {
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, 50)))
    } catch { /* ignore */ }
  }

  let reconnectTimer = null
  let pingTimer = null
  let uploadTimers = []
  let speedHistoryDown = []
  let speedHistoryUp = []
  let finishedThreads = 0
  let pendingResults = []

  function connect() {
    if (ws.value && (ws.value.readyState === WebSocket.OPEN || ws.value.readyState === WebSocket.CONNECTING)) return

    logInfo('Connecting to WebSocket', { url: WS_URL })
    const socket = new WebSocket(WS_URL)
    ws.value = socket

    socket.onopen = () => {
      connected.value = true
      logInfo('WebSocket connected', { url: WS_URL })
      startPing()
    }

    socket.onclose = (event) => {
      connected.value = false
      testing.value = false
      logWarn('WebSocket disconnected', { code: event.code, reason: event.reason })
      stopPing()
      scheduleReconnect()
    }

    socket.onerror = () => {
      socket.close()
    }

    socket.onmessage = (event) => {
      if (event.data instanceof Blob) return
      try {
        const msg = JSON.parse(event.data)
        if (msg.type === 'pong') return
        if (msg.type === 'error') logError('Server error', { text: msg.text })
      } catch { /* ignore */ }
    }
  }


  function startTest(mode, duration, threadsNum) {
    if (!connected.value) {
      logWarn('Cannot start test: not connected')
      return
    }
    if (testing.value) {
      logWarn('Cannot start test: test already in progress')
      return
    }

    const numThreads = threadsNum || 1
    logInfo('Starting test', { mode, duration, threads: numThreads })

    testing.value = true
    currentMode.value = mode
    threadCount.value = numThreads
    downSpeed.value = 0
    upSpeed.value = 0
    downTotal.value = 0
    upTotal.value = 0
    elapsed.value = 0
    speedHistoryDown = []
    speedHistoryUp = []
    finishedThreads = 0
    pendingResults = []

    threads.splice(0, threads.length)
    uploadTimers.forEach(t => { clearTimeout(t) })
    uploadTimers = []

    const aggregateDown = { speed: 0, total: 0 }
    const aggregateUp = { speed: 0, total: 0 }

    for (let i = 0; i < numThreads; i++) {
      const thread = createThread(i, mode, duration, aggregateDown, aggregateUp)
      threads.push(thread)
    }
  }

  function createThread(index, mode, duration, aggDown, aggUp) {
    const thread = {
      id: index,
      ws: null,
      connected: false,
      finished: false,
      downSpeed: 0,
      upSpeed: 0,
      downTotal: 0,
      upTotal: 0,
      lastResult: null,
    }
    threads[index] = thread

    const socket = new WebSocket(WS_URL)
    thread.ws = socket

    socket.onopen = () => {
      thread.connected = true
      logDebug(`Thread-${index} connected`)

      const payload = { type: 'start', mode, duration }
      socket.send(JSON.stringify(payload))
      logDebug(`Thread-${index} sent start`, payload)

      if (mode === 'upload' || mode === 'bidirectional') {
        startUploadOnThread(index, socket)
      }
    }

    socket.onclose = () => {
      thread.connected = false
      if (!thread.finished) {
        logWarn(`Thread-${index} closed unexpectedly`)
        markThreadFinished(index, aggDown, aggUp)
      }
    }

    socket.onerror = () => {
      logError(`Thread-${index} error`)
      socket.close()
    }

    socket.onmessage = (event) => {
      if (event.data instanceof Blob) return
      try {
        const msg = JSON.parse(event.data)
        logDebug(`Thread-${index} msg`, { type: msg.type, direction: msg.direction, speed: msg.speed_mbps })

        switch (msg.type) {
          case 'progress':
            elapsed.value = msg.elapsed || 0
            if (msg.direction === 'down' || msg.direction === 'download') {
              thread.downSpeed = msg.speed_mbps || 0
              thread.downTotal = msg.total_mb || 0
              speedHistoryDown.push({ time: msg.elapsed, speed: msg.speed_mbps || 0 })
            }
            if (msg.direction === 'up' || msg.direction === 'upload') {
              thread.upSpeed = msg.speed_mbps || 0
              thread.upTotal = msg.total_mb || 0
              speedHistoryUp.push({ time: msg.elapsed, speed: msg.speed_mbps || 0 })
            }
            aggregateThreads(aggDown, aggUp)
            break

          case 'result':
            logInfo(`Thread-${index} result`, msg)
            thread.lastResult = msg
            markThreadFinished(index, aggDown, aggUp)
            break
        }
      } catch { /* ignore */ }
    }

    return thread
  }

  function aggregateThreads(aggDown, aggUp) {
    let downSpd = 0, downTot = 0
    let upSpd = 0, upTot = 0
    for (const t of threads) {
      if (t.finished) continue
      downSpd += t.downSpeed
      downTot += t.downTotal
      upSpd += t.upSpeed
      upTot += t.upTotal
    }
    aggDown.speed = downSpd
    aggDown.total = downTot
    aggUp.speed = upSpd
    aggUp.total = upTot

    downSpeed.value = downSpd
    downTotal.value = downTot
    upSpeed.value = upSpd
    upTotal.value = upTot
  }

  function markThreadFinished(index, aggDown, aggUp) {
    if (threads[index] && threads[index].finished) return
    if (threads[index]) threads[index].finished = true
    finishedThreads++

    logInfo(`Thread-${index} finished (${finishedThreads}/${threadCount.value})`)

    if (threads[index] && threads[index].lastResult) {
      pendingResults.push(threads[index].lastResult)
    }

    if (finishedThreads >= threadCount.value) {
      testing.value = false
      uploadTimers.forEach(t => { clearTimeout(t) })
      uploadTimers = []

      aggregateThreads(aggDown, aggUp)

      const result = mergeResults(pendingResults)
      if (result) {
        lastResult.value = result
        history.unshift(result)
        if (history.length > 50) history.pop()
        saveHistory()
        logInfo('Aggregated result', result)
      }

      setTimeout(() => {
        threads.forEach(t => {
          if (t.ws) {
            try { t.ws.close() } catch { /* ignore */ }
          }
        })
        threads.splice(0, threads.length)
      }, 100)
    }
  }

  function mergeResults(results) {
    if (!results.length) return null
    const first = results[0]
    const isDown = first.direction === 'down'
    let totalAvg = 0, totalMax = 0, totalMin = Infinity, totalBytes = 0, totalDuration = 0

    for (const r of results) {
      totalAvg += r.avg_mbps || 0
      totalMax = Math.max(totalMax, r.max_mbps || 0)
      totalMin = Math.min(totalMin, r.min_mbps || Infinity)
      totalBytes += r.total_bytes || 0
      totalDuration = Math.max(totalDuration, r.duration_act || 0)
    }

    if (totalMin === Infinity) totalMin = 0

    return {
      direction: isDown ? 'down' : 'up',
      avgMbps: totalAvg,
      maxMbps: totalMax,
      minMbps: totalMin,
      totalBytes,
      duration: totalDuration,
      time: new Date().toLocaleString(),
    }
  }

  function startUploadOnThread(index, socket) {
    const chunk = getUploadChunk()
    let sentCount = 0
    function sendChunk() {
      if (!testing.value || !threads[index] || threads[index].finished) return
      if (socket.readyState !== WebSocket.OPEN) return
      if (socket.bufferedAmount > UPLOAD_CHUNK_SIZE * 10) {
        uploadTimers[index] = setTimeout(sendChunk, 50)
        return
      }
      socket.send(chunk.buffer)
      sentCount++
      if (sentCount % 100 === 0) {
        logDebug(`Upload thread-${index}`, { chunksSent: sentCount })
      }
      uploadTimers[index] = setTimeout(sendChunk, 0)
    }
    sendChunk()
  }

  function stopTest() {
    if (!connected.value) return
    logInfo('Stopping test by user request')
    testing.value = false
    uploadTimers.forEach(t => { clearTimeout(t) })
    uploadTimers = []
    threads.forEach(t => {
      if (t.ws && t.ws.readyState === WebSocket.OPEN) {
        t.ws.send(JSON.stringify({ type: 'stop' }))
      }
    })
    setTimeout(() => {
      threads.forEach(t => {
        if (t.ws) {
          try { t.ws.close() } catch { /* ignore */ }
        }
      })
      threads.splice(0, threads.length)
    }, 100)
  }

  function sendMsg(obj) {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(obj))
    }
  }

  function startPing() {
    pingTimer = setInterval(() => {
      sendMsg({ type: 'ping', timestamp: Date.now() })
    }, 5000)
  }

  function stopPing() {
    if (pingTimer) {
      clearInterval(pingTimer)
      pingTimer = null
    }
  }

  function scheduleReconnect() {
    if (reconnectTimer) return
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null
      connect()
    }, 3000)
  }

  onUnmounted(() => {
    stopPing()
    uploadTimers.forEach(t => { clearTimeout(t) })
    if (reconnectTimer) clearTimeout(reconnectTimer)
    if (ws.value) ws.value.close()
    threads.forEach(t => {
      if (t.ws) try { t.ws.close() } catch { /* ignore */ }
    })
  })

  return {
    logs,
    connected,
    testing,
    currentMode,
    threadCount,
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
  }
}
