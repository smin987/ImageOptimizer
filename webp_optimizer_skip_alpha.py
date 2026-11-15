import argparse
import os
from pathlib import Path
from typing import Optional

# ImageOps: 스마트폰 회전 방지, ImageSequence: GIF 프레임 순회
from PIL import Image, ImageOps, ImageSequence

# ================= 설정 구간 =================
# 변환할 원본 이미지가 있는 폴더
INPUT_FOLDER = "./input_images"

# 최적화된 이미지를 저장할 폴더
OUTPUT_FOLDER = "./output_images"

# ★ 출력 포맷 선택 ("WEBP", "JPG", "BOTH")
#   - "WEBP" : WebP 포맷으로만 출력 (.webp)
#   - "JPG"  : JPG 포맷으로만 출력 (.jpg)
#   - "BOTH" : WebP와 JPG 둘 다 동시에 출력 (.webp & .jpg)
OUTPUT_FORMAT = "WEBP"
# OUTPUT_FORMAT = "JPG"

# 웹용 최대 가로 해상도 (원본이 이보다 크면 축소, 작으면 원본 크기 유지)
MAX_WIDTH = 1920

# 압축 품질 (1~100 사이, 80~85가 화질 대비 용량 최적화 권장 수치)
QUALITY = 90

# 처리할 이미지 확장자 목록 (.gif 포함)
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"}

# ★ 알파 채널(투명도) 유지 여부 — 이 버전의 핵심
#   True (기본): 알파 채널이 있는 파일은 변환하지 않고 건너뛰며, 원본은 그대로 보존
#                → 스킵 기준은 아래 SKIP_ONLY_REAL_ALPHA로 조정
#   False      : 알파가 있는 파일도 전부 변환
#                → 실제 투명 픽셀은 FLATTEN_BACKGROUND에 합성, 불투명은 무손실 RGB 변환
#                → 이때는 스킵이 없으므로 SKIP_ONLY_REAL_ALPHA는 무시됨
KEEP_ALPHA = True
# KEEP_ALPHA = False

# 스킵 기준 (KEEP_ALPHA=True일 때만 적용)
#   False (기본): 알파 채널이 있기만 하면(RGBA/LA/P-투명) 전부 스킵
#                 → 화면 전체를 채우는 불투명 RGBA 사진도 스킵
#   True        : 실제 투명 픽셀이 있을 때만 스킵
#                 → 알파 채널이 있어도 전부 불투명이면 무손실 RGB 변환 후 WebP 저장
SKIP_ONLY_REAL_ALPHA = False

# KEEP_ALPHA=False일 때 투명 픽셀을 합성할 배경색 (R, G, B)
FLATTEN_BACKGROUND = (255, 255, 255)

# ★ 최적화 완료 후 원본 이미지 삭제 여부 (True: 삭제, False: 보존)
#   ※ 알파로 건너뛴 파일(KEEP_ALPHA=True)은 이 값과 무관하게 절대 삭제되지 않습니다.
DELETE_ORIGINALS = True
# ============================================


def open_folder(path: Path):
    """
    윈도우에서는 탐색기를 열고, 리눅스/맥 등 지원하지 않는 환경에서는 에러 없이 건너뜁니다.
    """
    if hasattr(os, "startfile"):
        os.startfile(path.resolve())


def format_bytes(size_bytes):
    """바이트 크기를 KB/MB 단위로 변환"""
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"


def flatten_alpha(img):
    """
    알파 채널을 제거하고 RGB로 변환합니다 (KEEP_ALPHA=False 경로).

    - 완전 불투명한 알파: 단순 RGB 변환 (화질 무손실, 최단 경로)
    - 실제 투명 픽셀 존재: FLATTEN_BACKGROUND 배경색 위에 합성

    반환: (RGB 이미지, 실제 투명 픽셀이 있었는지 여부)
    """
    if img.mode == "P" and "transparency" in img.info:
        img = img.convert("RGBA")

    if img.mode in ("RGBA", "LA"):
        rgba = img.convert("RGBA")
        alpha_min, _ = rgba.getchannel("A").getextrema()
        if alpha_min == 255:
            # 알파가 형식적으로만 존재(전부 불투명) → 단순 RGB 변환
            return rgba.convert("RGB"), False
        bg = Image.new("RGB", rgba.size, FLATTEN_BACKGROUND)
        bg.paste(rgba, mask=rgba.getchannel("A"))
        return bg, True

    return img.convert("RGB"), False


