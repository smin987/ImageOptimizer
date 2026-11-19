#!/bin/bash
# ====================================================
#  Image Optimizer - Debian (.deb) 패키징 스크립트
#  사용법: ./package_deb.sh <amd64|arm64> <version> <binary_path> <output_dir>
# ====================================================
set -e

ARCH="$1"
RAW_VERSION="$2"
BIN_PATH="$3"
OUTPUT_DIR="$4"

if [ -z "$ARCH" ] || [ -z "$RAW_VERSION" ] || [ -z "$BIN_PATH" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: $0 <amd64|arm64> <version> <binary_path> <output_dir>"
    exit 1
fi

# 버전 앞의 'v' 접두사 제거 (예: v1.0.3 -> 1.0.3)
VERSION="${RAW_VERSION#v}"

# 프로젝트 루트 디렉토리 계산
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PKG_DIR="$PROJECT_ROOT/pkg_build_${ARCH}"
rm -rf "$PKG_DIR"
mkdir -p "$PKG_DIR/DEBIAN"
mkdir -p "$PKG_DIR/usr/bin"
mkdir -p "$PKG_DIR/usr/share/applications"
mkdir -p "$PKG_DIR/usr/share/icons/hicolor/512x512/apps"
mkdir -p "$OUTPUT_DIR"

# 1. 바이너리 복사 및 실행 권한 부여
cp "$BIN_PATH" "$PKG_DIR/usr/bin/image-optimizer"
chmod 755 "$PKG_DIR/usr/bin/image-optimizer"

# 2. 고해상도 앱 아이콘 복사
if [ -f "$PROJECT_ROOT/assets/icon.png" ]; then
    cp "$PROJECT_ROOT/assets/icon.png" "$PKG_DIR/usr/share/icons/hicolor/512x512/apps/image-optimizer.png"
    chmod 644 "$PKG_DIR/usr/share/icons/hicolor/512x512/apps/image-optimizer.png"
fi

# 3. 데스크톱 런처 (.desktop) 파일 생성
cat <<EOF > "$PKG_DIR/usr/share/applications/image-optimizer.desktop"
[Desktop Entry]
Name=Image Optimizer
Name[ko]=이미지 옵티마이저
Comment=All-in-one image and animated GIF optimizer for web and desktop
Comment[ko]=웹과 데스크톱을 위한 이미지 및 움직이는 GIF 최적화 도구
Exec=image-optimizer
Icon=image-optimizer
Terminal=false
Type=Application
Categories=Graphics;2DGraphics;RasterGraphics;Utility;
StartupNotify=true
EOF
chmod 644 "$PKG_DIR/usr/share/applications/image-optimizer.desktop"

# 4. Debian control 파일 생성
cat <<EOF > "$PKG_DIR/DEBIAN/control"
Package: image-optimizer
Version: $VERSION
Section: non-free/graphics
Priority: optional
Architecture: $ARCH
Depends: libc6, libgl1, libegl1, libxkbcommon0, libdbus-1-3
Maintainer: smin987 <https://github.com/smin987/ImageOptimizer>
Homepage: https://github.com/smin987/ImageOptimizer
Description: All-in-one cross-platform image and animation optimizer (WebP, JPG, GIF)
 Ultra-efficient image and animated GIF optimizer for web and desktop.
 Drastically compress image sizes by up to 90% with minimal quality loss.
 Features animated GIF to WebP conversion, alpha preservation, and smart resizing.
EOF
chmod 644 "$PKG_DIR/DEBIAN/control"

# 5. .deb 패키지 빌드
DEB_NAME="ImageOptimizer_${VERSION}_${ARCH}.deb"
dpkg-deb --build --root-owner-group "$PKG_DIR" "$OUTPUT_DIR/$DEB_NAME"

# 정리
rm -rf "$PKG_DIR"

echo "=== Debian 패키지 빌드 완료: $OUTPUT_DIR/$DEB_NAME ==="
ls -lh "$OUTPUT_DIR/$DEB_NAME"
