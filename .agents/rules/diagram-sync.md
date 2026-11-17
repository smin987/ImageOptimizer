# Diagram-Code Sync Rule

## Mandatory Instruction
프로그램의 구조(클래스, 주요 메서드/인터페이스, 의존 관계, 비즈니스 흐름 등)를 수정하거나 추가/리팩토링할 경우, 반드시 아래 다이어그램 파일들을 즉시 검토하고 동기화하여 반영해야 합니다:

1. **`docs/diagrams/image_optimizer_class.wsd`**
   - 클래스 및 모듈의 속성, 메서드, 계층 구조, 의존 관계 변경 시 즉시 반영
2. **`docs/diagrams/image_optimizer_sequence.wsd`**
   - 변환 처리 흐름, 분기 조건, 비동기 호출 시퀀스 변경 시 즉시 반영
3. **`docs/README.md`**
   - 주요 파라미터(`ConversionOptions`)나 기능 명세 변경 시 설정 표 및 워크플로우 갱신

설계와 코드 간의 불일치(Documentation Drift)가 발생하지 않도록 코드를 수정할 때 위 다이어그램 파일들을 항상 동일한 작업 단위(커밋)에서 갱신하세요.
