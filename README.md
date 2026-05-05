# Random Coding Ideas

日常随机编码创意与小工具合集，记录各种实用脚本、工具和创意原型。

## 项目一览

### 1. 📊 Linux开发板性能监视器

基于 Python + Flask + Vue 3 + ECharts 的轻量级实时硬件状态监视器。专为 **NVIDIA Jetson**、**树莓派** 等 Linux 开发板设计，也支持桌面 Linux。

- **实时 SSE 推送** — 秒级延迟，告别轮询
- **CPU / 内存 / 磁盘 / GPU** — 全维度监控
- **暗色玻璃态 UI** — 美观的现代化仪表盘
- **Ping 监测** — 内置网络延迟实时追踪

```bash
cd "Linux开发板性能监视器"
bash start.sh
# 访问 http://localhost:8888
```

---

### 2. 🌐 局域网测速工具 (NetSpeed)

Go + Vue 3 构建的自托管网页版网络测速工具，**单文件部署**，跨平台支持。

- **三种模式** — 下载测速 / 上传测速 / 双向测速
- **多线程** — 支持 1/2/4/8 线程并发
- **实时仪表盘** — 200ms 窗口瞬时速度显示
- **开箱即用** — 提供 Windows / Linux / ARM64 预编译二进制

```bash
cd 局域网测速工具
./bin/netspeed
# 访问 http://localhost:7777
```

---

### 3. 🛠 小工具 v1.0

基于 Python Tkinter 的桌面小工具集合，已打包为 Windows exe，可直接运行。

| 工具 | 说明 |
|------|------|
| **简易画板** | Tkinter 绘图工具，支持颜色/粗细调节 |
| **网址快捷方式生成器** | 生成 .bat 快捷方式快速打开网址 |
| **获取系统状态** | 读取 CPU / GPU / 内存 / 磁盘信息 |
| **设备信息 CLI** | 命令行模式，支持 JSON 格式输出 |

---

### 4. 📁 局域网文件共享服务 (Lan Share Server)

基于 FastAPI 的轻量级局域网文件共享服务器，支持 PyInstaller 打包为单文件 exe。

- **浏览 / 下载** — Web 界面浏览并下载共享目录文件
- **内置前端** — 前后端一体，无需额外配置
- **可打包分发** — 支持打包为独立 exe，双击即可运行

```bash
cd "server/code/lan-share-server/backend"
pip install -r requirements.txt
python server.py
# 访问 http://localhost:8005
```

---

## 项目结构

```
History-of-Yu-main/
├── Linux开发板性能监视器/    # Flask 硬件监控
├── 局域网测速工具/           # Go 网络测速 (含预编译二进制)
├── 小工具v1.0/              # Python 桌面小工具集合
├── server/                  # 局域网文件共享服务
├── README.md
└── LICENSE
```

各子项目目录内均有独立的 README 文档，包含详细的使用说明和构建方法。

## 许可证

本仓库内容采用 [Apache License 2.0](LICENSE) 许可，欢迎参考和修改。
