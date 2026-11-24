# 🤝 Image Optimizer 기여 가이드라인 (Contributing Guidelines)

Image Optimizer 프로젝트에 관심을 가져주셔서 감사합니다! 버그 리포트, 기능 제안, 문서 보완, 코드 기여(Pull Request) 등 모든 기여를 환영합니다.

---

## 📜 기여자 라이선스 계약 (Contributor License Agreement, CLA)

Image Optimizer는 **Source-Available Freeware (공정 이용 무료 소프트웨어)** 모델로 운영되며, 향후 프로젝트의 지속 가능성과 기업용 기능 지원을 위해 **듀얼 라이선스(Dual-Licensing) 또는 상용 Pro/Enterprise 에디션**으로 확장될 수 있습니다.

따라서 타인의 기여(PR)가 코드베이스에 포함된 이후에도 법적 분쟁 없이 프로젝트를 원활하게 발전시키고 상용/듀얼 라이선스 버전을 제공할 수 있도록, **모든 기여자는 풀 리퀘스트(Pull Request) 제출 시 아래 조항에 동의하는 것으로 간주**됩니다.

### 1. 라이선스 부여 및 상용 재라이선싱 동의
> **국문 요약**:
> 본 프로젝트에 풀 리퀘스트(PR), 패치, 코드를 제출함으로써, 기여자는 프로젝트 관리자(smin987)에게 제출된 기여물에 대한 **영구적(perpetual), 전 세계적(worldwide), 비독점적(non-exclusive), 로열티 없는(royalty-free) 사용, 수정, 복제, 배포 및 재라이선싱 권한**을 부여합니다.
> 프로젝트 관리자는 기여된 코드를 현재의 무료 버전뿐만 아니라 **향후 상용 라이선스(Commercial License), 듀얼 라이선스, BSL, 유료 Pro/Enterprise 에디션에 포함하여 배포하고 수익화할 수 있는 완전한 권한**을 가집니다.

### 2. Contributor License Terms (English)
> By submitting a Pull Request, patch, or contribution to this repository, you agree to the following terms:
> 1. **Grant of Rights**: You grant the Author/Project Maintainer (smin987) a perpetual, worldwide, non-exclusive, royalty-free, irrevocable copyright license to reproduce, prepare derivative works of, publicly display, sublicense, and distribute your contributions and such derivative works.
> 2. **Commercial & Dual-Licensing Authorization**: You expressly acknowledge and agree that the Author retains the unrestricted right to include your contributions in future commercial editions, dual-licensed offerings (e.g., Commercial EULA, BSL, Open Core, or Paid Pro/Enterprise versions), and to relicense or monetize the software without requiring separate approval or compensation.
> 3. **Original Work Representation**: You represent that each of your contributions is your original creation, and that you have the full legal right to grant the rights described above.

---

## 🚀 기여 절차 및 방법

### 1. 이슈(Issue) 등록
- 새로운 기능 제안이나 대규모 변경 작업 전에는 먼저 [GitHub Issues](https://github.com/smin987/ImageOptimizer/issues)를 등록하여 방향성을 논의해 주세요.
- 버그를 제보할 때는 OS 환경(Windows/macOS/Linux), 문제 발생 이미지 포맷, 재현 단계를 상세히 적어주세요.

### 2. 풀 리퀘스트(Pull Request) 생성
1. 저장소를 Fork하고 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`).
2. 변경 사항을 커밋합니다. (커밋 메시지는 Conventional Commits 규격을 권장합니다: `feat:`, `fix:`, `docs:`, `test:` 등).
3. 기존 단위 테스트를 실행하여 모든 테스트가 통과하는지 확인합니다:
   ```bash
   python -m unittest tests/test_converter_core.py
   ```
4. PR 템플릿의 **기여자 라이선스 동의(CLA)** 체크박스를 확인 및 체크한 후 PR을 제출합니다.

---

## 💡 개발 및 코딩 컨벤션
- 파이썬 3.10+ 표준 문법을 준수합니다.
- GUI는 `PySide6`를 기준으로 작성하며, 코어 변환 로직(`converter_core.py`)과 UI 로직(`main_gui.py`)을 엄격히 분리합니다.
- 새로운 포맷이나 압축 옵션을 추가할 때는 반드시 `tests/` 디렉터리에 대응하는 단위 테스트를 추가해 주세요.
