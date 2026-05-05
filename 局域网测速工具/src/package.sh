#!/bin/bash
set -e

VERSION="${1#v}"
VERSION="${VERSION:-1.0.0}"
OUTPUT_DIR="release/netspeed-$VERSION"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== NetSpeed Packager v$VERSION ==="
echo ""

# Step 1: Build everything
echo "[1/4] Building frontend..."
cd "$PROJECT_DIR/frontend"
export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
  \. "$NVM_DIR/nvm.sh"
fi
npm install --silent
npm run build

echo "[2/4] Building Go binaries..."
cd "$PROJECT_DIR"

build() {
  local GOOS="$1" GOARCH="$2" SUFFIX="$3"
  local BIN="netspeed-$GOOS-$GOARCH$SUFFIX"
  echo "  -> $BIN"
  GOOS="$GOOS" GOARCH="$GOARCH" go build -ldflags="-s -w" -o "$OUTPUT_DIR/bin/$BIN" .
}

mkdir -p "$OUTPUT_DIR/bin"
build linux   amd64 ""
build linux   arm64 ""
build windows amd64 ".exe"
go build -ldflags="-s -w" -o "$OUTPUT_DIR/bin/netspeed" .

echo "[3/4] Copying source code..."
cd "$PROJECT_DIR"

mkdir -p "$OUTPUT_DIR/src"
mkdir -p "$OUTPUT_DIR/src/backend/model"
mkdir -p "$OUTPUT_DIR/src/backend/handler"
mkdir -p "$OUTPUT_DIR/src/backend/loglib"
mkdir -p "$OUTPUT_DIR/src/frontend/src/composables"
mkdir -p "$OUTPUT_DIR/src/frontend/src/components"
mkdir -p "$OUTPUT_DIR/src/frontend/dist/assets"

# Go backend
cp backend/model/types.go      "$OUTPUT_DIR/src/backend/model/"
cp backend/handler/ws.go       "$OUTPUT_DIR/src/backend/handler/"
cp backend/handler/speedtest.go "$OUTPUT_DIR/src/backend/handler/"
cp backend/loglib/logger.go    "$OUTPUT_DIR/src/backend/loglib/"
cp main.go                     "$OUTPUT_DIR/src/"

# Frontend source
cp frontend/index.html         "$OUTPUT_DIR/src/frontend/"
cp frontend/vite.config.js     "$OUTPUT_DIR/src/frontend/"
cp frontend/package.json       "$OUTPUT_DIR/src/frontend/"
cp frontend/src/main.js        "$OUTPUT_DIR/src/frontend/src/"
cp frontend/src/App.vue        "$OUTPUT_DIR/src/frontend/src/"
cp frontend/src/composables/useSpeedTest.js "$OUTPUT_DIR/src/frontend/src/composables/"
cp frontend/src/components/TestControls.vue   "$OUTPUT_DIR/src/frontend/src/components/"
cp frontend/src/components/SpeedGauge.vue     "$OUTPUT_DIR/src/frontend/src/components/"
cp frontend/src/components/ResultsHistory.vue "$OUTPUT_DIR/src/frontend/src/components/"

# Built frontend dist (needed for Go embed)
cp frontend/dist/index.html    "$OUTPUT_DIR/src/frontend/dist/"
cp frontend/dist/assets/*.js   "$OUTPUT_DIR/src/frontend/dist/assets/"
cp frontend/dist/assets/*.css  "$OUTPUT_DIR/src/frontend/dist/assets/"

# Go module
cp go.mod go.sum               "$OUTPUT_DIR/src/"

# Scripts & docs
cp build.sh start.py package.sh .gitignore README.md "$OUTPUT_DIR/src/" 2>/dev/null || true

echo "[4/4] Writing release metadata..."
cat > "$OUTPUT_DIR/RELEASE.txt" <<EOF
NetSpeed v$VERSION
Release date: $(date '+%Y-%m-%d')
Build commit: $(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

Contents:
  bin/       - Pre-compiled binaries (ready to run)
  src/       - Full source code (build from source)

Quick start:
  # Run directly
  ./bin/netspeed

  # Or build from source
  cd src && bash build.sh

  # Open http://localhost:7777
EOF

# Create archive
echo ""
echo "=== Packaging ==="
cd "$PROJECT_DIR"
tar czf "release/netspeed-$VERSION.tar.gz" -C release "netspeed-$VERSION/"
cd "$PROJECT_DIR/release"
zip -qr "netspeed-$VERSION.zip" "netspeed-$VERSION/"

echo ""
echo "=== Done ==="
echo "Output: $PROJECT_DIR/release/netspeed-$VERSION/"
echo "  tar.gz: $PROJECT_DIR/release/netspeed-$VERSION.tar.gz"
echo "  zip:    $PROJECT_DIR/release/netspeed-$VERSION.zip"
echo ""
echo "Release contents:"
du -sh "$PROJECT_DIR"/release/netspeed-$VERSION/*
echo ""
echo "Archive size:"
ls -lh "$PROJECT_DIR"/release/netspeed-$VERSION.tar.gz "$PROJECT_DIR"/release/netspeed-$VERSION.zip
