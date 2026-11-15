#!/bin/bash
# ====================================================
#  Image Optimizer - macOS (.app / .dmg) 빌드 스크립트
#  지원: Apple Silicon (M1/M2/M3/M4) 및 Intel Mac
# ====================================================
set -e

echo "=== [1/3] 의존성 설치 ==="
pip install -r requirements.txt
pip install pyinstaller

echo "=== [2/3] macOS .app 번들 빌드 ==="
pyinstaller --windowed \
            --clean \
            --name="ImageOptimizer" \
            main_gui.py

echo "=== [3/3] 빌드 완료 ==="
echo "생성된 앱 번들: dist/ImageOptimizer.app"
echo "DMG 파일 생성을 원할 경우: hdiutil create -volname ImageOptimizer -srcfolder dist/ImageOptimizer.app -ov -format UDZO dist/ImageOptimizer.dmg"
