"""
이미지 및 애니메이션 WebP/JPG 최적화 변환 코어 엔진
GUI 및 CLI에서 공통으로 재사용 가능한 비즈니스 로직 모듈
"""

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Callable, Optional

from PIL import Image, ImageOps, ImageSequence
import send2trash

# 8K 및 초대형 이미지 처리를 위해 Pillow의 픽셀 제한 해제 (DecompressionBomb 방지)
Image.MAX_IMAGE_PIXELS = None

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"}

# 인플루언서 / SNS 크리에이터 맞춤 권장 해상도 규격 (2026 최신 표준)
SNS_PRESETS = {
    "youtube_thumb": {"width": 1280, "height": 720, "label": "YouTube Thumbnail (16:9)"},
    "youtube_shorts": {"width": 1080, "height": 1920, "label": "YouTube Shorts / Reels (9:16)"},
    "insta_feed": {"width": 1080, "height": 1080, "label": "Instagram Square Feed (1:1)"},
    "insta_portrait": {"width": 1080, "height": 1350, "label": "Instagram Portrait Feed (4:5)"},
    "insta_story": {"width": 1080, "height": 1920, "label": "Instagram Story / Reels (9:16)"},
    "blog_content": {"width": 1200, "height": None, "label": "Blog Content Width (1200px)"},
    "blog_thumb": {"width": 1080, "height": 1080, "label": "Blog Cover (1:1)"},
    "x_feed": {"width": 1200, "height": 675, "label": "X / Threads Feed (16:9)"},
}
SNS_PRESET_KEYS = list(SNS_PRESETS.keys())
SNS_CROP_MODE_KEYS = ["fit", "contain", "cover"]


@dataclass
class ConversionOptions:
    """변환 파라미터 설정 데이터 클래스"""

    output_formats: list[str] = field(default_factory=lambda: ["WEBP"])  # "WEBP", "JPG", 또는 둘 다
    quality: int = 90  # 1~100
    resize_mode: str = "none"  # 기본값: "none" (원본 크기 유지). 선택 가능: "max_width", "scale_percent", "sns_preset", "none"
    max_width: int = 1920  # resize_mode == "max_width"일 때 가로폭 제한
    scale_percent: int = 50  # resize_mode == "scale_percent"일 때 축소 비율 (1~100%)
    # 인플루언서 / SNS 맞춤 프리셋 설정 (resize_mode == "sns_preset")
    sns_preset_target: str = "youtube_thumb"  # SNS_PRESETS 키값
    sns_crop_mode: str = "fit"  # 기본값: "fit"(비율유지 - 잘림 없음), "contain"(빈공간 흰색 레터박스), "cover"(스마트 중앙 맞춤)
    remove_alpha: bool = False  # True: 투명 배경 제거(흰색 배경 합성), False(기본): 투명 배경(Alpha) 그대로 보존
    keep_alpha: bool = False  # 하위 호환용 (사용되지 않음)
    skip_only_real_alpha: bool = False  # 실제 투명 픽셀 존재 시에만 스킵
    flatten_background: tuple[int, int, int] = (255, 255, 255)  # 알파 제거 시 배경색
    delete_originals: bool = False  # 원본 파일 휴지통 이동 여부
    output_mode: str = "same"  # 'same': 원본 폴더, 'sub': 하위 폴더, 'custom': 지정 폴더
    custom_output_dir: Optional[Path] = None
    subfolder_name: str = "optimized"


@dataclass
class FileResult:
    """단일 파일 변환 결과 정보"""

    file_path: Path
    status: str  # "success", "skipped", "error"
    tag: str = ""
    orig_size: int = 0
    new_sizes: dict[str, int] = field(default_factory=dict)
    note: Optional[str] = None
    error_message: Optional[str] = None


def format_bytes(size_bytes: int) -> str:
    """바이트 크기를 KB/MB 단위 문자열로 변환"""
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"


def flatten_alpha(img: Image.Image, bg_color: tuple[int, int, int]):
    """알파 채널을 제거하고 지정된 배경색 위에 합성하여 RGB로 변환"""
    if img.mode == "P" and "transparency" in img.info:
        img = img.convert("RGBA")

    if img.mode in ("RGBA", "LA"):
        rgba = img.convert("RGBA")
        alpha_channel = rgba.getchannel("A")
        alpha_min, _ = alpha_channel.getextrema()
        if alpha_min == 255:
            return rgba.convert("RGB"), False
        bg = Image.new("RGB", rgba.size, bg_color)
        bg.paste(rgba, mask=alpha_channel)
        return bg, True

    return img.convert("RGB"), False


