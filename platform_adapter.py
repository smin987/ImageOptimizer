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
        resolved = str(file_path.resolve())
        send2trash.send2trash(resolved)
        notify_file_deleted(file_path)
        return True
    except Exception as e:
        print(f"[Warning] 휴지통 이동 실패: {file_path.name} ({e})")
        return False


def notify_file_created(file_path: Path) -> None:
    """새 파일이 디스크에 생성되었음을 OS 파일 탐색기에 즉시 통지 (0ms)"""
    if get_current_os() == "Windows":
        try:
            import ctypes
            # SHCNE_CREATE = 0x00000002, SHCNF_PATHW = 0x0005
            ctypes.windll.shell32.SHChangeNotify(0x00000002, 0x0005, str(file_path.resolve()), 0)
        except Exception:
            pass


def notify_file_deleted(file_path: Path) -> None:
    """파일이 삭제/휴지통 이동되었음을 OS 파일 탐색기에 즉시 통지 (0ms)"""
    if get_current_os() == "Windows":
        try:
            import ctypes
            # SHCNE_DELETE = 0x00000004, SHCNF_PATHW = 0x0005
            ctypes.windll.shell32.SHChangeNotify(0x00000004, 0x0005, str(file_path.resolve()), 0)
        except Exception:
            pass


def notify_folder_updated(folder_path: Path) -> None:
    """폴더 내 항목이 변경(생성/삭제)되었음을 쉘에 즉시 통지 (0ms)"""
    if get_current_os() == "Windows":
        try:
            import ctypes
            # SHCNE_UPDATEDIR = 0x00001000, SHCNF_PATHW = 0x0005, SHCNF_FLUSH = 0x1000
            ctypes.windll.shell32.SHChangeNotify(0x00001000, 0x1005, str(folder_path.resolve()), 0)
        except Exception:
            pass


def refresh_folder(folder_path: Path) -> None:
    """
    지정된 폴더에 대해 운영체제 파일 탐색기가 즉시 새로고침(F5)하도록 통지합니다.
    열려 있는 탐색기 창이 있다면 해당 창의 뷰를 즉각 갱신합니다.
    """
    refresh_folders({folder_path})


def refresh_folders(folder_paths: set[Path] | list[Path]) -> None:
    """
    여러 폴더에 대해 운영체제 파일 탐색기가 즉시 새로고침(F5)하도록 일괄 통지합니다.
    """
    valid_paths = [p for p in folder_paths if p and p.exists()]
    if not valid_paths:
        return

    # 1. 시스템 쉘 알림 API (0ms 초고속 통지)
    for p in valid_paths:
        notify_folder_updated(p)

    # 2. Windows 환경: 열려 있는 탐색기 창(Explorer) 새로고침(F5) 트리거
    if get_current_os() == "Windows":
        try:
            resolved_list = [str(p.resolve()).replace("'", "''") for p in valid_paths]
            paths_arr = "@(" + ", ".join(f"'{p}'" for p in resolved_list) + ")"
            ps_script = (
                f"$paths = {paths_arr}; "
                "$sh = New-Object -ComObject Shell.Application; "
                "foreach ($w in $sh.Windows()) { "
                "  try { "
                "    $curr = $w.Document.Folder.Self.Path; "
                "    if ($paths -contains $curr) { $w.Refresh() } "
                "  } catch {} "
                "}"
            )
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", ps_script],
                creationflags=flags,
                timeout=2,
            )
        except Exception:
            pass


def get_system_font_family() -> str:
    """OS별 가독성이 우수한 기본 UI 폰트 패밀리 반환"""
    current_os = get_current_os()
    if current_os == "Windows":
        return "Segoe UI Variable, Segoe UI, Malgun Gothic, sans-serif"
    elif current_os == "Darwin":
        return "-apple-system, SF Pro, Apple SD Gothic Neo, sans-serif"
    else:
        return "Noto Sans CJK KR, Ubuntu, DejaVu Sans, sans-serif"
