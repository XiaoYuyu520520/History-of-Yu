#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$PROJECT_DIR/build"
VERSION="1.0.0"
BUILD_TIME=$(date '+%Y-%m-%d_%H:%M:%S')
COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

echo "=== NetSpeed Builder v$VERSION ==="
echo "Build time: $BUILD_TIME"
echo ""

# Step 1: Build Vue frontend
echo "[1/3] Building Vue frontend..."
cd "$PROJECT_DIR/frontend"
export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
  \. "$NVM_DIR/nvm.sh"
fi
npm install --silent
npm run build
echo "  Frontend built: frontend/dist/"
echo ""

# Step 2: Build Go backend for current platform
echo "[2/3] Building Go backend (current platform)..."
cd "$PROJECT_DIR"
go build -ldflags="-s -w -X main.version=$VERSION -X main.buildTime=$BUILD_TIME" -o "$OUTPUT_DIR/netspeed" .
echo "  Output: $OUTPUT_DIR/netspeed"
echo ""

# Step 3: Cross-compile for other platforms
echo "[3/3] Cross-compiling..."

# ARM64 Linux (e.g., Jetson, Raspberry Pi)
echo "  Target: linux/arm64"
GOOS=linux GOARCH=arm64 go build -ldflags="-s -w" -o "$OUTPUT_DIR/netspeed-linux-arm64" .
echo "    Output: $OUTPUT_DIR/netspeed-linux-arm64"

# AMD64 Windows
echo "  Target: windows/amd64"
GOOS=windows GOARCH=amd64 go build -ldflags="-s -w" -o "$OUTPUT_DIR/netspeed-windows-amd64.exe" .
echo "    Output: $OUTPUT_DIR/netspeed-windows-amd64.exe"

# AMD64 Linux
echo "  Target: linux/amd64"
GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o "$OUTPUT_DIR/netspeed-linux-amd64" .
echo "    Output: $OUTPUT_DIR/netspeed-linux-amd64"
echo ""

echo "=== Build complete ==="
echo "Output directory: $OUTPUT_DIR"
ls -lh "$OUTPUT_DIR/"
echo ""
echo "To run: cd $OUTPUT_DIR && ./netspeed"
echo "Then open http://localhost:7777 in your browser"
