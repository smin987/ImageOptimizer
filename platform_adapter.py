"""
크로스 플랫폼(Windows 11, Linux Debian, macOS) 시스템 어댑터 모듈
OS별 탐색기 열기, 휴지통 안전 삭제, 기본 설정 경로 및 시스템 폰트 추상화
"""

import os
from pathlib import Path
import platform
import subprocess
from typing import Optional

import send2trash


def get_current_os() -> str:
    """현재 운영체제 이름 반환 ('Windows', 'Darwin' (macOS), 'Linux')"""
    return platform.system()


def open_folder(path: Path) -> bool:
    """
    OS에 맞춰 파일 탐색기(Windows 탐색기, macOS Finder, Linux 파일 매니저)를 엽니다.
    """
    if not path.exists():
        return False

    abs_path = str(path.resolve())
    current_os = get_current_os()

    try:
        if current_os == "Windows":
            if hasattr(os, "startfile"):
                os.startfile(abs_path)
            else:
                subprocess.run(["explorer", abs_path], check=False)
            return True
        elif current_os == "Darwin":  # macOS
            subprocess.run(["open", abs_path], check=False)
            return True
        elif current_os == "Linux":  # Linux Debian/Ubuntu
            subprocess.run(
                ["xdg-open", abs_path],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
    except Exception:
        pass
    return False


def get_app_config_dir(app_name: str = "ImageOptimizer") -> Path:
    """OS별 표준 사용자 설정 저장 폴더 경로 반환 (기존 WebPOptimizer 설정 마이그레이션 지원)"""
    current_os = get_current_os()
    home = Path.home()

    if current_os == "Windows":
        app_data = os.environ.get("APPDATA")
        base = Path(app_data) if app_data else home / "AppData" / "Roaming"
        config_dir = base / app_name
        legacy_dir = base / "WebPOptimizer"
    elif current_os == "Darwin":  # macOS
        config_dir = home / "Library" / "Application Support" / app_name
        legacy_dir = home / "Library" / "Application Support" / "WebPOptimizer"
    else:  # Linux (XDG Base Directory)
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        base = Path(xdg_config) if xdg_config else home / ".config"
        config_dir = base / app_name.lower()
        legacy_dir = base / "webpoptimizer"

    config_dir.mkdir(parents=True, exist_ok=True)

    # 기존 WebPOptimizer/settings.json 설정 자동 승계 (하위 호환)
    legacy_settings = legacy_dir / "settings.json"
    new_settings = config_dir / "settings.json"
    if legacy_settings.exists() and not new_settings.exists():
        try:
            import shutil
            shutil.copy2(legacy_settings, new_settings)
        except Exception:
            pass

    return config_dir


def send_to_trash(file_path: Path) -> bool:
    """
    파일을 OS에 상관없이 안전하게 시스템 휴지통으로 이동합니다.
    (Windows 휴지통, macOS 휴지통, Linux FreeDesktop Trash 모두 지원)
    """
    try:
        send2trash.send2trash(str(file_path.resolve()))
        return True
    except Exception as e:
        print(f"[Warning] 휴지통 이동 실패: {file_path.name} ({e})")
        return False


def get_system_font_family() -> str:
    """OS별 가독성이 우수한 기본 UI 폰트 패밀리 반환"""
    current_os = get_current_os()
    if current_os == "Windows":
        return "Segoe UI Variable, Segoe UI, Malgun Gothic, sans-serif"
    elif current_os == "Darwin":
        return "-apple-system, SF Pro, Apple SD Gothic Neo, sans-serif"
    else:
        return "Noto Sans CJK KR, Ubuntu, DejaVu Sans, sans-serif"
