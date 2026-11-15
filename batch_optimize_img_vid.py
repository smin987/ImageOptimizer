import os
import platform  # OS 판별용 모듈 추가
import shutil
import subprocess
from pathlib import Path

# ImageOps 추가 (회전 방지용)
from PIL import Image, ImageOps

# ================= 설정 구간 =================
INPUT_FOLDER = "./input_images"
OUTPUT_FOLDER = "./output_images"

# 최대 가로 해상도
MAX_WIDTH = 1920

# WebP 이미지 압축 품질 (1~100)
IMAGE_QUALITY = 90

# MP4 비디오 압축률 (CRF: 0~51, 낮을수록 고화질)
VIDEO_CRF = 23

# ★ 최적화 완료 후 원본 이미지 삭제 여부 (True: 삭제, False: 유지)
DELETE_ORIGINALS = True

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"}
# ============================================


def open_folder(path: Path):
    """OS에 맞춰 파일 탐색기를 열고, 열 수 없는 환경이면 안전하게 무시"""
    abs_path = str(path.resolve())
    current_os = platform.system()

    try:
        if current_os == "Windows":
            os.startfile(abs_path)
        elif current_os == "Darwin":  # macOS
            subprocess.run(["open", abs_path], check=False)
        elif current_os == "Linux":  # Linux (Ubuntu 데스크톱 등)
            subprocess.run(
                ["xdg-open", abs_path],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except Exception:
        # GUI가 없는 리눅스 서버 등에서는 에러를 무시하고 통과
        pass


def format_bytes(size_bytes):
    """바이트 크기를 KB/MB 단위로 변환"""
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"


def check_ffmpeg():
    """시스템에 ffmpeg가 설치되어 있는지 확인"""
    return shutil.which("ffmpeg") is not None


def process_image(img, out_file):
    """일반 정지 이미지 -> WebP 변환"""
    # 1. 스마트폰 카메라 회전 메타데이터 자동 적용
    img = ImageOps.exif_transpose(img)

    # 2. 색상 모드 변환 (투명 배경 보존)
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
    else:
        img = img.convert("RGB")

    # 3. 해상도 리사이징
    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / float(img.width)
        new_height = int(float(img.height) * float(ratio))
        img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)

    img.save(out_file, format="WEBP", quality=IMAGE_QUALITY, optimize=True)


def convert_gif_to_mp4(input_path, output_path):
    """움직이는 GIF -> 웹 최적화 MP4 변환"""
    scale_filter = f"scale='min({MAX_WIDTH},iw)':-2"

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-vf",
        scale_filter,
        "-c:v",
        "libx264",
        "-crf",
        str(VIDEO_CRF),
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-an",
        str(output_path),
    ]

    subprocess.run(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
    )


def process_single_file(file: Path, output_path: Path):
    """파일 1개를 판별하여 변환하고 (필요 시) 원본을 삭제하는 함수"""
    orig_size = file.stat().st_size
    if orig_size == 0:
        raise ValueError("빈 파일(0 바이트)입니다.")

    # 포맷 판별 및 변환
    if file.suffix.lower() == ".gif":
        with Image.open(file) as img:
            is_animated = getattr(img, "is_animated", False)

        if is_animated:
            if not check_ffmpeg():
                raise RuntimeError("GIF를 MP4로 변환하려면 ffmpeg가 필요합니다.")
            out_file = output_path / f"{file.stem}.mp4"
            convert_gif_to_mp4(file, out_file)
            tag = "[GIF -> MP4 비디오]"
        else:
            out_file = output_path / f"{file.stem}.webp"
            with Image.open(file) as img:
                process_image(img, out_file)
            tag = "[정지 GIF -> WebP]"
    else:
        out_file = output_path / f"{file.stem}.webp"
        with Image.open(file) as img:
            process_image(img, out_file)
        tag = "[이미지 -> WebP]"

    # 결과 검증
    if not out_file.exists() or out_file.stat().st_size == 0:
        raise RuntimeError("결과 파일이 비정상적으로 생성되었습니다.")

    new_size = out_file.stat().st_size
    reduction = (1 - (new_size / orig_size)) * 100

    print(f"[완료] {file.name} {tag}")
    print(
        f"       {format_bytes(orig_size)} -> {format_bytes(new_size)} ({reduction:.1f}% 절감)"
    )

    # 원본 삭제
    if DELETE_ORIGINALS:
        file.unlink()
        print(f"       🗑️ 원본 삭제: {file.name}")

    return orig_size, new_size


def optimize_files():
    """전체 파일 목록을 돌며 최적화를 총괄하는 함수"""
    input_path = Path(INPUT_FOLDER)
    output_path = Path(OUTPUT_FOLDER)
    output_path.mkdir(parents=True, exist_ok=True)

    files = [
        f for f in input_path.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    if not files:
        print(f"[{INPUT_FOLDER}] 폴더에 처리할 이미지가 없습니다.")
        return

    print(f"총 {len(files)}개의 파일 최적화를 시작합니다...")
    if DELETE_ORIGINALS:
        print("※ [주의] 작업 완료 후 원본 파일이 삭제됩니다.")
    print("=" * 55)

    total_orig_size = 0
    total_new_size = 0
    success_count = 0

    for file in files:
        try:
            orig_size, new_size = process_single_file(file, output_path)
            total_orig_size += orig_size
            total_new_size += new_size
            success_count += 1
        except Exception as e:
            print(f"[오류] {file.name} 처리 중 에러 (원본 유지): {e}")

    # 요약 출력
    print("=" * 55)
    print(f"변환 성공: {success_count}/{len(files)} 개")
    if total_orig_size > 0:
        overall_reduction = (1 - (total_new_size / total_orig_size)) * 100
        print(
            f"총 용량: {format_bytes(total_orig_size)} -> {format_bytes(total_new_size)}"
        )
        print(f"총 절감률: {overall_reduction:.1f}% 절약됨")
    # ★ 모든 변환이 끝나면 윈도우 탐색기로 output_images 폴더 열기
    open_folder(output_path)


# ★ 실행 진입점 추가
if __name__ == "__main__":
    optimize_files()
