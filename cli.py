"""
Image Optimizer CLI (Command-Line Interface)
단일 실행 파일에서 터미널 인자 감지 시 초고속 헤드리스 일괄 변환을 수행하는 모듈
명령어 별칭: iopt, image-optimizer
"""

import argparse
import os
from pathlib import Path
import sys
import time

from converter_core import (
    SUPPORTED_EXTENSIONS,
    ConversionOptions,
    FileResult,
    collect_target_files,
    format_bytes,
    process_single_file,
)

VERSION = "1.0.5"

# 터미널 ANSI 컬러 코드 (Windows 10+ 및 Unix 터미널 지원)
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_GREEN = "\033[32m"
COLOR_CYAN = "\033[36m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_MAGENTA = "\033[35m"


def enable_windows_ansi():
    """Windows cmd/powershell에서 ANSI 컬러 이스케이프 활성화"""
    if sys.platform == "win32":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            # STD_OUTPUT_HANDLE = -11
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass


def build_parser() -> argparse.ArgumentParser:
    """CLI 인자 파서 생성"""
    parser = argparse.ArgumentParser(
        prog="iopt",
        description=f"{COLOR_BOLD}Image Optimizer CLI (iopt){COLOR_RESET} - 초고효율 WebP/JPG 이미지 및 움짤 변환 최적화 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  iopt photo.png                        # 단일 이미지를 WebP(품질 85)로 변환
  iopt photo.png -f jpg -q 90           # JPG 포맷 및 품질 90으로 변환
  iopt photo.png -f both                # WebP와 JPG를 동시에 둘 다 생성
  iopt ./images/ -r                     # images 폴더 내 모든 이미지를 재귀 탐색하여 일괄 변환
  iopt banner.gif                       # 움직이는 GIF를 초경량 애니메이션 WebP로 변환
  iopt *.jpg --resize-width 1920        # 가로폭 1920px 초과 시 비율 유지 축소
  iopt *.png --scale 50 -o ./output/    # 50% 축소하여 output 폴더에 저장
  iopt photo.png --flatten-white        # 투명 배경을 흰색 배경으로 합성
  iopt --gui                            # 데스크톱 GUI 창 실행
""",
    )

    # 위치 인자: 파일 또는 폴더 경로 (여러 개 가능)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="변환할 이미지 파일 또는 디렉토리 경로 (여러 개 지정 가능)",
    )

    # 출력 포맷 & 품질
    parser.add_argument(
        "-f",
        "--format",
        choices=["webp", "jpg", "both"],
        default="webp",
        help="출력 포맷 선택: webp (기본값), jpg, both (둘 다 동시 생성)",
    )
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=85,
        metavar="1-100",
        help="압축 품질 (1~100, 기본값: 85)",
    )

    # 출력 위치
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        metavar="DIR",
        help="출력 디렉토리 지정 (미지정 시 원본 파일과 동일한 위치)",
    )
    parser.add_argument(
        "--subfolder",
        type=str,
        default=None,
        metavar="NAME",
        help="각 원본 폴더 아래 지정한 이름의 하위 폴더에 저장 (예: optimized)",
    )

    # 리사이즈 옵션
    resize_group = parser.add_argument_group("리사이즈 옵션")
    resize_group.add_argument(
        "--resize-width",
        type=int,
        default=None,
        metavar="PX",
        help="최대 가로폭 제한 (가로폭이 지정값보다 크면 비율을 유지하며 축소, 예: 1920)",
    )
    resize_group.add_argument(
        "--scale",
        type=int,
        default=None,
        metavar="%",
        help="비율(%%) 축소 (1~99, 예: 50 입력 시 절반 크기로 축소)",
    )

    # 투명도 & 원본 처리
    advanced_group = parser.add_argument_group("고급 및 원본 처리 옵션")
    advanced_group.add_argument(
        "--flatten-white",
        action="store_true",
        help="투명 배경을 흰색(RGB) 배경으로 합성 (기본값은 투명 Alpha 채널 100%% 보존)",
    )
    advanced_group.add_argument(
        "--trash-orig",
        action="store_true",
        help="변환 성공 시 원본 파일을 시스템 휴지통으로 안전 이동",
    )
    advanced_group.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="디렉토리 지정 시 하위 폴더까지 재귀적으로 이미지 탐색",
    )

    # 기타
    parser.add_argument(
        "--gui",
        action="store_true",
        help="GUI 모드로 실행 (인자가 있더라도 데스크톱 화면 창을 띄움)",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s (Image Optimizer) v{VERSION}",
    )

    return parser


def parse_conversion_options(args: argparse.Namespace) -> ConversionOptions:
    """argparse 인자를 ConversionOptions 데이터 클래스로 변환"""
    # 포맷 매핑
    fmt_upper = args.format.upper()
    if fmt_upper == "BOTH":
        output_formats = ["WEBP", "JPG"]
    elif fmt_upper == "JPG":
        output_formats = ["JPG"]
    else:
        output_formats = ["WEBP"]

    # 품질 유효성 검사 (1~100)
    quality = max(1, min(100, args.quality))

    # 리사이즈 모드 결정
    if args.resize_width:
        resize_mode = "max_width"
        max_width = args.resize_width
        scale_percent = 50
    elif args.scale:
        resize_mode = "scale_percent"
        max_width = 1920
        scale_percent = max(1, min(99, args.scale))
    else:
        resize_mode = "none"
        max_width = 1920
        scale_percent = 50

    # 출력 모드 결정
    if args.output:
        output_mode = "custom"
        custom_output_dir = args.output
        subfolder_name = "optimized"
    elif args.subfolder:
        output_mode = "sub"
        custom_output_dir = None
        subfolder_name = args.subfolder
    else:
        output_mode = "same"
        custom_output_dir = None
        subfolder_name = "optimized"

    return ConversionOptions(
        output_formats=output_formats,
        quality=quality,
        resize_mode=resize_mode,
        max_width=max_width,
        scale_percent=scale_percent,
        remove_alpha=args.flatten_white,
        delete_originals=args.trash_orig,
        output_mode=output_mode,
        custom_output_dir=custom_output_dir,
        subfolder_name=subfolder_name,
    )


def collect_cli_files(raw_paths: list[Path], recursive: bool) -> list[Path]:
    """CLI에서 전달받은 경로 목록에서 대상 이미지 파일 수집 (단일 파일, 디렉토리, 재귀)"""
    collected: list[Path] = []
    seen = set()

    for p in raw_paths:
        p = p.expanduser()
        if not p.exists():
            print(f"{COLOR_YELLOW}⚠️  경로를 찾을 수 없습니다: {p}{COLOR_RESET}", file=sys.stderr)
            continue

        if p.is_file():
            if p.suffix.lower() in SUPPORTED_EXTENSIONS and p.resolve() not in seen:
                collected.append(p)
                seen.add(p.resolve())
            else:
                print(f"{COLOR_YELLOW}⚠️  지원하지 않는 파일 형식: {p.name}{COLOR_RESET}", file=sys.stderr)
        elif p.is_dir():
            pattern = "**/*" if recursive else "*"
            for item in p.glob(pattern):
                if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS and item.resolve() not in seen:
                    collected.append(item)
                    seen.add(item.resolve())

    return collected


def run_cli(args_list: list[str]) -> int:
    """CLI 메인 실행 함수. 성공 시 0, 오류 발생 시 1 반환"""
    enable_windows_ansi()
    parser = build_parser()
    args = parser.parse_args(args_list)

    # --gui 옵션이 전달된 경우 GUI 실행 플래그 반환
    if args.gui or not args.paths:
        return -1  # GUI 모드로 전환하라는 신호

    options = parse_conversion_options(args)
    target_files = collect_cli_files(args.paths, args.recursive)

    if not target_files:
        print(f"{COLOR_RED}❌ 변환할 유효한 이미지 파일을 찾지 못했습니다.{COLOR_RESET}")
        return 1

    total_files = len(target_files)
    print(f"\n{COLOR_BOLD}{COLOR_CYAN}🚀 Image Optimizer (iopt) v{VERSION} 시작{COLOR_RESET}")
    print(f"📁 대상 파일: {COLOR_BOLD}{total_files}개{COLOR_RESET}")
    print(f"⚙️  설정: 포맷={COLOR_GREEN}{', '.join(options.output_formats)}{COLOR_RESET}, 품질={options.quality}, 리사이즈={options.resize_mode}")
    if options.output_mode == "custom":
        print(f"📂 저장 경로: {options.custom_output_dir}")
    print("-" * 65)

    start_time = time.time()
    success_count = 0
    skipped_count = 0
    error_count = 0
    total_orig_size = 0
    total_new_size = 0

    for idx, f in enumerate(target_files, start=1):
        try:
            res: FileResult = process_single_file(f, options)
        except Exception as e:
            res = FileResult(file_path=f, status="error", error_message=str(e))

        progress_prefix = f"[{idx}/{total_files}]"

        if res.status == "success":
            success_count += 1
            total_orig_size += res.orig_size
            file_new_total = sum(res.new_sizes.values())
            total_new_size += file_new_total

            # 절감률 계산
            if res.orig_size > 0:
                saved_ratio = (1.0 - (file_new_total / res.orig_size)) * 100.0
                ratio_str = f"{saved_ratio:+.1f}%"
                color = COLOR_GREEN if saved_ratio >= 0 else COLOR_YELLOW
            else:
                ratio_str = "0.0%"
                color = COLOR_GREEN

            orig_str = format_bytes(res.orig_size)
            new_str = format_bytes(file_new_total)
            note_str = f" ({res.note})" if res.note else ""

            print(
                f"{COLOR_BOLD}{progress_prefix}{COLOR_RESET} {f.name} -> {COLOR_BOLD}{new_str}{COLOR_RESET} "
                f"({orig_str} -> {color}{ratio_str}{COLOR_RESET}){note_str}"
            )

        elif res.status == "skipped":
            skipped_count += 1
            print(f"{COLOR_YELLOW}{progress_prefix} 건너뜀: {f.name} ({res.note}){COLOR_RESET}")
        else:
            error_count += 1
            print(f"{COLOR_RED}{progress_prefix} 실패: {f.name} - {res.error_message}{COLOR_RESET}", file=sys.stderr)

    elapsed = time.time() - start_time
    print("-" * 65)

    # 최종 결과 리포트
    if total_orig_size > 0:
        total_saved_bytes = total_orig_size - total_new_size
        total_saved_ratio = (total_saved_bytes / total_orig_size) * 100.0
        saved_str = format_bytes(max(0, total_saved_bytes))
        orig_str = format_bytes(total_orig_size)
        new_str = format_bytes(total_new_size)
        print(f"{COLOR_BOLD}🎉 최적화 완료!{COLOR_RESET} (소요 시간: {elapsed:.2f}초)")
        print(f"📊 성공: {COLOR_GREEN}{success_count}{COLOR_RESET}개, 건너뜀: {skipped_count}개, 실패: {error_count}개")
        print(
            f"💾 용량 절감: {orig_str} -> {COLOR_BOLD}{new_str}{COLOR_RESET} "
            f"({COLOR_GREEN}{COLOR_BOLD}{total_saved_ratio:.1f}% 절감{COLOR_RESET}, 총 {saved_str} 절약)"
        )
    else:
        print(f"완료 (소요 시간: {elapsed:.2f}초) - 성공: {success_count}, 실패: {error_count}")

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(run_cli(sys.argv[1:]))