def has_alpha(img, real_only):
    """
    단일 이미지(또는 프레임)에 알파가 있는지 검사.

    - real_only=False: 알파 채널 자체가 있으면 True
    - real_only=True : 실제 투명 픽셀(알파 < 255)이 있을 때만 True
    """
    if img.mode in ("RGBA", "LA"):
        if not real_only:
            return True
        alpha_min, _ = img.convert("RGBA").getchannel("A").getextrema()
        return alpha_min < 255

    if img.mode == "P" and "transparency" in img.info:
        if not real_only:
            return True
        # 투명 팔레트 인덱스가 실제 픽셀에 사용됐는지 확인
        alpha_min, _ = img.convert("RGBA").getchannel("A").getextrema()
        return alpha_min < 255

    return False


def has_alpha_any_frame(img, real_only):
    """애니메이션: 하나의 프레임이라도 알파가 있으면 GIF 전체를 알파 파일로 판정"""
    for frame in ImageSequence.Iterator(img):
        if has_alpha(frame, real_only):
            return True
    return False


def resolve_target_formats(format_choice: Optional[str] = None):
    """
    포맷 설정 문자열을 정규화하여 처리할 포맷 목록을 반환합니다.
    - 'WEBP' -> ['WEBP']
    - 'JPG' 또는 'JPEG' -> ['JPG']
    - 'BOTH' 또는 'ALL' -> ['WEBP', 'JPG']
    """
    choice = (format_choice or "WEBP").strip().upper()
    if choice == "WEBP":
        return ["WEBP"]
    elif choice in ("JPG", "JPEG"):
        return ["JPG"]
    elif choice in ("BOTH", "ALL"):
        return ["WEBP", "JPG"]
    else:
        raise ValueError(
            f"지원하지 않는 포맷 설정입니다: '{format_choice}'. "
            "('WEBP', 'JPG', 'BOTH' 중 하나를 선택해주세요.)"
        )


def prepare_static_image(img):
    """일반 정지 이미지의 회전 메타데이터 적용, 색상 모드 변환, 가로 해상도 리사이징 수행"""
    # 1. 스마트폰 카메라 회전 메타데이터 자동 적용
    img = ImageOps.exif_transpose(img)

    # 2. 색상 모드 변환 (KEEP_ALPHA 플래그에 따름)
    note = None
    if KEEP_ALPHA:
        # 알파 파일은 사전 스킵되므로 여기 도달한 이미지에는 알파가 없음
        if img.mode != "RGB":
            img = img.convert("RGB")
    else:
        img, had_real_alpha = flatten_alpha(img)
        if had_real_alpha:
            note = "알파 제거→흰 배경"

    # JPG/WebP 공통: RGB 모드 보장
    if img.mode != "RGB":
        img = img.convert("RGB")

    # 3. 가로 해상도 리사이징
    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / float(img.width)
        new_height = int(float(img.height) * float(ratio))
        img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)

    return img, note


def save_static_image(img, out_file, fmt="WEBP"):
    """전처리된 정지 이미지를 지정 포맷(WEBP 또는 JPG)으로 저장"""
    save_fmt = "JPEG" if fmt.upper() in ("JPG", "JPEG") else "WEBP"
    img.save(out_file, format=save_fmt, quality=QUALITY, optimize=True)


def process_image(img, out_file, fmt="WEBP"):
    """일반 정지 이미지 처리 및 저장. 알파 처리 결과 문자열을 반환 (단일 호출 호환용)"""
    processed_img, note = prepare_static_image(img)
    save_static_image(processed_img, out_file, fmt)
    return note


