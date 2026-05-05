# WLAN Scanner

跨平台网络扫描工具 | Cross-platform Network Scanner

[English](#english) | [中文](#中文)

---

## 功能特性

### 核心功能
- **网段发现** - 自动检测本机所有网络接口和网段
- **网关查找** - 寻找可访问互联网的网络出口
- **局域网扫描** - 高并发扫描局域网存活设备
- **端口扫描** - 支持常用端口和全端口 (0-65535) 扫描
- **设备识别** - 获取 MAC 地址、主机名、厂商信息

### 技术特性
- **跨平台** - 支持 Ubuntu 和 Windows
- **高并发** - 默认 500 并发，支持自定义
- **模块化** - 清晰的模块设计，便于复用
- **交互模式** - 菜单式操作，逐步选择
- **配置持久化** - 默认选项自动保存

---

## 安装

### 1. 克隆或下载项目

```bash
git clone <repository-url>
cd wlan_scan
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 依赖列表
```
psutil>=5.9.0      # 网络接口获取
colorama>=0.4.6    # 终端着色
requests>=2.28.0   # HTTP 请求
```

---

## 使用方式

### 命令行模式

```bash
# 检测本机所有网段
python main.py --detect-subnets

# 寻找互联网网关
python main.py --find-gateway

# 扫描本机所有网段 (常用端口)
python main.py --scan-local

# 扫描指定网段
python main.py --subnet 192.168.1.0/24

# 全端口扫描 (0-65535)
python main.py --scan-local --full-port

# 自定义端口扫描
python main.py --subnet 192.168.1.0/24 --ports 22,80,443

# 获取设备详细信息 (MAC/主机名/厂商)
python main.py --scan-local --enrich

# 输出到 JSON 文件
python main.py --scan-local --enrich --output-json results.json

# 输出到 CSV 文件
python main.py --scan-local --enrich --output-csv results.csv

# 同时输出 JSON 和 CSV
python main.py --scan-local --enrich --output-json results.json --output-csv results.csv

# 自定义并发数
python main.py --scan-local --concurrency 1000

# 查看帮助
python main.py --help
```

### 交互模式

```bash
# 启动交互式菜单
python main.py --interactive
# 或
python main.py -i
```

交互模式提供菜单式操作：
- 检测本机网段
- 寻找互联网网关
- 扫描局域网设备
- 扫描指定网段
- 设置默认选项
- 查看当前配置

按 Enter 使用默认值，默认值保存在 `~/.wlan_scan/config.json`

---

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--detect-subnets` | 检测本机所有网段 | - |
| `--find-gateway` | 寻找互联网网关 | - |
| `--scan-local` | 扫描本机所有网段 | - |
| `--subnet` | 扫描指定网段 (CIDR) | - |
| `--interactive`, `-i` | 交互式菜单模式 | - |
| `--full-port` | 全端口扫描 (0-65535) | False |
| `--ports` | 端口: common/all/逗号分隔 | common |
| `--concurrency` | 并发数 (50-1000) | 500 |
| `--timeout` | 超时时间 (秒) | 1.0 |
| `--enrich` | 获取设备详细信息 | False |
| `--output-json` | JSON 输出文件 | - |
| `--output-csv` | CSV 输出文件 | - |
| `-v`, `--verbose` | 详细输出 | - |
| `-q`, `--quiet` | 静默模式 | - |

---

## 项目结构

```
wlan_scan/
├── core/                      # 核心工具模块
│   ├── __init__.py
│   ├── network_utils.py       # 跨平台网络工具
│   └── logger.py             # 日志模块
├── discovery/                 # 网络发现模块
│   ├── __init__.py
│   ├── subnet_detector.py    # 获取本机网段
│   └── gateway_finder.py     # 寻找互联网出口
├── scanner/                   # 扫描模块
│   ├── __init__.py
│   ├── lan_scanner.py        # 局域网扫描
│   ├── port_scanner.py       # 端口扫描
│   └── device_info.py        # 设备信息解析
├── models/                    # 数据模型
│   ├── __init__.py
│   ├── device.py             # 设备模型
│   └── scan_result.py        # 扫描结果模型
├── output/                    # 输出模块
│   ├── __init__.py
│   ├── console_writer.py     # 终端输出
│   ├── json_writer.py        # JSON 输出
│   └── csv_writer.py         # CSV 输出
├── config.py                  # 配置文件管理
├── interactive.py             # 交互式菜单
├── main.py                    # 主入口
├── requirements.txt           # 依赖
└── README.md                  # 文档
```

---

## 模块说明

### Core 模块
- `NetworkUtils` - 跨平台网络接口获取、IP 处理

### Discovery 模块
- `SubnetDetector` - 检测本机所有网段
- `GatewayFinder` - 寻找互联网出口

### Scanner 模块
- `LanScanner` - 局域网设备扫描
- `PortScanner` - 端口扫描 (支持 0-65535)
- `DeviceInfo` - MAC 地址、主机名、厂商识别

### Output 模块
- `ConsoleWriter` - 终端彩色输出
- `JsonWriter` - JSON 文件输出
- `CsvWriter` - CSV 文件输出

---

## 使用示例

### 编程调用

```python
from scanner import LanScanner, PortScanner, DeviceInfo
from discovery import SubnetDetector, GatewayFinder
from models import Device

# 检测网段
detector = SubnetDetector()
subnets = detector.detect_all_subnets()

# 寻找网关
finder = GatewayFinder()
gateway = finder.find_internet_exit()

# 扫描局域网
scanner = LanScanner(concurrency=500)
devices = scanner.scan_network("192.168.1.0/24")

# 扫描端口
port_scanner = PortScanner(concurrency=500)
for device in devices:
    device.open_ports = port_scanner.scan_ports(device.ip)

# 获取设备信息
device_info = DeviceInfo()
device_info.enrich_device(device)
```

---

## 注意事项

1. **权限** - 某些操作可能需要管理员/root 权限
2. **网络** - 确保有网络访问权限
3. **防火墙** - 防火墙可能阻止扫描
4. **限速** - 建议不要使用过高的并发数

---

## 许可证

MIT License

---

## English

### Features

- **Subnet Detection** - Auto-detect all network interfaces and subnets
- **Gateway Finding** - Find internet-accessible network exit
- **LAN Scanning** - High-concurrency local network scanning
- **Port Scanning** - Common ports or full range (0-65535)
- **Device Identification** - MAC address, hostname, vendor info

### Installation

```bash
pip install -r requirements.txt
```

### Quick Start

```bash
# Interactive mode
python main.py --interactive

# Scan local network
python main.py --scan-local

# Scan specific subnet
python main.py --subnet 192.168.1.0/24

# Full port scan
python main.py --scan-local --full-port

# Save to JSON/CSV
python main.py --scan-local --enrich --output-json results.json
```

### Configuration

Default config stored in: `~/.wlan_scan/config.json`

```json
{
  "scan": {
    "concurrency": 500,
    "timeout": 1.0,
    "ports": "common",
    "enrich": true
  },
  "output": {
    "format": "console",
    "json_file": "results.json",
    "csv_file": "results.csv"
  }
}
```