def has_alpha(img: Image.Image, real_only: bool) -> bool:
    """단일 프레임의 알파 채널 존재 여부 판별"""
    if img.mode in ("RGBA", "LA"):
        if not real_only:
            return True
        alpha_min, _ = img.convert("RGBA").getchannel("A").getextrema()
        return alpha_min < 255

    if img.mode == "P" and "transparency" in img.info:
        if not real_only:
            return True
        alpha_min, _ = img.convert("RGBA").getchannel("A").getextrema()
        return alpha_min < 255

    return False


def has_alpha_any_frame(img: Image.Image, real_only: bool) -> bool:
    """애니메이션 프레임 중 하나라도 알파가 있는지 판별"""
    for frame in ImageSequence.Iterator(img):
        if has_alpha(frame, real_only):
            return True
    return False


def should_skip_for_alpha(img: Image.Image, is_animated: bool, options: ConversionOptions) -> bool:
    """설정에 따라 알파 채널을 이유로 스킵해야 하는지 확인 (변환 모드에서는 스킵하지 않음)"""
    return False


def apply_resize(img: Image.Image, options: ConversionOptions) -> Image.Image:
    """옵션에 설정된 리사이즈 모드에 따라 이미지 해상도 조정"""
    if options.resize_mode == "scale_percent":
        # 비율(%) 축소: 1~99%일 때 비율 축소 적용
        if 0 < options.scale_percent < 100:
            scale = options.scale_percent / 100.0
            new_width = max(1, int(img.width * scale))
            new_height = max(1, int(img.height * scale))
            return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return img

    elif options.resize_mode == "max_width":
        # 최대 가로폭 기준 축소 (가로폭 초과 시에만 비율 유지 축소)
        if options.max_width > 0 and img.width > options.max_width:
            ratio = options.max_width / float(img.width)
            new_height = max(1, int(float(img.height) * float(ratio)))
            return img.resize((options.max_width, new_height), Image.Resampling.LANCZOS)
        return img

    elif options.resize_mode == "sns_preset":
        # 인플루언서 / SNS 맞춤 프리셋 규격 적용
        preset_info = SNS_PRESETS.get(options.sns_preset_target, SNS_PRESETS["youtube_thumb"])
        target_w = preset_info["width"]
        target_h = preset_info["height"]

        # 1. 가로폭만 지정된 프리셋 (예: blog_content 가로 1200px)
        if target_h is None:
            if target_w and img.width > target_w:
                ratio = target_w / float(img.width)
                new_h = max(1, int(float(img.height) * float(ratio)))
                return img.resize((target_w, new_h), Image.Resampling.LANCZOS)
            return img

        # 이미 목표 해상도와 정확히 일치하는 경우 추가 연산 없이 원본 그대로 보존
        if (img.width, img.height) == (target_w, target_h):
            return img

        # 2. 가로/세로 고정 규격 (유튜브 썸네일, 인스타 피드/릴스 등)
        crop_mode = options.sns_crop_mode

        if crop_mode == "fit":
            # 비율유지 (기본값: 잘림 없음, 여백 없음, 원본 비율 그대로 목표 박스에 축소)
            return ImageOps.contain(img, (target_w, target_h), method=Image.Resampling.LANCZOS)

        elif crop_mode == "contain":
            # 빈공간 흰색 레터박스 (잘림 없음, 여백 채우기)
            contained = ImageOps.contain(img, (target_w, target_h), method=Image.Resampling.LANCZOS)
            if img.mode in ("RGBA", "LA"):
                canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
                canvas.paste(contained, ((target_w - contained.width) // 2, (target_h - contained.height) // 2))
                return canvas
            else:
                bg_color = options.flatten_background if options.remove_alpha else (255, 255, 255)
                canvas = Image.new("RGB", (target_w, target_h), bg_color)
                canvas.paste(contained, ((target_w - contained.width) // 2, (target_h - contained.height) // 2))
                return canvas

        elif crop_mode == "cover":
            # 스마트 중앙 맞춤 (화면 꽉 채우기, 잘림 발생)
            return ImageOps.fit(img, (target_w, target_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

        # 기본 fallback: 비율유지 (잘림 없음)
        return ImageOps.contain(img, (target_w, target_h), method=Image.Resampling.LANCZOS)

    # "none" 또는 그 외: 원본 해상도 유지
    return img


def prepare_static_image(img: Image.Image, options: ConversionOptions):
    """일반 정지 이미지 회전 보정, 색상 변환(투명도 보존 or 알파 제거), 해상도 리사이즈 수행"""
    img = ImageOps.exif_transpose(img)
    note = None

    if options.remove_alpha:
        # 사용자가 '투명 배경 제거'를 체크한 경우 -> 흰색 배경으로 합성
        img, had_real_alpha = flatten_alpha(img, options.flatten_background)
        if had_real_alpha:
            note = "알파 제거(흰색 배경 합성)"
        if img.mode != "RGB":
            img = img.convert("RGB")
    else:
        # 기본값: 투명 배경(Alpha Channel) 보존
        if has_alpha(img, real_only=False):
            img = img.convert("RGBA")
            note = "투명 배경(Alpha) 보존"
        elif img.mode != "RGB":
            img = img.convert("RGB")

    img = apply_resize(img, options)
    return img, note


def save_static_image(img: Image.Image, out_file: Path, fmt: str, options: ConversionOptions):
    """전처리된 정지 이미지를 WebP(투명도 보존) 또는 JPEG(배경 합성)로 저장"""
    save_fmt = "JPEG" if fmt.upper() in ("JPG", "JPEG") else "WEBP"
    if save_fmt == "JPEG" and img.mode in ("RGBA", "LA"):
        # JPEG 규격은 알파 채널을 지원하지 않으므로 흰색 배경 합성 후 저장
        jpg_img, _ = flatten_alpha(img, options.flatten_background)
        jpg_img.save(out_file, format="JPEG", quality=options.quality, optimize=True)
    else:
        img.save(out_file, format=save_fmt, quality=options.quality, optimize=True)


def process_animated_gif_to_webp(img: Image.Image, out_file: Path, options: ConversionOptions):
    """움직이는 GIF의 모든 프레임을 유지하며 애니메이션 WebP로 저장 (투명 배경 보존 지원)"""
    frames = []
    durations = []
    had_real_alpha = False

    for frame in ImageSequence.Iterator(img):
        f = frame.copy()
        if options.remove_alpha:
            f, frame_alpha = flatten_alpha(f, options.flatten_background)
            had_real_alpha = had_real_alpha or frame_alpha
        else:
            if has_alpha(f, real_only=False):
                f = f.convert("RGBA")
                had_real_alpha = True
            elif f.mode != "RGB":
                f = f.convert("RGB")

        f = apply_resize(f, options)
        frames.append(f)
        durations.append(frame.info.get("duration", 100))

    frames[0].save(
        out_file,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=img.info.get("loop", 0),
        quality=options.quality,
        optimize=True,
    )

    if options.remove_alpha and had_real_alpha:
        note = "알파 제거(흰색 배경 합성)"
    elif (not options.remove_alpha) and had_real_alpha:
        note = "투명 애니메이션 WebP"
    else:
        note = None
    return len(frames), note


def process_animated_gif_to_jpg(img: Image.Image, out_file: Path, options: ConversionOptions):
    """움직이는 GIF의 첫 프레임을 추출하여 정지 이미지 JPG로 저장 (배경 합성)"""
    first_frame = next(ImageSequence.Iterator(img)).copy()
    first_frame = ImageOps.exif_transpose(first_frame)
    first_frame, had_real_alpha = flatten_alpha(first_frame, options.flatten_background)
    first_frame = apply_resize(first_frame, options)
    first_frame.save(out_file, format="JPEG", quality=options.quality, optimize=True)
    note = "알파 제거(흰색 배경 합성)" if had_real_alpha else None
    return note


def determine_output_dir(file_path: Path, options: ConversionOptions) -> Path:
    """옵션에 따라 파일이 저장될 출력 디렉토리 경로 계산"""
    if options.output_mode == "custom" and options.custom_output_dir:
        out_dir = Path(options.custom_output_dir)
    elif options.output_mode == "sub":
        out_dir = file_path.parent / options.subfolder_name
    else:  # "same"
        out_dir = file_path.parent

    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def process_single_file(file_path: Path, options: ConversionOptions) -> FileResult:
    """단일 파일에 대해 변환 및 검증, 원본 안전 삭제(옵션)를 수행"""
    orig_size = file_path.stat().st_size
    if orig_size == 0:
        return FileResult(
            file_path=file_path,
            status="error",
            error_message="빈 파일(0 바이트)입니다.",
        )

    out_dir = determine_output_dir(file_path, options)

    with Image.open(file_path) as img:
        is_animated = getattr(img, "is_animated", False)

        if should_skip_for_alpha(img, is_animated, options):
            return FileResult(
                file_path=file_path,
                status="skipped",
                orig_size=orig_size,
                tag="[알파 포함 건너뜀]",
                note="알파 채널 포함(원본 보존)",
            )

        created_files: dict[str, Path] = {}

        if is_animated:
            tags = []
            note = None
            for fmt in options.output_formats:
                ext = ".jpg" if fmt == "JPG" else ".webp"
                out_file = out_dir / f"{file_path.stem}{ext}"
                if fmt == "WEBP":
                    frame_count, n = process_animated_gif_to_webp(img, out_file, options)
                    tags.append(f"WebP({frame_count}프레임)")
                else:  # JPG
                    n = process_animated_gif_to_jpg(img, out_file, options)
                    tags.append("JPG(첫 프레임)")
                if n:
                    note = n
                created_files[fmt] = out_file
            tag = f"[GIF 애니메이션: {', '.join(tags)}]"
        else:
            processed_img, note = prepare_static_image(img, options)
            for fmt in options.output_formats:
                ext = ".jpg" if fmt == "JPG" else ".webp"
                out_file = out_dir / f"{file_path.stem}{ext}"
                save_static_image(processed_img, out_file, fmt, options)
                created_files[fmt] = out_file
            tag = f"[정지 이미지 -> {', '.join(options.output_formats)}]"

    # 결과 파일 정상 생성 확인
    new_sizes: dict[str, int] = {}
    for fmt, out_file in created_files.items():
        if not out_file.exists() or out_file.stat().st_size == 0:
            return FileResult(
                file_path=file_path,
                status="error",
                error_message=f"{fmt} 결과 파일이 정상 생성되지 않았습니다.",
            )
        new_sizes[fmt] = out_file.stat().st_size

    # 원본 파일 휴지통 이동 (옵션)
    if options.delete_originals:
        try:
            send2trash.send2trash(str(file_path.resolve()))
        except Exception as e:
            # 변환은 성공했으므로 에러로 처리하지 않고 note에 기록
            note = f"원본 휴지통 이동 실패: {e}"

    return FileResult(
        file_path=file_path,
        status="success",
        tag=tag,
        orig_size=orig_size,
        new_sizes=new_sizes,
        note=note,
    )


def collect_target_files(paths: list[Path]) -> list[Path]:
    """파일 및 디렉토리 목록에서 지원하는 모든 대상 이미지 파일 목록을 평탄화하여 수집"""
    collected: list[Path] = []
    seen = set()

    for p in paths:
        if p.is_file():
            if p.suffix.lower() in SUPPORTED_EXTENSIONS and p.resolve() not in seen:
                collected.append(p)
                seen.add(p.resolve())
        elif p.is_dir():
            for item in p.rglob("*"):
                if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS and item.resolve() not in seen:
                    collected.append(item)
                    seen.add(item.resolve())

    return collected


def process_batch(
    files: list[Path],
    options: ConversionOptions,
    progress_callback: Optional[Callable[[int, int, FileResult], None]] = None,
    cancel_check: Optional[Callable[[], bool]] = None,
) -> list[FileResult]:
    """여러 파일을 순차 변환하며 진행률 콜백 호출 및 취소 확인"""
    results: list[FileResult] = []
    total = len(files)

    for idx, f in enumerate(files, start=1):
        if cancel_check and cancel_check():
            break

        try:
            res = process_single_file(f, options)
        except Exception as e:
            res = FileResult(
                file_path=f,
                status="error",
                orig_size=f.stat().st_size if f.exists() else 0,
                error_message=str(e),
            )

        results.append(res)
        if progress_callback:
            progress_callback(idx, total, res)

    return results
