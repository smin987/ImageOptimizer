# 🚀 Image Optimizer (이미지 옵티마이저)

<div align="center">

<p>
  <a href="README.md"><b>English</b></a> • <b>한국어 (Korean)</b>
</p>

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-41cd52.svg)](https://www.qt.io/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](#-지원-플랫폼)
[![Sponsor](https://img.shields.io/badge/Sponsor-💖-ff69b4.svg)](#-개발자-후원하기)

**웹과 데스크톱을 위한 올인원 크로스 플랫폼 이미지 & 애니메이션 최적화 도구**  
*초고효율 WebP / JPG 변환, 움직이는 GIF 애니메이션 최적화, 투명 배경 보존 및 스마트 리사이징*

[주요 기능](#-주요-기능) • [다운로드](#-다운로드) • [소스코드 실행](#-소스코드-실행-및-빌드) • [후원하기](#-개발자-후원하기)

</div>

---

## 🌟 개요 (Overview)

**Image Optimizer**는 원본 이미지의 우수한 시각적 화질을 그대로 유지하면서 파일 용량을 최대 90%까지 경량화하여, 웹사이트 로딩 속도와 스토리지 효율을 극대화하는 **오픈소스 크로스 플랫폼 데스크톱 도구**입니다.

일반 정지 이미지(`PNG`, `JPG`, `BMP`, `TIFF` 등)뿐만 아니라 **움직이는 GIF(움짤)**의 모든 프레임과 타이밍을 온전히 보존하는 **애니메이션 WebP 변환**을 완벽하게 지원합니다.

---

## ✨ 주요 기능 (Key Features)

- ⚡ **초고효율 포맷 변환**
  - `WebP`: 원본 대비 최대 90% 용량 절감
  - `JPG`: 뛰어난 호환성의 고화질 압축
  - `둘 다(BOTH)`: WebP와 JPG를 동시에 한 번에 생성 (웹 최적화 및 레거시 대응)
- 🎞️ **움직이는 GIF (움짤) 애니메이션 최적화**
  - 모든 프레임과 재생 속도를 100% 보존하며 용량을 획기적으로 줄여주는 **애니메이션 WebP** 변환
  - 첫 프레임을 추출하여 정지 이미지 JPG로 변환하는 모드 지원
- 📐 **3가지 스마트 리사이즈 모드**
  - **최대 가로폭에 맞춤 (Fit Max Width)**: 4K, FHD, HD 등 가로폭 초과 시 비율을 유지하며 자동 축소
  - **비율(%) 축소 (Scale %)**: 25%, 50%, 75% 등 원하는 배율로 직관적 축소
  - **원본 크기 유지 (100%)**: 해상도 변경 없이 순수 포맷 압축만 수행
- 🎨 **투명 배경(Alpha Channel) 보존 / 제거 선택**
  - 투명 배경을 100% 유지하며 WebP로 압축하거나, 필요 시 흰색 배경으로 합성
- 🌐 **원클릭 다국어 지원 (Bilingual UI)**
  - 상단 버튼 클릭 한 번으로 **한국어 ↔ English** 즉시 전환 (설정 자동 저장)
- 🌗 **다크 모드 & 라이트 모드 테마**
  - 눈이 편안한 세련된 다크 테마 및 깔끔한 라이트 테마 지원
- 🗑️ **안전한 원본 파일 처리**
  - 영구 삭제 위험 없이 **시스템 휴지통(Trash)**으로 안전하게 이동
- 📊 **실시간 성과 대시보드**
  - 변환 성공 건수, 총 절약된 용량(MB), 평균 절감률(%)을 실시간으로 집계 및 시각화
- 💖 **원클릭 후원 연동**
  - 앱 헤더 바에 탑재된 `💖 후원하기` 버튼으로 개발자 GitHub Sponsors 페이지 바로가기 지원

---

## 💻 지원 플랫폼 (Platform Support)

| 플랫폼 | 아키텍처 | 설치 및 패키지 형식 | 지원 상태 |
| :--- | :--- | :--- | :--- |
| **Windows 11 / 10** | x64 (AMD64) | 무설치 단일 파일 (`.exe`) / 설치 마법사 | ✅ 지원 완료 |
| **macOS (Apple Silicon & Intel)** | Universal (M1/M2/M3/M4 & Intel) | **Homebrew Cask** / 디스크 이미지 (`.dmg`) | ✅ 지원 완료 |
| **Linux (Debian, Ubuntu, Mint)** | x86_64 | **APT 데비안 패키지 (`.deb`)** / 단일 바이너리 | ✅ 지원 완료 |
| **Linux (라즈베리 파이, ARM SBC)** | ARM64 (aarch64) | **APT 데비안 패키지 (`.deb`)** / 단일 바이너리 | ✅ 지원 완료 |

---

## 📥 설치 및 다운로드 (Installation & Downloads)

### 🪟 Windows 환경 : winget을 통한 원클릭 설치
Windows 10/11의 공식 패키지 관리자(`winget`)를 통해 터미널에서 즉시 설치할 수 있습니다:
```powershell
winget install --manifest https://raw.githubusercontent.com/smin987/ImageOptimizer/main/build/winget/manifests/s/smin987/ImageOptimizer/1.0.3/smin987.ImageOptimizer.yaml
```

### 🍺 macOS 환경 : Homebrew를 통한 원클릭 설치
[Homebrew](https://brew.sh/)를 사용하면 Mac 터미널에서 명령어 한 줄로 편리하게 설치할 수 있습니다:
```bash
brew install --cask https://raw.githubusercontent.com/smin987/ImageOptimizer/main/build/homebrew/Casks/image-optimizer.rb
```

### 🐧 리눅스 환경 : 공식 APT 저장소 등록 (자동 업데이트 지원)
공식 APT 저장소를 등록해 두면 `apt upgrade` 시 항상 최신 버전으로 자동 업데이트됩니다:
```bash
# 1. 저장소 공개키 등록
curl -fsSL https://smin987.github.io/ImageOptimizer/repo.key | sudo gpg --dearmor -o /etc/apt/keyrings/image-optimizer.gpg

# 2. 저장소 소스 추가
echo "deb [signed-by=/etc/apt/keyrings/image-optimizer.gpg] https://smin987.github.io/ImageOptimizer ./" | sudo tee /etc/apt/sources.list.d/image-optimizer.list

# 3. 설치 및 자동 업데이트
sudo apt update && sudo apt install image-optimizer
```
> *단일 `.deb` 패키지만 다운로드하여 직접 설치하시려면 [GitHub Releases](https://github.com/smin987/ImageOptimizer/releases)에서 다운로드 후 `sudo apt install ./ImageOptimizer_*_amd64.deb` (또는 `arm64.deb`)를 실행하세요.*

### 📦 무설치 포터블 단일 파일 (Direct Downloads)
별도의 설치 과정 없이 다운로드 후 바로 사용하시려면 **[GitHub Releases](https://github.com/smin987/ImageOptimizer/releases)**에서 다운로드하세요:

- **Windows**: `ImageOptimizer-windows-x64.exe` (다운로드 후 더블클릭으로 즉시 실행)
- **macOS**: `ImageOptimizer-macos.dmg` (열어서 응용 프로그램 폴더로 드래그 앤 드롭)
- **Linux x86_64**: `ImageOptimizer-linux-x86_64` (실행 권한 부여 후 실행: `chmod +x`)
- **Linux ARM64**: `ImageOptimizer-linux-arm64` (라즈베리 파이 4/5 및 ARM64 SBC용)

---

## 🛠️ 소스코드 실행 및 빌드

### 1. 요구 사항
- Python 3.10 이상

### 2. 직접 실행
```bash
# 저장소 복제
git clone https://github.com/smin987/ImageOptimizer.git
cd ImageOptimizer

# 필수 패키지 설치
pip install -r requirements.txt

# 앱 실행
python main_gui.py
```

### 3. 로컬 독립 실행 파일 빌드
- **Windows**: `build\build_windows.bat` 실행
- **Linux**: `bash build/build_linux.sh` 실행
- **macOS**: `bash build/build_macos.sh` 실행

---

## 💖 개발자 후원하기 (Sponsor)

**Image Optimizer**는 누구나 자유롭게 사용할 수 있는 **무료 오픈소스 소프트웨어(Apache 2.0)**입니다.  
이 프로그램이 유용하셨거나 지속적인 기능 업데이트, 성능 개선, 멀티플랫폼 지원을 응원하고 싶으시다면 커피 한 잔의 따뜻한 후원을 부탁드립니다! 여러분의 따뜻한 후원은 프로젝트를 유지하는 데 매우 큰 힘이 됩니다. ☕✨

<div align="center">

[![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa?style=for-the-badge&logo=github&logoColor=white)](https://github.com/sponsors/smin987)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/smin987)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/smin987)

> **💖 후원자 혜택**:
> - 🎖️ README 및 릴리즈 노트의 공식 후원자(Backers / Sponsors) 명단 등재
> - 🚀 버그 리포트 및 신규 기능 요청(Feature Request) 우선 검토
> - 💬 신규 실험 기능 우선 체험 및 개발자와의 직접 소통

</div>

---

## 📄 라이선스 (License)

본 프로젝트는 **[Apache License 2.0](LICENSE)**에 따라 배포됩니다.  
개인 및 상업적 용도로 자유롭게 사용, 수정, 배포하실 수 있습니다.
