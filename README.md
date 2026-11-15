# 🚀 Image Optimizer

<div align="center">

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-41cd52.svg)](https://www.qt.io/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](#-platform-support)
[![Sponsor](https://img.shields.io/badge/Sponsor-💖-ff69b4.svg)](#-support--sponsorship-후원하기)

**All-in-one Cross-Platform Image & Animation Optimizer for Web & Desktop**  
*초고효율 WebP / JPG 변환, 움직이는 GIF 애니메이션 최적화, 투명 배경 보존 및 리사이징 올인원 도구*

[English](#-key-features) • [한국어](#-주요-기능) • [Downloads](#-downloads) • [Sponsor](#-support--sponsorship-후원하기)

</div>

---

## 🌟 Overview (개요)

**Image Optimizer**는 원본 이미지의 뛰어난 시각적 화질을 유지하면서 파일 용량을 최대 90%까지 경량화하여 웹사이트 로딩 속도와 스토리지 효율을 극대화하는 **오픈소스 크로스 플랫폼 GUI 도구**입니다.

정지 이미지(`PNG`, `JPG`, `BMP`, `TIFF` 등)뿐만 아니라 **움직이는 GIF(움짤)**의 모든 프레임을 보존하는 **애니메이션 WebP 변환**을 완벽하게 지원합니다.

---

## ✨ Key Features (주요 기능)

- ⚡ **고효율 포맷 변환 (High-Efficiency Format Conversion)**
  - `WebP`: 원본 대비 최대 90% 용량 절감
  - `JPG`: 호환성 중심의 고화질 압축
  - `BOTH (둘 다)`: WebP와 JPG를 한 번에 동시 생성 (웹 서빙 및 레거시 대응)
- 🎞️ **움직이는 GIF (움짤) 완벽 지원 (Animated GIF Optimization)**
  - 애니메이션의 모든 프레임과 타이밍을 온전히 보존하여 가벼운 **애니메이션 WebP**로 변환
  - 또는 정지 이미지 JPG 추출 지원
- 📐 **3가지 스마트 리사이즈 모드 (Flexible Resizing)**
  - **최대 가로폭에 맞춤 (Fit Max Width)**: 4K, FHD, HD 등 가로폭 초과 시 비율 유지 축소
  - **비율(%) 축소 (Scale %)**: 25%, 50%, 75% 등 원하는 배율로 직관적 축소
  - **원본 크기 유지 (100%)**: 해상도 손실 없이 포맷 압축만 수행
- 🎨 **투명 배경(Alpha) 완벽 보존 / 제거 선택**
  - 투명 배경을 100% 보존하거나, 필요 시 흰색 배경으로 합성하는 옵션 제공
- 🌐 **원클릭 다국어 지원 (One-Click Bilingual UI)**
  - 상단 버튼 클릭 한 번으로 **한국어 ↔ English** 즉각 전환
- 🌗 **다크 모드 & 라이트 모드 (Dark / Light Theme)**
  - 시스템 테마에 맞춘 모던하고 눈이 편안한 감성적인 디자인
- 🗑️ **안전한 원본 파일 처리 (Safe Trash Integration)**
  - 영구 삭제가 아닌 **시스템 휴지통(Trash)** 안전 이동 지원
- 📊 **실시간 절감 성과 대시보드 (Real-time Savings Dashboard)**
  - 변환 성공률, 전후 용량 변화, 절감된 데이터 용량(MB) 및 절감률(%) 실시간 집계

---

## 💻 Platform Support (지원 플랫폼)

| Platform | Architecture | Binary Format | Support Status |
| :--- | :--- | :--- | :--- |
| **Windows 11 / 10** | x64 (AMD64) | Standalone `.exe` / Installer | ✅ Fully Supported |
| **Linux (Debian, Ubuntu, Mint)** | x86_64 & ARM64 | Standalone ELF Binary | ✅ Fully Supported |
| **macOS (Apple Silicon & Intel)** | Universal (arm64/x86_64) | `.dmg` / `.app` | ✅ Fully Supported |

---

## 📥 Downloads (다운로드)

최신 사전 컴파일된 단일 실행 파일은 [GitHub Releases](https://github.com/smin987/ImageOptimizer/releases) 페이지에서 다운로드할 수 있습니다:

- **Windows**: `ImageOptimizer-windows-x64.exe` (설치 없이 더블클릭 실행)
- **Linux**: `ImageOptimizer-linux-x86_64` (실행 권한 부여 후 실행: `chmod +x`)
- **macOS**: `ImageOptimizer-macos.dmg` (응용 프로그램 폴더로 드래그 앤 드롭)

---

## 🛠️ Build & Run from Source (소스코드 실행 및 빌드)

### 1. Requirements (요구 사항)
- Python 3.10 이상

### 2. Run Directly (직접 실행)
```bash
# 저장소 복제
git clone https://github.com/smin987/ImageOptimizer.git
cd ImageOptimizer

# 의존성 설치
pip install -r requirements.txt

# 앱 실행
python main_gui.py
```

### 3. Build Executable (로컬 빌드)
- **Windows**:
  ```cmd
  build\build_windows.bat
  ```
- **Linux**:
  ```bash
  chmod +x build/build_linux.sh
  ./build/build_linux.sh
  ```
- **macOS**:
  ```bash
  chmod +x build/build_macos.sh
  ./build/build_macos.sh
  ```

---

## 💖 Support & Sponsorship (후원하기)

**Image Optimizer**는 전 세계 누구나 자유롭게 사용할 수 있는 **무료 오픈소스 소프트웨어(Apache 2.0)**입니다.  
이 프로젝트가 유용하셨거나 지속적인 기능 업데이트, 성능 개선, 멀티플랫폼 지원을 응원하고 싶으시다면 작은 후원으로 개발자를 후원해 주세요! 여러분의 따뜻한 후원은 프로젝트를 유지하는 데 매우 큰 힘이 됩니다. ☕✨

<div align="center">

[![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa?style=for-the-badge&logo=github&logoColor=white)](https://github.com/sponsors/smin987)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/smin987)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/smin987)

> **후원자 혜택**:
> - README 및 릴리즈 노트의 공식 후원자(Backers / Sponsors) 명단 등재
> - 버그 리포트 및 신규 기능 요청(Feature Request) 우선 검토

</div>

---

## 📄 License (라이선스)

Image Optimizer is licensed under the **[Apache License 2.0](LICENSE)**.  
You are free to use, modify, distribute, and integrate this project for both personal and commercial purposes.

```
Copyright 2026 smin987

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```
