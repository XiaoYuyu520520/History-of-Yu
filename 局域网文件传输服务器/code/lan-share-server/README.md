# Lan Share Server — 局域网文件共享服务

基于 FastAPI 的轻量级局域网文件共享服务器，支持 PyInstaller 打包为单文件 exe。

## 快速开始

```bash
cd backend
pip install -r requirements.txt
python server.py
# 访问 http://localhost:8005
```

## 功能

- **文件浏览** — Web 界面列出并导航共享目录
- **文件下载** — 点击即可下载共享文件
- **配置灵活** — 通过 `config.yaml` 自定义端口和共享目录
- **即点即用** — 支持 PyInstaller 打包为独立 exe 分发

## 配置

编辑 `backend/config.yaml`：

```yaml
server:
  host: "0.0.0.0"
  port: 8005

files:
  shared_directory: "X:\\"    # 共享目录路径
```

## 打包为单文件 exe

参考 [`backend/packaging-guide.md`](backend/packaging-guide.md) 了解如何使用 PyInstaller 将服务打包为独立可执行文件。

## 目录结构

```
lan-share-server/
├── backend/
│   ├── server.py              # FastAPI 主服务
│   ├── server_for_packaging.py # 打包专用版本
│   ├── config.yaml            # 服务配置
│   ├── requirements.txt       # Python 依赖
│   ├── packaging-guide.md     # PyInstaller 打包教程
│   ├── dist/                  # 构建输出
│   └── dist1/
├── frontend/
│   ├── index.html             # 前端主页面
│   ├── index_3.html
│   ├── css/                   # 样式文件
│   └── js/                    # 脚本文件
└── README.md
```

## 技术栈

- **后端**：FastAPI + Uvicorn
- **前端**：原生 HTML / CSS / JavaScript
- **打包**：PyInstaller