def process_animated_gif(img, out_file):
    """
    움직이는 GIF의 모든 프레임을 유지하며 애니메이션 WebP로 저장.
    - KEEP_ALPHA=True : 알파 GIF는 사전 스킵되므로 무투명 GIF만 도달 (프레임 RGB 변환)
    - KEEP_ALPHA=False: 투명 프레임은 FLATTEN_BACKGROUND에 합성 후 RGB 변환
    ※ 애니메이션 WebP는 규격상 확장 컨테이너(VP8X)가 필수입니다.
    반환: (프레임 수, 알파 처리 결과 문자열)
    """
    frames = []
    durations = []
    had_real_alpha = False

    # 모든 프레임 순회
    for frame in ImageSequence.Iterator(img):
        f = frame.copy()

        if KEEP_ALPHA:
            f = f.convert("RGB")
        else:
            f, frame_alpha = flatten_alpha(f)
            had_real_alpha = had_real_alpha or frame_alpha

        # 프레임별 리사이징
        if f.width > MAX_WIDTH:
            ratio = MAX_WIDTH / float(f.width)
            new_height = int(float(f.height) * float(ratio))
            f = f.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)

        frames.append(f)
        durations.append(frame.info.get("duration", 100))

    # 첫 프레임 뒤에 나머지 프레임을 덧붙여서 WebP로 일괄 저장
    frames[0].save(
        out_file,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=img.info.get("loop", 0),
        quality=QUALITY,
        optimize=True,
    )

    note = "알파 제거→흰 배경" if (not KEEP_ALPHA and had_real_alpha) else None
    return len(frames), note


def process_animated_gif_to_jpg(img, out_file):
    """
    움직이는 GIF의 첫 번째 프레임을 추출하여 JPG로 저장.
    (JPG는 애니메이션을 지원하지 않으므로 첫 프레임 정지 이미지로 변환)
    반환: 알파 처리 결과 문자열
    """
    first_frame = next(ImageSequence.Iterator(img)).copy()
    first_frame = ImageOps.exif_transpose(first_frame)

    note = None
    if KEEP_ALPHA:
        if first_frame.mode != "RGB":
            first_frame = first_frame.convert("RGB")
    else:
        first_frame, had_real_alpha = flatten_alpha(first_frame)
        if had_real_alpha:
            note = "알파 제거→흰 배경"

    if first_frame.mode != "RGB":
        first_frame = first_frame.convert("RGB")

    if first_frame.width > MAX_WIDTH:
        ratio = MAX_WIDTH / float(first_frame.width)
        new_height = int(float(first_frame.height) * float(ratio))
        first_frame = first_frame.resize(
            (MAX_WIDTH, new_height), Image.Resampling.LANCZOS
        )

    first_frame.save(out_file, format="JPEG", quality=QUALITY, optimize=True)
    return note


def should_skip_for_alpha(img, is_animated: bool) -> bool:
    """KEEP_ALPHA=True일 때 이미지에 알파 채널/투명도가 포함되어 있는지 확인"""
    if not KEEP_ALPHA:
        return False
    if is_animated:
        return has_alpha_any_frame(img, SKIP_ONLY_REAL_ALPHA)
    return has_alpha(img, SKIP_ONLY_REAL_ALPHA)


def convert_animated_formats(
    img, file_stem: str, output_path: Path, target_formats: list
):
    """애니메이션 GIF를 각 대상 포맷으로 변환"""
    created_files = {}
    tags = []
    note = None

    for fmt in target_formats:
        ext = ".jpg" if fmt == "JPG" else ".webp"
        out_file = output_path / f"{file_stem}{ext}"
        if fmt == "WEBP":
            frame_count, n = process_animated_gif(img, out_file)
            tags.append(f"WebP({frame_count}프레임)")
        else:
            n = process_animated_gif_to_jpg(img, out_file)
            tags.append("JPG(첫 프레임)")
        if n:
            note = n
        created_files[fmt] = out_file

    tag = f"[GIF 애니메이션: {', '.join(tags)}]"
    if note:
        tag += f" [{note}]"
    return created_files, tag


