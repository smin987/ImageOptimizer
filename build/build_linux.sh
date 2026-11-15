#!/bin/bash
# ====================================================
#  Image Optimizer - Linux Debian/Ubuntu 빌드 스크립트
# ====================================================
set -e

# 스크립트 위치 기준 프로젝트 루트 경로 계산
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== [1/3] Linux Python 가상환경 구성 및 패키지 설치 ==="
if [ ! -d ".venv_linux" ]; then
    python3 -m venv .venv_linux
fi

.venv_linux/bin/pip install --upgrade pip
.venv_linux/bin/pip install -r requirements.txt
.venv_linux/bin/pip install pyinstaller

echo "=== [2/3] Linux 단일 실행 바이너리 빌드 (PyInstaller) ==="
mkdir -p dist/linux
.venv_linux/bin/pyinstaller --noconsole \
                           --onefile \
                           --clean \
                           --add-data="assets:assets" \
                           --distpath="dist/linux" \
                           --name="ImageOptimizer" \
                           main_gui.py

echo "=== [3/3] 빌드 완료 ==="
chmod +x dist/linux/ImageOptimizer
echo "결과 바이너리 위치: dist/linux/ImageOptimizer"
ls -lh dist/linux/ImageOptimizer
