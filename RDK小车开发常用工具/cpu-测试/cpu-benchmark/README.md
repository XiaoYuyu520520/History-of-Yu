# CPU Benchmark Tool

一个用 C++ 编写的 CPU 性能检测工具，可测试整数运算、浮点运算（FP32/FP64）性能，以及核间延迟并生成热力图。

## 功能特性

- **整数运算测试**：加法、乘法、除法、取模
- **浮点运算测试**：
  - FP32（单精度）：加法、乘法、FMA
  - FP64（双精度）：加法、乘法、FMA
- **核间延迟测试**：测量所有 CPU 核心对之间的通信延迟
- **热力图可视化**：生成 PNG 格式的延迟热力图

## 环境要求

### 硬件

- x86_64 架构 CPU
- Linux 操作系统
- 建议 4 核以上 CPU

### 软件依赖

- **GCC** >= 7.0 或 **Clang** >= 5.0
- **GNU Make**
- **zlib** 开发库（用于 PNG 压缩）

### 安装依赖（Ubuntu/Debian）

```bash
sudo apt-get update
sudo apt-get install build-essential zlib1g-dev
```

### 安装依赖（CentOS/RHEL）

```bash
sudo yum install gcc-c++ make zlib-devel
```

### 安装依赖（macOS）

```bash
brew install gcc make zlib
```

## 编译

### 默认编译

```bash
cd cpu-benchmark
make
```

### 清理编译

```bash
make clean
```

### 自定义编译选项

编辑 `Makefile` 可以修改编译选项：

```makefile
CXX = g++
CXXFLAGS = -O3 -march=native -std=c++17 -Wall -Wextra
```

- `-O3`：最高优化级别
- `-march=native`：针对本地 CPU 优化
- `-std=c++17`：使用 C++17 标准

## 运行

### 基本用法

```bash
./cpu-benchmark
```

### 命令行选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--no-integer` | 跳过整数基准测试 | 启用 |
| `--no-fp` | 跳过浮点基准测试 | 启用 |
| `--no-latency` | 跳过核间延迟测试 | 启用 |
| `-i <num>` | 整数/浮点测试迭代次数 | 100000000 |
| `-l <num>` | 延迟测试迭代次数 | 1000 |
| `-c <size>` | 热力图单元格大小 | 50 |
| `-h, --help` | 显示帮助信息 | - |

### 运行示例

```bash
# 完整测试（默认）
./cpu-benchmark

# 快速测试（减少迭代次数）
./cpu-benchmark -i 10000000 -l 500

# 只测试浮点性能
./cpu-benchmark --no-integer --no-latency

# 只测试核间延迟（生成热力图）
./cpu-benchmark --no-integer --no-fp

# 自定义热力图大小
./cpu-benchmark -c 80
```

## 输出说明

### 终端输出示例

```
===========================================
     CPU Performance Benchmark Tool       
===========================================

CPU: Intel(R) Core(TM) i7-2670QM CPU @ 2.20GHz
CPU Cores: 8

=== Running Integer Benchmarks ===
  Add: 0.527094 Gops/s
  Multiply: 0.456002 Gops/s
  ...

=== Running FP32 Benchmarks ===
  FP32 Add: 0.41073 Gops/s
  ...

=== Running FP64 Benchmarks ===
  FP64 Add: 0.405167 Gops/s
  ...

=== Results ===

Test Name                   OPS/sec       Time(ns)
--------------------------------------------------
Integer Add                 0.53 G    1.90 ns
Integer Multiply            0.46 G    2.19 ns
...

=== Running Core-to-core Latency Test ===
Measuring core-to-core latency (8 cores, 1000 iterations per pair)...
Progress: 64/64
Done!

Latency Matrix (ns):
         0     1     2     3     4     5     6     7
   0     0  23.5  24.1  23.8  35.2  34.8  35.1  34.9
   1  23.2     0  23.6  24.0  35.0  35.3  34.7  35.1
   ...

CSV saved to latency_matrix.csv
Heatmap saved to latency_heatmap.png

=== Benchmark Complete ===
```

### 输出文件

1. **latency_matrix.csv** - 延迟矩阵的 CSV 格式数据
2. **latency_heatmap.png** - 延迟热力图图片

### 热力图说明

- 颜色从蓝到红表示延迟从低到高
- X 轴和 Y 轴表示 CPU 核心编号
- 每个单元格颜色对应两个核心间的通信延迟

## 核间延迟测试原理

本工具使用 **CAS (Compare-And-Swap)** 原子操作测量核间延迟：

1. 创建两个线程，分别绑定到不同的 CPU 核心
2. 线程 A 通过原子操作发送消息
3. 线程 B 收到消息后回复确认
4. 测量多次往返时间并计算平均值

这种方法利用了 CPU 缓存一致性协议，能够真实反映核心间的通信延迟。

## 性能优化说明

### 整数/浮点测试

- 使用 RDTSC 指令进行高精度计时
- 编译器优化：`-O3 -march=native`
- 循环展开以减少分支预测开销

### 延迟测试

- 线程 CPU 亲和性绑定
- 使用 `memory_order_seq_cst` 内存序保证一致性
- 多次测量取平均以提高精度

## 常见问题

### Q: 延迟测试时间太长怎么办？

A: 使用 `-l` 参数减少迭代次数，例如：
```bash
./cpu-benchmark -l 500
```

### Q: 热力图无法生成？

A: 确保已安装 zlib 开发库：
```bash
# Ubuntu
sudo apt-get install zlib1g-dev
```

### Q: 如何在虚拟机中运行？

A: 虚拟机中核间延迟测试结果可能不准确，建议在物理机上运行以获得真实数据。

### Q: 支持 AMD CPU 吗？

A: 支持，代码使用通用的 x86 指令集，AMD 和 Intel CPU 均可运行。

## 项目结构

```
cpu-benchmark/
├── src/
│   ├── main.cpp           # 主程序入口
│   ├── integer_bench.cpp  # 整数运算测试
│   ├── fp_bench.cpp       # 浮点运算测试
│   ├── latency_bench.cpp  # 核间延迟测试
│   └── heatmap.cpp       # PNG 热力图生成
├── include/
│   ├── cpu_benchmark.h    # 头文件
│   └── stb_image_write.h # 图片库
├── Makefile               # 编译脚本
└── README.md              # 说明文档
```

## 许可证

MIT License

## 参考项目

- [c2clat](https://github.com/rigtorp/c2clat) - Core-to-core latency measurement
- [Flops](https://github.com/Mysticial/Flops) - FLOPS benchmark
- [core-to-core-latency-plus](https://github.com/KCORES/core-to-core-latency-plus) - 增强版核间延迟测试