def convert_static_formats(
    img, file_stem: str, output_path: Path, target_formats: list
):
    """일반 정지 이미지를 각 대상 포맷으로 변환"""
    created_files = {}
    processed_img, note = prepare_static_image(img)

    for fmt in target_formats:
        ext = ".jpg" if fmt == "JPG" else ".webp"
        out_file = output_path / f"{file_stem}{ext}"
        save_static_image(processed_img, out_file, fmt)
        created_files[fmt] = out_file

    tag = f"[정지 이미지 -> {', '.join(target_formats)}]"
    if note:
        tag += f" [{note}]"
    return created_files, tag


def convert_image_formats(
    img, file_stem: str, output_path: Path, target_formats: list, is_animated: bool
):
    """애니메이션 여부에 따라 알맞은 포맷 변환 함수 호출"""
    if is_animated:
        return convert_animated_formats(img, file_stem, output_path, target_formats)
    return convert_static_formats(img, file_stem, output_path, target_formats)


def finalize_processed_file(file: Path, orig_size: int, created_files: dict, tag: str):
    """결과 파일 정상 생성 검증, 콘솔 결과 출력 및 원본 삭제 수행"""
    sizes = {}
    for fmt, out_file in created_files.items():
        if not out_file.exists() or out_file.stat().st_size == 0:
            raise RuntimeError(
                f"{fmt} 결과 파일이 비정상적으로 생성되었습니다: {out_file.name}"
            )
        sizes[fmt] = out_file.stat().st_size

    print(f"[완료] {file.name} {tag}")
    if len(sizes) == 1:
        _, new_size = next(iter(sizes.items()))
        reduction = (1 - (new_size / orig_size)) * 100
        print(
            f"       {format_bytes(orig_size)} -> {format_bytes(new_size)} ({reduction:.1f}% 절감)"
        )
    else:
        print(f"       원본: {format_bytes(orig_size)}")
        for fmt, new_size in sizes.items():
            reduction = (1 - (new_size / orig_size)) * 100
            print(
                f"       -> {fmt:4s}: {format_bytes(new_size)} ({reduction:.1f}% 절감)"
            )

    if DELETE_ORIGINALS:
        file.unlink()
        print(f"       🗑️ 원본 삭제: {file.name}")

    return orig_size, sizes


def process_single_file(file: Path, output_path: Path, target_formats: list):
    """
    파일 1개를 처리하여 target_formats 목록의 포맷들로 저장합니다.
    KEEP_ALPHA=True에서 알파 포함 시 None을 반환해 건너뜁니다 (원본 보존).
    반환: (orig_size, {fmt: new_size})
    """
    orig_size = file.stat().st_size
    if orig_size == 0:
        raise ValueError("빈 파일(0 바이트)입니다.")

    with Image.open(file) as img:
        is_animated = getattr(img, "is_animated", False)
        if should_skip_for_alpha(img, is_animated):
            return None

        created_files, tag = convert_image_formats(
            img, file.stem, output_path, target_formats, is_animated
        )

    return finalize_processed_file(file, orig_size, created_files, tag)


def collect_input_files(input_path: Path) -> list[Path]:
    """입력 폴더에서 지원하는 확장자의 파일 목록을 수집합니다."""
    if not input_path.exists():
        return []
    return [f for f in input_path.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS]


