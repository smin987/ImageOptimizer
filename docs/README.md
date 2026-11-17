# 📚 Image Optimizer 개발 & 운영 가이드 (Developer & Operations Guide)

이 문서는 **Image Optimizer (`img2webp`)** 프로젝트의 아키텍처, 핵심 설정, 개발 워크플로우, GitHub 릴리스 배포 프로세스, 그리고 시스템 설계 다이어그램(UML)을 정리한 기술 매뉴얼입니다. 사람 개발자뿐만 아니라 AI 에이전트도 일관된 설계 원칙을 준수할 수 있도록 돕습니다.

---

## 📑 목차
1. [프로젝트 개요 및 구조](#1-프로젝트-개요-및-구조)
2. [앱 주요 설정 및 기능 사용법](#2-앱-주요-설정-및-기능-사용법)
3. [시스템 설계 및 UML 다이어그램 참조](#3-시스템-설계-및-uml-다이어그램-참조)
4. [GitHub 릴리스 및 업데이트 프로세스](#4-github-릴리스-및-업데이트-프로세스)
5. [개발 환경 및 유지보수 팁](#5-개발-환경-및-유지보수-팁)

---

## 1. 프로젝트 개요 및 구조

Image Optimizer는 정지 이미지와 움직이는 GIF(움짤)를 고화질을 유지하며 초경량 WebP/JPG로 변환하는 크로스 플랫폼 최적화 도구입니다.

### 🏛️ 아키텍처 원칙: 관심사 분리 (SoC)
* **Presentation Layer (UI/CLI)**: `main_gui.py` (PySide6/Tkinter GUI), `cli.py` (터미널 CLI 도구 `iopt`)
* **Core Engine (Business Logic)**: `converter_core.py` (Pillow 기반의 순수 변환 알고리즘, UI 종속성 없음)
* **Infrastructure**: `platform_adapter.py` (OS별 탐색기 열기 등 시스템 연동)

```text
img2webp/
├── main_gui.py              # 데스크톱 GUI 진입점 (드래그 앤 드롭, 실시간 대시보드)
├── cli.py                   # CLI 진입점 (iopt 명령어 인터페이스)
├── converter_core.py        # 핵심 변환 로직 (리사이징, 알파 처리, 인코딩)
├── platform_adapter.py      # 크로스 플랫폼 OS 어댑터
├── packaging/               # 배포용 리소스 (아이콘, 매니페스트)
└── docs/                    # 기술 문서 및 설계 다이어그램
    ├── README.md            # 본 문서
    └── diagrams/            # Diagrams as Code (PlantUML)
        ├── image_optimizer_class.wsd
        └── image_optimizer_sequence.wsd
```

---

## 2. 앱 주요 설정 및 기능 사용법

앱의 모든 변환 설정은 `converter_core.py`의 `ConversionOptions` 데이터 클래스로 캡슐화되어 GUI와 CLI에서 공통으로 사용됩니다.

### ⚙️ 핵심 설정 옵션 요약

| 설정 항목 | 선택 가능 값 | 기본값 | 설명 |
| :--- | :--- | :--- | :--- |
| **출력 포맷 (`output_formats`)** | `WEBP`, `JPG`, `둘 다(BOTH)` | `WEBP` | 고효율 WebP 또는 범용 JPG 선택 (동시 변환 지원) |
| **압축 품질 (`quality`)** | `1` ~ `100` | `90` | 시각적 화질 대비 용량 최적화 (80~90 권장) |
| **리사이즈 모드 (`resize_mode`)** | `none`, `max_width`, `scale_percent` | `none` | 원본 크기 유지, 최대 가로폭 제한, 비율(%) 축소 |
| **최대 가로폭 (`max_width`)** | 픽셀 단위 (예: `1920`, `2560`) | `1920` | `max_width` 모드 시 초과하는 이미지만 비율 유지 축소 |
| **비율 축소 (`scale_percent`)** | `1` ~ `100%` | `50` | `scale_percent` 모드 시 원본 크기를 지정 비율로 축소 |
| **알파 채널 (`remove_alpha`)** | `True` / `False` | `False` | `False`: 투명 배경 보존<br>`True`: 흰색 배경과 합성 후 RGB 변환 |
| **원본 파일 처리 (`delete_originals`)** | `True` / `False` | `False` | `True` 설정 시 변환 성공 후 **시스템 휴지통(Trash)**으로 안전 이동 |
| **저장 위치 (`output_mode`)** | `same`, `sub`, `custom` | `same` | 원본 폴더, 하위 폴더(`optimized/`), 지정 폴더 선택 |

### 🖥️ 실행 방법
* **GUI 모드**: `python main_gui.py` 실행 후 이미지를 창에 드래그 앤 드롭
* **CLI 모드**: `python cli.py [대상폴더/파일] -q 90 --format webp --resize-mode max_width --max-width 1920`

---

## 3. 시스템 설계 및 UML 다이어그램 참조

설계의 노후화를 방지하고 버전 추적이 가능하도록 **Diagrams as Code (DaC)** 방식으로 관리하고 있습니다.

### 📐 다이어그램 목록 (`docs/diagrams/`)
1. **[image_optimizer_class.wsd](diagrams/image_optimizer_class.wsd)**
   * **시스템 구조 및 클래스 다이어그램**
   * UI(`MainGUI`, `CLI`), 변환 코어(`ConverterCore`), 데이터 모델(`ConversionOptions`, `FileResult`), 외부 라이브러리(`Pillow`, `Send2Trash`) 간의 의존 관계 표현.
2. **[image_optimizer_sequence.wsd](diagrams/image_optimizer_sequence.wsd)**
   * **변환 처리 시퀀스 다이어그램**
   * 파일 드롭부터 EXIF 회전 보정, 알파 채널 분기, 리사이징, 다중 포맷 인코딩, 결과 통계 집계까지의 호출 흐름 표현.

### 💡 다이어그램 보는 방법 (VS Code)
1. VS Code에서 위의 `.wsd` 파일 중 하나를 엽니다.
2. 키보드 단축키 **`Alt + D`**를 누르면 우측 패널에 다이어그램이 즉시 렌더링됩니다.  
   *(온라인 PlantUML 렌더링 서버가 `.vscode/settings.json`에 사전 설정되어 있어 Java 설치 없이 즉시 작동합니다)*

---

## 4. GitHub 릴리스 및 업데이트 프로세스

새로운 기능 개발이나 버그 수정을 완료한 뒤 사용자가 최신 버전을 설치/업데이트할 수 있도록 배포하는 정식 파이프라인입니다.

```mermaid
flowchart LR
    A["코드 수정 & 테스트"] --> B["1. 버전 번호 갱신"]
    B --> C["2. Git 태그 생성 & 푸시"]
    C --> D["3. GitHub Actions 자동 빌드"]
    D --> E["4. GitHub Releases 바이너리 게시"]
    E --> F["5. 패키지 매니저 갱신\n(Winget, Homebrew, APT)"]
```

### 🚀 배포 단계별 상세 절차

#### Step 1. 버전 번호 갱신
새 릴리스 버전(예: `v1.0.5`)에 맞춰 관련 파일의 버전 문자열을 수정합니다:
* `cli.py`: `VERSION = "1.0.5"`
* `main_gui.py`: 상단 헤더 배지 버전 표기

#### Step 2. 변경사항 커밋 및 Git 태그 발행
```bash
# 1. 파일 변경 커밋 및 푸시
git add cli.py main_gui.py docs/
git commit -m "chore: release v1.0.5"
git push origin main

# 2. 릴리스 태그 생성 및 푸시 (자동 빌드 트리거)
git tag v1.0.5
git push origin v1.0.5
```

#### Step 3. GitHub Actions 자동 빌드
* 태그가 푸시되면 `.github/workflows/release.yml` 워크플로우가 자동으로 실행됩니다.
* 각 OS별 가상머신에서 실행 바이너리(`ImageOptimizer-windows-x64.exe`, `.dmg`, `.deb`)가 컴파일되어 GitHub Releases에 자동 업로드됩니다.

#### Step 4. 패키지 매니저 업데이트
* **Winget (Windows)**:
  1. 새 릴리스 `.exe`의 SHA-256 해시값 추출
  2. `microsoft/winget-pkgs` 공식 저장소 매니페스트 업데이트 제출
  *(상세 절차는 [private/WINGET_RELEASE_GUIDE.md](../private/WINGET_RELEASE_GUIDE.md) 참조)*
* **Homebrew (macOS)**: `build/homebrew/Casks/image-optimizer.rb` 버전 및 SHA-256 갱신
* **APT (Linux)**: 데비안 패키지 저장소 메타데이터 갱신

---

## 5. 개발 환경 및 유지보수 팁

* **가상환경 활성화**: 프로젝트 루트에서 권장 Python 버전(3.10+) 가상환경 사용
* **의존성 설치**: `pip install -r requirements.txt`
* **설계 준수 원칙**:
  * 비즈니스 로직(알파 채널 처리, 리사이즈, 이미지 저장 등)을 UI 파일(`main_gui.py`)에 직접 작성하지 마세요. 반드시 `converter_core.py`에 메서드를 정의하고 호출해야 합니다.
  * 새로운 옵션 파라미터가 필요할 경우 `ConversionOptions` 데이터 클래스에 기본값과 함께 필드를 추가하세요.
