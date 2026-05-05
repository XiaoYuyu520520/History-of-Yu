# RDK 小车开发常用工具

> 针对 RDK（Robot Development Kit）小车开发场景收集整理的常用工具集，涵盖性能基准测试、ROS2 调试、USB/网络设备扫描、磁盘监控、雷达调试等实用工具。

---

## 目录

- [CPU 基准测试](#cpu-基准测试)
- [磁盘工具](#磁盘工具)
- [ROS2 调试](#ros2-调试)
- [USB 扫描](#usb-扫描)
- [网络扫描](#网络扫描)
- [雷达调试](#雷达调试)
- [实用工具](#实用工具)

---

## CPU 基准测试

评估 RDK 小车 CPU 性能的工具。

### `cpu-测试/cpu-benchmark/`（C++）

高性能 CPU 基准测试二进制程序。测试内容包括：
- 整数运算（加法、乘法、除法、取模）
- 单精度 / 双精度浮点运算（加法、乘法、FMA）
- 核间延迟测试
- 生成热力图 PNG

```bash
cd "cpu-测试/cpu-benchmark"
./cpu-benchmark
```

### `CPU和磁盘基准测试工具/CPU 单核基准测试脚本.py`（Python）

Python 实现的单核 CPU 基准测试，通过质数查找（整数）和三角函数 / 平方根运算（浮点）评估性能，输出类 Geekbench 评分。

```bash
python "CPU和磁盘基准测试工具/CPU 单核基准测试脚本.py"
```

---

## 磁盘工具

### `CPU和磁盘基准测试工具/磁盘 IO 速度测试 Python 脚本.py`

磁盘顺序读写吞吐量测试。创建临时文件，依次执行顺序写入 → 缓存清理（需 sudo）→ 顺序读取，以 B/KB/MB/GB 每秒报告结果。

```bash
sudo python "CPU和磁盘基准测试工具/磁盘 IO 速度测试 Python 脚本.py"
```

### `磁盘工具/disk_monitor.py`

基于 `iostat -x` 的实时磁盘 I/O 监控器。持续显示指定挂载点的读取速度（MB/s）、写入速度（MB/s）和磁盘繁忙率（`%util`）。支持 Ctrl+C 退出。

```bash
python 磁盘工具/disk_monitor.py
```

---

## ROS2 调试

### `ros2_helper/`

完整的 ROS2 话题扫描与诊断工具，支持交互式选择、QoS 解析、消息预览和结果导出。

**功能特性：**
- 扫描当前所有活跃 ROS2 话题
- 解析 QoS 配置（可靠性、持久性、历史记录、深度等）
- 捕获并解析消息样本（图像、IMU、激光雷达、里程计等）
- 交互式多选话题
- 导出结果为 JSON / YAML 格式

**安装与使用：**

```bash
cd ros2_helper
pip install -r requirements.txt
pip install -e .
ros2-helper
```

---

## USB 扫描

### `USB_scan/`

跨平台 USB 设备扫描与实时监控工具。

**功能特性：**
- **扫描模式**：快照当前所有 USB 设备，写入 Markdown 日志
- **监控模式**：实时监听 USB 插拔事件（添加 / 移除）
- Linux 版基于 `pyudev`，Windows 版基于 WMI

```bash
cd USB_scan
# 扫描模式
python main.py scan
# 监控模式
python main.py monitor
```

---

## 网络扫描

### `wlan_scan/`（完整扫描框架）

功能丰富的跨平台局域网扫描器。

**功能特性：**
- 子网自动检测
- 默认网关查找（含公网 IP 获取、路由追踪）
- 高并发 ARP Ping 局域网设备发现
- TCP 端口扫描（支持常见端口列表和全端口扫描）
- 设备识别（MAC 地址、主机名、厂商 OUI 识别）
- 多种输出格式：彩色终端、JSON、CSV
- 交互式菜单模式

```bash
cd wlan_scan
pip install -r requirements.txt
python main.py --interactive
```

### `局域网设备扫描/`（轻量脚本）

简洁的局域网设备发现脚本，适合快速使用。

| 脚本 | 适用平台 |
|------|----------|
| `network_linux.py` | Linux - 基础 Ping 扫描 |
| `network_linux_v2.py` | Linux - 增强版（含 MAC、主机名） |
| `network_windows.py` | Windows |

```bash
python "局域网设备扫描/network_linux.py"
```

---



项目结构

RDK小车开发常用工具/
├── 磁盘工具/
│   └── disk_monitor.py        # 磁盘监控
├── 局域网设备扫描/
│   ├── network_linux.py       # Linux 局域网扫描
│   ├── network_linux_v2.py
│   ├── network_windows.py     # Windows 局域网扫描
│   └── scan_results.txt
├── 文件夹结构打印工具/
│   └── tree_交互式输入路径.py
├── CPU测试/
│   └── cpu-benchmark/         # C++ CPU性能基准测试
├── CPU&磁盘基准测试/
│   ├── 磁盘IO速度测试.py
│   └── CPU单核基准测试.py
├── ros2_helper/               # ROS2 辅助工具（解析、保存、扫描、UI）
├── USB_scan/                  # USB/雷达串口扫描、数据解析
├── wlan_scan/                 # 无线网络扫描工具
│   ├── core/      # 日志+网络工具
│   ├── discovery/ # 网关/子网发现
│   ├── models/    # 设备/扫描数据模型
│   ├── output/    # 控制台/CSV/JSON 输出
│   ├── scanner/   # 局域网+端口扫描
│   └── main.py
└── README.md




## 雷达调试

### `USB_scan/code_秦嘉伟_20260317/雷达/`

激光雷达串口调试与可视化工具。

**工具列表：**

| 文件 | 用途 |
|------|------|
| `COM3_link.py` | 串口连接雷达，原始十六进制数据读取 |
| `decode.py` | 雷达协议解码（角度、距离、校验和验证） |
| `display.py` | Pygame 实时 360° 极坐标雷达可视化 |

```bash
# 实时可视化雷达数据
python "USB_scan/code_秦嘉伟_20260317/雷达/display.py"
```

---

## 实用工具

### `文件夹结构打印忽略特殊文件夹/tree_交互式输入路径.py`

交互式目录树打印工具，以 `tree` 风格输出目录结构，自动忽略 `venv`、`__pycache__`、`node_modules`、`.git`、`dist`、`build` 等文件夹。支持深度限制和 `~` 路径展开。

```bash
python "文件夹结构打印忽略特殊文件夹/tree_交互式输入路径.py"
```

---

## 系统要求

- **操作系统**：Linux（主要）、Windows（部分工具支持）
- **Python**：3.8+
- **ROS2**：Jazzy（ros2_helper 需要）
- **C++ 工具**：gcc/clang、make、zlib（cpu-benchmark 需要）

## 许可

本项目工具仅供 RDK 小车开发调试使用。