def print_start_banner(file_count: int, target_formats: list[str]):
    """배치 작업 시작 안내 문구를 출력합니다."""
    mode_desc = (
        f"알파 파일 스킵, SKIP_ONLY_REAL_ALPHA={SKIP_ONLY_REAL_ALPHA}"
        if KEEP_ALPHA
        else "전체 변환(알파 제거)"
    )
    formats_desc = ", ".join(target_formats)
    print(
        f"총 {file_count}개의 파일 최적화를 시작합니다... "
        f"(출력 포맷: {formats_desc}, KEEP_ALPHA={KEEP_ALPHA}, {mode_desc})"
    )
    if DELETE_ORIGINALS:
        print("※ [주의] 변환 성공 파일의 원본이 영구 삭제됩니다 (건너뛴 파일 제외).")
    print("=" * 55)


def process_batch(files: list[Path], output_path: Path, target_formats: list[str]):
    """파일 목록을 순회하며 변환을 수행하고 집계 결과를 반환합니다."""
    total_orig_size = 0
    total_sizes_by_fmt = dict.fromkeys(target_formats, 0)
    success_count = 0
    skipped_files = []

    for file in files:
        try:
            result = process_single_file(file, output_path, target_formats)
            if result is None:
                skipped_files.append(file.name)
                print(f"[건너뜀] {file.name} (알파 채널 포함, 원본 보존)")
                continue

            orig_size, sizes = result
            total_orig_size += orig_size
            for fmt, size in sizes.items():
                total_sizes_by_fmt[fmt] += size
            success_count += 1
        except Exception as e:
            print(f"[오류] {file.name} 처리 중 에러 (원본 유지): {e}")

    return success_count, skipped_files, total_orig_size, total_sizes_by_fmt


def print_optimization_summary(
    total_files: int,
    target_formats: list[str],
    success_count: int,
    skipped_files: list[str],
    total_orig_size: int,
    total_sizes_by_fmt: dict,
):
    """최종 최적화 결과 요약을 출력합니다."""
    print("=" * 55)
    print(
        f"변환 완료: {success_count}/{total_files} 개 (건너뜀: {len(skipped_files)}개)"
    )
    if skipped_files:
        print("건너뛴 파일 (알파 포함, 원본 보존):")
        for name in skipped_files:
            print(f"  - {name}")

    if total_orig_size <= 0:
        return

    if len(target_formats) == 1:
        fmt = target_formats[0]
        fmt_size = total_sizes_by_fmt[fmt]
        reduction = (1 - (fmt_size / total_orig_size)) * 100
        print(f"총 용량: {format_bytes(total_orig_size)} -> {format_bytes(fmt_size)}")
        print(f"총 절감률: {reduction:.1f}% 절약됨")
    else:
        print(f"총 원본 용량: {format_bytes(total_orig_size)}")
        for fmt in target_formats:
            fmt_size = total_sizes_by_fmt[fmt]
            reduction = (1 - (fmt_size / total_orig_size)) * 100
            print(
                f"- {fmt:4s} 총 용량: {format_bytes(fmt_size)} ({reduction:.1f}% 절약)"
            )


def optimize_images(format_choice: Optional[str] = None):
    """전체 파일 최적화 총괄 함수"""
    target_formats = resolve_target_formats(format_choice or OUTPUT_FORMAT)

    input_path = Path(INPUT_FOLDER)
    output_path = Path(OUTPUT_FOLDER)
    output_path.mkdir(parents=True, exist_ok=True)

    files = collect_input_files(input_path)
    if not files:
        print(f"[{INPUT_FOLDER}] 폴더에 처리할 이미지가 없습니다.")
        return

    print_start_banner(len(files), target_formats)
    stats = process_batch(files, output_path, target_formats)
    print_optimization_summary(len(files), target_formats, *stats)

    # 윈도우 환경에서만 탐색기로 열기 (subprocess 없이 동작)
    open_folder(output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="이미지 최적화 변환 도구 (WebP / JPG)")
    parser.add_argument(
        "--format",
        "-f",
        choices=["WEBP", "JPG", "BOTH"],
        type=str.upper,
        default=OUTPUT_FORMAT,
        help=f"출력 포맷 선택: WEBP, JPG, BOTH (기본값: {OUTPUT_FORMAT})",
    )
    args = parser.parse_args()
    optimize_images(format_choice=args.format)
