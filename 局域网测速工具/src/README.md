# NetSpeed - 网络速度测试工具

NetSpeed 是一个自托管的网页版网络测速工具，使用 Go + Vue3 构建。支持下载测速、上传测速、双向测速和多线程传输，所有数据通过 WebSocket 实时传输，结果页面实时显示。

## 特性

- **三种测速模式**：下载测速、上传测速、双向同时测速
- **多线程传输**：支持 1/2/4/8 线程并行传输，更准确压榨带宽
- **实时显示**：200ms 窗口实时速度仪表盘
- **测速时长可选**：5 秒 / 10 秒 / 30 秒
- **历史记录**：保存最近 50 条测速结果（页面刷新不丢失）
- **单文件部署**：前后端打包为一个可执行文件，无需任何依赖
- **跨平台**：支持 Windows / Linux / ARM64

## 快速开始

### 下载预编译二进制

从 `build/` 目录获取对应平台的可执行文件：

| 文件 | 平台 |
|------|------|
| `netspeed-windows-amd64.exe` | Windows x86_64 |
| `netspeed-linux-amd64` | Linux x86_64 |
| `netspeed-linux-arm64` | Linux ARM64（树莓派、Jetson 等） |
| `netspeed` | 当前编译平台 |

### 运行

**方法一：双击运行（Windows）**

双击 `netspeed-windows-amd64.exe`，打开浏览器访问 `http://localhost:7777`

**方法二：命令行运行**

```bash
# Linux / macOS
./netspeed

# Windows (cmd)
netspeed-windows-amd64.exe

# Windows (PowerShell)
.\netspeed-windows-amd64.exe
```

**方法三：Python 启动器**

```bash
python3 start.py
```

启动器会自动检测平台、选择合适的二进制文件，并显示局域网访问地址。

**方法四：自定义端口**

```bash
# Linux
PORT=8888 ./netspeed

# Windows (cmd)
set PORT=8888 && netspeed-windows-amd64.exe

# Windows (PowerShell)
$env:PORT=8888; .\netspeed-windows-amd64.exe
```

### 访问

打开浏览器访问 `http://localhost:7777`（或自定义端口）。

如果需要局域网内其他设备访问，使用 `http://<本机IP>:7777`。

> **Windows 防火墙**：首次运行可能会弹出防火墙提示，点击「允许访问」即可。

## 使用说明

1. 打开页面后，状态指示灯显示「已连接」表示 WebSocket 连接成功
2. 选择测速模式：下载测速 / 上传测速 / 双向测速
3. 选择线程数（默认为 1）
4. 选择测速时长（5/10/30 秒）
5. 点击「开始测速」，等待测试完成
6. 查看实时速度和最终结果

### 调试模式

点击页面底部的「显示调试」按钮，可以查看前端实时日志，包括 WebSocket 连接状态、收发消息、上传数据块计数等，方便排查问题。

## 从源码构建

### 前置要求

- Go 1.21+
- Node.js 18+ (构建前端时需要)

### 一键构建

```bash
bash build.sh
```

构建产物输出到 `build/` 目录。

### 分步构建

**1. 构建前端**

```bash
cd frontend
npm install
npm run build
```

**2. 构建 Go 后端**

```bash
# 当前平台
go build -ldflags="-s -w" -o build/netspeed .

# 交叉编译
GOOS=linux GOARCH=arm64 go build -ldflags="-s -w" -o build/netspeed-linux-arm64 .
GOOS=windows GOARCH=amd64 go build -ldflags="-s -w" -o build/netspeed-windows-amd64.exe .
GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o build/netspeed-linux-amd64 .
```

## 项目结构

```
netspeed/
├── main.go                    # Go 入口，嵌入前端静态文件
├── build.sh                   # 一键构建脚本
├── start.py                   # Python 启动器
├── go.mod / go.sum            # Go 模块依赖
├── backend/
│   ├── model/
│   │   └── types.go           # 消息类型与数据结构
│   ├── handler/
│   │   ├── ws.go              # WebSocket 连接管理与消息路由
│   │   └── speedtest.go       # 测速引擎（下载/上传/双向）
│   └── loglib/
│       └── logger.go          # 日志工具（同时输出到文件和控制台）
├── frontend/
│   ├── index.html             # 入口 HTML
│   ├── vite.config.js         # Vite 配置
│   ├── package.json           # Node.js 依赖
│   ├── dist/                  # 构建后的前端文件（嵌入 Go 二进制）
│   └── src/
│       ├── main.js            # Vue 应用入口
│       ├── App.vue            # 根组件
│       ├── composables/
│       │   └── useSpeedTest.js    # WebSocket 连接、多线程管理、速度聚合
│       └── components/
│           ├── TestControls.vue   # 模式/时长/线程数选择
│           ├── SpeedGauge.vue     # 实时速度仪表盘
│           └── ResultsHistory.vue # 历史记录表格
└── build/                     # 编译产物目录
```

## 技术架构

```
┌─────────────┐     WebSocket      ┌──────────────┐
│  浏览器     │ ◄────────────────► │  Go 服务端   │
│  (Vue 3)   │    /ws 端口 7777   │  (Gorilla)   │
│            │                    │              │
│ 多线程连接   │  ── text (JSON) ──►  │  解析消息     │
│ (N条WS连接) │  ◄── text (JSON) ──  │  执行测速     │
│            │  ◄── binary data ──   │  返回进度/结果 │
│ 实时聚合显示 │  ── binary data ──►  │  (上传模式)   │
└─────────────┘                    └──────────────┘
```

- **传输协议**：所有测速数据通过 WebSocket 传输，文本消息传递 JSON 控制/进度/结果，二进制消息传递测速载荷
- **多线程**：每个线程独立 WebSocket 连接，前端实时聚合各线程速度（求和后显示）
- **速度计算**：后端每 200ms 统计窗口内传输字节数，计算瞬时速度上报前端

## 测速算法

- **下载测速**：服务端持续发送 64KB 数据块，客户端接收后丢弃，仅统计传输速率
- **上传测速**：客户端生成 64KB 随机数据块持续发送，服务端接收计数
- **双向测速**：上下行同时进行，各自独立统计
- **速度窗口**：每 200ms 计算一次瞬时速度（deltaBytes / deltaTime），用于实时显示和最大/最小值统计
- **125000 换算**：公式 `Mbps = bytes / seconds / 125000`（因为 1 Mbps = 1,000,000 bit/s = 125,000 byte/s）

## 日志

服务端启动后会在 `logs/` 目录生成日志文件，命名格式 `netspeed_YYYYMMDD_HHMMSS.log`，同时输出到标准输出。

日志内容包括：
- 每条 WebSocket 连接建立/断开
- 每条消息的接收与解析
- 测速开始/结束及详细参数
- 每 200ms 进度报告
- 最终结果统计

## 常见问题

**Q: 测速结果不准确？**
A: 尝试增加线程数（2/4/8），或使用更长的测速时长（30 秒）。局域网测速建议使用 10 秒以上。

**Q: 页面显示「正在连接...」？**
A: 检查服务端是否正在运行，以及端口是否正确（默认 7777）。

**Q: Windows 防火墙阻止？**
A: 点击「允许访问」，或手动在 Windows 防火墙中添加入站规则开放对应端口。

## License

MIT
