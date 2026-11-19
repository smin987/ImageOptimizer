"""
Image Optimizer - 크로스 플랫폼 GUI 메인 애플리케이션
Windows 11, Linux Debian, macOS 지원 (PySide6)
"""

import json
import os
from pathlib import Path
import sys
from typing import Optional

# 4K / HiDPI 고해상도 모니터 자동 스케일링 환경 변수 활성화
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"

# Windows 환경에서 Qt QPA DPI 중복 설정 관련 콘솔 노이즈 경고 억제
os.environ["QT_LOGGING_RULES"] = "qt.qpa.window=false"

from PySide6.QtCore import QPoint, Qt, QThread, Signal
from PySide6.QtGui import (
    QColor,
    QDragEnterEvent,
    QDropEvent,
    QFont,
    QGuiApplication,
    QIcon,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from converter_core import (
    SUPPORTED_EXTENSIONS,
    SNS_CROP_MODE_KEYS,
    SNS_PRESET_KEYS,
    SNS_PRESETS,
    ConversionOptions,
    FileResult,
    collect_target_files,
    determine_output_dir,
    format_bytes,
    process_single_file,
)
import platform_adapter as pa

def get_resource_path(relative_path: str) -> Path:
    """PyInstaller 번들 내부 리소스 및 일반 개발 환경 리소스 경로 안전 반환"""
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_dir / relative_path

SETTINGS_FILE = pa.get_app_config_dir() / "settings.json"

I18N = {
    "ko": {
        "theme_dark": "🌙 다크 모드로 전환",
        "theme_light": "☀️ 기본(라이트) 모드로 전환",
        "lang_toggle": "🌐 English",
        "btn_sponsor": "💖 후원하기",
        "btn_sponsor_tip": "GitHub Sponsors를 통해 개발자를 후원하고 지속적인 업데이트를 응원합니다.",
        "btn_about": "ℹ️ 정보 / 라이선스",
        "btn_about_tip": "앱 버전, 저작권 및 제3자 오픈소스 라이선스 정보를 확인합니다.",
        "about_dlg_title": "정보 및 오픈소스 라이선스",
        "about_dlg_btn_repo": "🌐 GitHub 저장소",
        "about_dlg_btn_file": "📄 라이선스 문서 열기",
        "about_dlg_btn_close": "닫기",
        "desc_text": (
            "원본 이미지를 웹사이트 게시전용으로 최적화하여 경량화된 이미지로 변경해주는 도구입니다.\n"
            "원본 이미지와 화질차이는 거의 없지만 최대 90% 정도의 이미지 용량을 줄일 수 있습니다. "
            "('이미지 품질' 설정값에 따라 달라질 수 있음)\n"
            "※ 애니메이션 GIF도 WebP로 변환 가능"
        ),
        "drop_title": "이미지 또는 폴더를 드래그 앤 드롭하세요",
        "queue_status_init": "최적화할 이미지 또는 폴더를 드래그하거나 버튼으로 추가하세요.",
        "queue_status_added": "✅ {count}개의 이미지가 최적화 대상 목록에 추가되었습니다.",
        "queue_status_cleared": "최적화 대상 목록이 초기화되었습니다.",
        "queue_status_auto_cleared": "변환이 완료되어 최적화 대상 목록이 자동으로 비워졌습니다.",
        "btn_add_files": "📄 파일 추가",
        "btn_add_folder": "📁 폴더 추가",
        "btn_clear_list": "🗑️ 대기 목록 비우기",
        "btn_queue_count": "최적화 대상 이미지: {count}개 🔍",
        "btn_queue_count_tip": "클릭하면 최적화 대상 이미지 전체 목록을 확인하고 개별 제외할 수 있습니다.",
        "settings_title": "⚙️ 설정",
        "settings_toggle_hide": "▲ ⚙️ 설정",
        "settings_toggle_show": "▼ ⚙️ 설정",
        "lbl_format": "출력 포맷:",
        "fmt_both": "둘 다(BOTH)",
        "lbl_quality": "이미지 품질:",
        "lbl_resize": "해상도 조절:",
        "resize_modes": [
            "선택하세요",
            "최대 가로폭에 맞춤",
            "비율(%) 축소 (Scale %)",
            "🌟 SNS / 인플루언서 맞춤 프리셋",
            "원본 크기 유지 (100%)",
        ],
        "lbl_sns_preset": "플랫폼:",
        "lbl_sns_crop": "맞춤 방식:",
        "sns_presets": [
            "🎬 [유튜브] 썸네일 - FHD (1920×1080, 16:9)",
            "🎬 [유튜브] 썸네일 - HD 기본 (1280×720, 16:9)",
            "📱 [유튜브] 쇼츠 커버 (1080×1920, 9:16)",
            "📱 [SNS 공용] 세로 표준 규격 (1080×1350, 4:5)",
            "🐦 [X / 스레드] 타임라인 피드 (1200×675, 16:9)",
            "📸 [인스타] 최신 세로 피드 (1080×1440, 3:4)",
            "🔲 [인스타] 정사각형 피드 (1080×1080, 1:1)",
            "🖼️ [인스타] 가로형 와이드 (1080×566, 1.91:1)",
            "🚀 [인스타] 릴스 / 스토리 (1080×1920, 9:16)",
            "📝 [블로그] 본문 최적 가로폭 (1200px)",
            "📌 [블로그] 대표 썸네일 (1080×1080, 1:1)",
        ],
        "sns_crop_modes": [
            "비율유지(기본값)",
            "스마트 중앙 맞춤 (화면 꽉 채우기)",
            "빈공간 흰색 레터박스",
            "빈공간 검은색 레터박스",
        ],
        "lbl_dest": "저장 위치:",
        "dest_sub": "하위 'optimized' 폴더",
        "dest_same": "원본과 동일 폴더",
        "dest_custom": "지정 폴더",
        "btn_browse": "찾아보기...",
        "chk_remove_alpha": "투명 배경(Alpha Channel) 제거",
        "chk_remove_alpha_tip": (
            "체크 시: 투명 배경을 제거하고 흰색 배경으로 합성합니다.\n"
            "체크 해제(기본): 투명 배경(Alpha Channel)을 100% 그대로 유지하며 WebP로 최적화합니다."
        ),
        "chk_delete_orig": "변환 성공 시 원본 파일을 휴지통으로 이동",
        "btn_start": "🚀 변환 시작",
        "btn_cancel": "⏹️ 작업 중단",
        "btn_open_folder": "📂 결과 열기",
        "status_ready": "파일을 드래그하여 추가한 후 [변환 시작]을 누르세요.",
        "status_cancelling": "작업 중단 요청 중...",
        "status_progress": "진행 중: {name} ({cur}/{total})",
        "log_toggle_hide": "▲ 📋 실시간 변환 로그",
        "log_toggle_show": "▼ 📋 실시간 변환 로그",
        "log_toggle_count_suffix": " ({count}건)",
        "log_headers": ["상태", "파일명", "유형", "용량 변화", "절감률"],
        "log_done": "✅ 완료",
        "log_skipped": "⚠️ 건너뜀",
        "log_error": "❌ 오류",
        "log_saving_suffix": "{reduc:.1f}% 절감",
        "log_alpha_note": "알파 보존",
        "stat_title": "📊 최적화 성과 대시보드",
        "stat_idle_count": "대기 중 (0건)",
        "stat_idle_saving": "🚀 변환을 실행하면 총 용량 절감 성과가 여기에 집계됩니다.",
        "stat_size_label": "용량 변화: -",
        "stat_count_format": "완료 {total}건 (성공 {success} / 건너뜀 {skipped} / 오류 {errors})",
        "stat_size_format": "용량: {orig} ➔ {new_str}",
        "stat_saving_single": "🚀 총 {diff} 절약 ({ratio:.1f}% 감소)",
        "stat_saving_both": "🚀 WebP 기준 {diff} 절약 ({ratio:.1f}% 감소)",
        "stat_saving_negative": "ℹ️ 용량 변동 {diff} ({ratio:+.1f}%)",
        "stat_no_data": "변환된 파일이 없습니다.",
        "msg_del_warn_title": "⚠️ 원본 파일 삭제 주의",
        "msg_del_warn_text": "변환 완료 시 원본 파일이 삭제(휴지통 이동)됩니다.\n삭제 옵션을 활성화하시겠습니까?",
        "msg_no_files_title": "파일 없음",
        "msg_no_files_text": "변환할 이미지 파일을 먼저 추가하거나 드래그 앤 드롭해 주세요.",
        "msg_done_title": "작업 완료",
        "msg_done_text": "변환 완료! (총 {total}개 중 성공: {success}개, 건너뜀: {skipped}개, 실패: {errors}개)",
        "dlg_select_files": "이미지 파일 선택",
        "dlg_select_folder": "이미지가 있는 폴더 선택",
        "dlg_select_dest": "저장할 대상 폴더 선택",
        "dlg_queue_empty_title": "최적화 대상 없음",
        "dlg_queue_empty_text": "현재 최적화 대상 이미지가 없습니다.\n이미지 파일이나 폴더를 추가한 후 클릭해 주세요.",
        "queue_dlg_title": "최적화 대상 이미지 목록 ({count}개)",
        "queue_dlg_headers": ["#", "파일명", "용량", "폴더 경로"],
        "queue_dlg_info": "현재 최적화 대상 이미지: 총 {count}개",
        "queue_dlg_hint": "💡 이미지를 클릭하면 초록색으로 선택되고, 다시 클릭하면 해제됩니다.",
        "queue_dlg_btn_all": "전체 선택",
        "queue_dlg_btn_deselect": "선택 해제",
        "queue_dlg_btn_remove": "❌ 선택한 항목 제외",
        "queue_dlg_btn_remove_n": "❌ 선택한 항목 제외 ({count}개)",
        "queue_dlg_btn_close": "확인 및 닫기",
        "queue_dlg_no_selection_title": "선택 없음",
        "queue_dlg_no_selection_text": "제외할 이미지를 목록에서 클릭하여 먼저 선택해 주세요.",
    },
    "en": {
        "theme_dark": "🌙 Dark Mode",
        "theme_light": "☀️ Light Mode",
        "lang_toggle": "🌐 한국어",
        "btn_sponsor": "💖 Sponsor",
        "btn_sponsor_tip": "Support the developer on GitHub Sponsors to keep this tool growing.",
        "btn_about": "ℹ️ About / Licenses",
        "btn_about_tip": "View app version, copyright, and third-party open source licenses.",
        "about_dlg_title": "About & Open Source Licenses",
        "about_dlg_btn_repo": "🌐 GitHub Repository",
        "about_dlg_btn_file": "📄 Open Licenses Document",
        "about_dlg_btn_close": "Close",
        "desc_text": (
            "Optimize and compress original images for website publishing with minimal quality loss.\n"
            "Reduce file size by up to 90% with virtually no noticeable visual difference. "
            "(Depends on 'Quality' setting)\n"
            "※ Supports converting animated GIF to WebP"
        ),
        "drop_title": "Drag & drop images or folders here",
        "queue_status_init": "Drag and drop images or folders, or use the buttons to add.",
        "queue_status_added": "✅ {count} image(s) added to the optimization queue.",
        "queue_status_cleared": "Optimization queue has been cleared.",
        "queue_status_auto_cleared": "Conversion completed. Queue has been automatically cleared.",
        "btn_add_files": "📄 Add Files",
        "btn_add_folder": "📁 Add Folder",
        "btn_clear_list": "🗑️ Clear Queue",
        "btn_queue_count": "Queued Images: {count} 🔍",
        "btn_queue_count_tip": "Click to view full list and exclude individual images.",
        "settings_title": "⚙️ Settings",
        "settings_toggle_hide": "▲ ⚙️ Settings",
        "settings_toggle_show": "▼ ⚙️ Settings",
        "lbl_format": "Format:",
        "fmt_both": "Both (BOTH)",
        "lbl_quality": "Quality:",
        "lbl_resize": "Resize:",
        "resize_modes": [
            "Select mode",
            "Fit Max Width",
            "Scale by Percent (%)",
            "🌟 Influencer & Social Media Presets",
            "Keep Original Size (100%)",
        ],
        "lbl_sns_preset": "Platform:",
        "lbl_sns_crop": "Fit Mode:",
        "sns_presets": [
            "🎬 [YouTube] Thumbnail - FHD (1920×1080, 16:9)",
            "🎬 [YouTube] Thumbnail - HD (1280×720, 16:9)",
            "📱 [YouTube] Shorts Cover (1080×1920, 9:16)",
            "📱 [Universal SNS] Portrait Standard (1080×1350, 4:5)",
            "🐦 [X / Threads] Timeline Feed (1200×675, 16:9)",
            "📸 [Instagram] Modern Portrait (1080×1440, 3:4)",
            "🔲 [Instagram] Square Feed (1080×1080, 1:1)",
            "🖼️ [Instagram] Wide Feed (1080×566, 1.91:1)",
            "🚀 [Instagram] Reels / Stories (1080×1920, 9:16)",
            "📝 [Blog] Content Width (1200px)",
            "📌 [Blog] Square Cover (1080×1080, 1:1)",
        ],
        "sns_crop_modes": [
            "Keep Ratio (Default)",
            "Smart Center Crop (Fill & Cover)",
            "White Letterbox Padding",
            "Black Letterbox Padding",
        ],
        "lbl_dest": "Save to:",
        "dest_sub": "Subfolder 'optimized'",
        "dest_same": "Same as original folder",
        "dest_custom": "Custom folder",
        "btn_browse": "Browse...",
        "chk_remove_alpha": "Remove transparent background (Alpha)",
        "chk_remove_alpha_tip": (
            "Checked: Removes transparency and flattens onto a solid white background.\n"
            "Unchecked (Default): Preserves 100% transparent alpha channels in WebP."
        ),
        "chk_delete_orig": "Move original files to Trash after conversion",
        "btn_start": "🚀 Start Conversion",
        "btn_cancel": "⏹️ Cancel",
        "btn_open_folder": "📂 Open Output",
        "status_ready": "Add files and click [Start Conversion].",
        "status_cancelling": "Cancelling task...",
        "status_progress": "Processing: {name} ({cur}/{total})",
        "log_toggle_hide": "▲ 📋 Real-time Conversion Log",
        "log_toggle_show": "▼ 📋 Real-time Conversion Log",
        "log_toggle_count_suffix": " ({count} files)",
        "log_headers": ["Status", "Filename", "Type", "Size Change", "Saving"],
        "log_done": "✅ Done",
        "log_skipped": "⚠️ Skipped",
        "log_error": "❌ Error",
        "log_saving_suffix": "{reduc:.1f}% Saved",
        "log_alpha_note": "Alpha kept",
        "stat_title": "📊 Optimization Performance Dashboard",
        "stat_idle_count": "Idle (0 files)",
        "stat_idle_saving": "🚀 Total savings and reduction metrics will appear here after conversion.",
        "stat_size_label": "Size Change: -",
        "stat_count_format": "Done {total} (Success {success} / Skipped {skipped} / Errors {errors})",
        "stat_size_format": "Size: {orig} ➔ {new_str}",
        "stat_saving_single": "🚀 Total {diff} Saved ({ratio:.1f}% reduction)",
        "stat_saving_both": "🚀 Based on WebP: {diff} Saved ({ratio:.1f}% reduction)",
        "stat_saving_negative": "ℹ️ Size delta {diff} ({ratio:+.1f}%)",
        "stat_no_data": "No files converted.",
        "msg_del_warn_title": "⚠️ Original File Deletion Warning",
        "msg_del_warn_text": "Original files will be moved to the Trash after conversion.\nDo you want to enable this deletion option?",
        "msg_no_files_title": "No Files",
        "msg_no_files_text": "Please add or drag and drop image files to convert first.",
        "msg_done_title": "Conversion Completed",
        "msg_done_text": "Conversion completed! (Total {total}: Success {success}, Skipped {skipped}, Failed {errors})",
        "dlg_select_files": "Select Image Files",
        "dlg_select_folder": "Select Folder with Images",
        "dlg_select_dest": "Select Destination Folder",
        "dlg_queue_empty_title": "No Images Queued",
        "dlg_queue_empty_text": "There are currently no queued images.\nPlease add images or folders first.",
        "queue_dlg_title": "Optimization Queue ({count} files)",
        "queue_dlg_headers": ["#", "Filename", "Size", "Folder Path"],
        "queue_dlg_info": "Queued Images: {count} total",
        "queue_dlg_hint": "💡 Click an item to toggle green selection for exclusion.",
        "queue_dlg_btn_all": "Select All",
        "queue_dlg_btn_deselect": "Deselect All",
        "queue_dlg_btn_remove": "❌ Exclude Selected",
        "queue_dlg_btn_remove_n": "❌ Exclude Selected ({count})",
        "queue_dlg_btn_close": "OK & Close",
        "queue_dlg_no_selection_title": "No Selection",
        "queue_dlg_no_selection_text": "Please click and select images from the list to exclude first.",
    },
}

DARK_STYLE = """
QWidget {
    background-color: #0f1117;
    color: #f1f5f9;
    font-size: 10.5pt;
    font-family: 'Segoe UI Variable Text', 'Segoe UI', 'Malgun Gothic', sans-serif;
}

QLabel {
    background-color: transparent;
}

QFrame#settings_card {
    background-color: #161922;
    border: 1px solid #282d3c;
    border-radius: 8px;
}
QLabel#lbl_settings_header {
    color: #38bdf8;
    font-size: 11pt;
    font-weight: bold;
    background-color: transparent;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e2430;
}

QPushButton {
    background-color: #1e2430;
    border: 1px solid #333a4a;
    border-radius: 6px;
    padding: 7px 16px;
    color: #f1f5f9;
    font-size: 10pt;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #2b3345;
    border-color: #4a5568;
}
QPushButton:pressed {
    background-color: #171b24;
}
QPushButton:disabled {
    background-color: #12151c;
    color: #64748b;
    border-color: #212634;
}

QPushButton#btn_start {
    background-color: #2563eb;
    border: none;
    color: #ffffff;
    font-size: 11.5pt;
    font-weight: bold;
    padding: 10px 24px;
    border-radius: 6px;
}
QPushButton#btn_start:hover {
    background-color: #3b82f6;
}
QPushButton#btn_start:pressed {
    background-color: #1d4ed8;
}
QPushButton#btn_start:disabled {
    background-color: #1e293b;
    color: #64748b;
}

QPushButton#btn_cancel {
    background-color: #dc2626;
    border: none;
    color: #ffffff;
    font-size: 11.5pt;
    font-weight: bold;
    padding: 10px 24px;
    border-radius: 6px;
}
QPushButton#btn_cancel:hover {
    background-color: #ef4444;
}
QPushButton#btn_cancel:disabled {
    background-color: #381a1d;
    color: #ffffff;
}

QPushButton#btn_open_folder {
    background-color: #059669;
    border: none;
    color: #ffffff;
    font-size: 11.5pt;
    font-weight: bold;
    padding: 10px 24px;
    border-radius: 6px;
}
QPushButton#btn_open_folder:hover {
    background-color: #10b981;
}
QPushButton#btn_open_folder:pressed {
    background-color: #047857;
}
QPushButton#btn_open_folder:disabled {
    background-color: #1e293b;
    color: #64748b;
}

QPushButton#btn_toggle_log {
    background-color: transparent;
    border: none;
    color: #94a3b8;
    font-size: 9.5pt;
    font-weight: 600;
    text-align: left;
    padding: 3px 4px;
}
QPushButton#btn_toggle_log:hover {
    color: #38bdf8;
}

QPushButton#btn_toggle_settings {
    background-color: transparent;
    border: none;
    color: #38bdf8;
    font-size: 11pt;
    font-weight: bold;
    text-align: left;
    padding: 0px 2px;
}
QPushButton#btn_toggle_settings:hover {
    color: #7dd3fc;
}

QPushButton#btn_theme_toggle, QPushButton#btn_lang_toggle, QPushButton#btn_about {
    background-color: #1e2430;
    border: 1px solid #333a4a;
    border-radius: 14px;
    padding: 4px 12px;
    font-size: 9.5pt;
    font-weight: 600;
    color: #f1f5f9;
}
QPushButton#btn_theme_toggle:hover, QPushButton#btn_lang_toggle:hover, QPushButton#btn_about:hover {
    background-color: #2b3345;
    border-color: #38bdf8;
    color: #38bdf8;
}

QPushButton#btn_sponsor {
    background-color: #2a1523;
    border: 1px solid #701a45;
    border-radius: 14px;
    padding: 4px 12px;
    font-size: 9.5pt;
    font-weight: 600;
    color: #f472b6;
}
QPushButton#btn_sponsor:hover {
    background-color: #3b1930;
    border-color: #ec4899;
    color: #fbcfe8;
}

QPushButton[segment="true"] {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 5px;
    padding: 6px 16px;
    color: #94a3b8;
    font-weight: 600;
}
QPushButton[segment="true"]:hover {
    background-color: #242b3a;
    color: #f1f5f9;
}
QPushButton[segment="true"]:checked {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #3b82f6;
}

QPushButton[chip="true"] {
    background-color: #1e2430;
    border: 1px solid #2d3748;
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 9pt;
    color: #cbd5e1;
}
QPushButton[chip="true"]:hover {
    background-color: #2d3748;
    border-color: #38bdf8;
    color: #38bdf8;
}

QProgressBar {
    border: 1px solid #282d3c;
    border-radius: 6px;
    text-align: center;
    background-color: #12151c;
    color: #ffffff;
    font-weight: bold;
    font-size: 10pt;
    min-height: 22px;
}
QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 5px;
}

QTableWidget {
    background-color: #161922;
    border: 1px solid #282d3c;
    border-radius: 6px;
    gridline-color: #1e2430;
    color: #f1f5f9;
    font-size: 10pt;
}
QHeaderView::section {
    background-color: #1e2430;
    color: #94a3b8;
    padding: 6px;
    border: 1px solid #282d3c;
    font-weight: bold;
    font-size: 10pt;
}

QSlider::groove:horizontal {
    border: 1px solid #282d3c;
    height: 8px;
    background: #12151c;
    border-radius: 4px;
}
QSlider::sub-page:horizontal {
    background: #2563eb;
    border-radius: 4px;
}
QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #38bdf8;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}

QRadioButton {
    background-color: transparent;
    spacing: 10px;
    font-size: 10.5pt;
    color: #cbd5e1;
}
QRadioButton:checked {
    color: #38bdf8;
    font-weight: bold;
}
QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 10px;
    border: 2px solid #64748b;
    background-color: #1e2430;
}
QRadioButton::indicator:checked {
    border: 2px solid #38bdf8;
    background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 0.45, fx: 0.5, fy: 0.5,
        stop: 0 #ffffff,
        stop: 0.65 #ffffff,
        stop: 0.66 #2563eb,
        stop: 1 #2563eb);
}

QCheckBox {
    background-color: transparent;
    spacing: 10px;
    font-size: 10.5pt;
    color: #cbd5e1;
}
QCheckBox:checked {
    color: #38bdf8;
    font-weight: bold;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 2px solid #64748b;
    background-color: #1e2430;
}
QCheckBox::indicator:checked {
    border: 2px solid #38bdf8;
    background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 0.45, fx: 0.5, fy: 0.5,
        stop: 0 #ffffff,
        stop: 0.65 #ffffff,
        stop: 0.66 #2563eb,
        stop: 1 #2563eb);
}

QSpinBox, QComboBox {
    background-color: #1e2430;
    border: 1px solid #333a4a;
    border-radius: 4px;
    padding: 5px 8px;
    color: #f1f5f9;
    font-size: 10pt;
}

QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    border: none;
    background: #0f1117;
    width: 8px;
    border-radius: 4px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #333a4a;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #4a5568;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

LIGHT_STYLE = """
QWidget {
    background-color: #f8fafc;
    color: #0f172a;
    font-size: 10.5pt;
    font-family: 'Segoe UI Variable Text', 'Segoe UI', 'Malgun Gothic', sans-serif;
}

QLabel {
    background-color: transparent;
}

QFrame#settings_card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}
QLabel#lbl_settings_header {
    color: #2563eb;
    font-size: 11pt;
    font-weight: bold;
    background-color: transparent;
    padding-bottom: 6px;
    border-bottom: 1px solid #f1f5f9;
}

QPushButton {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 7px 16px;
    color: #1e293b;
    font-size: 10pt;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #f1f5f9;
    border-color: #94a3b8;
}
QPushButton:pressed {
    background-color: #e2e8f0;
}
QPushButton:disabled {
    background-color: #f8fafc;
    color: #94a3b8;
    border-color: #e2e8f0;
}

QPushButton#btn_start {
    background-color: #2563eb;
    border: none;
    color: #ffffff;
    font-size: 11.5pt;
    font-weight: bold;
    padding: 10px 24px;
    border-radius: 6px;
}
QPushButton#btn_start:hover {
    background-color: #1d4ed8;
}
QPushButton#btn_start:pressed {
    background-color: #1e40af;
}
QPushButton#btn_start:disabled {
    background-color: #94a3b8;
    color: #f8fafc;
}

QPushButton#btn_cancel {
    background-color: #dc2626;
    border: none;
    color: #ffffff;
    font-size: 11.5pt;
    font-weight: bold;
    padding: 10px 24px;
    border-radius: 6px;
}
QPushButton#btn_cancel:hover {
    background-color: #b91c1c;
}
QPushButton#btn_cancel:disabled {
    background-color: #fca5a5;
    color: #ffffff;
}

QPushButton#btn_open_folder {
    background-color: #059669;
    border: none;
    color: #ffffff;
    font-size: 11.5pt;
    font-weight: bold;
    padding: 10px 24px;
    border-radius: 6px;
}
QPushButton#btn_open_folder:hover {
    background-color: #047857;
}
QPushButton#btn_open_folder:pressed {
    background-color: #065f46;
}
QPushButton#btn_open_folder:disabled {
    background-color: #e2e8f0;
    color: #94a3b8;
}

QPushButton#btn_toggle_log {
    background-color: transparent;
    border: none;
    color: #64748b;
    font-size: 9.5pt;
    font-weight: 600;
    text-align: left;
    padding: 3px 4px;
}
QPushButton#btn_toggle_log:hover {
    color: #2563eb;
}

QPushButton#btn_toggle_settings {
    background-color: transparent;
    border: none;
    color: #2563eb;
    font-size: 11pt;
    font-weight: bold;
    text-align: left;
    padding: 0px 2px;
}
QPushButton#btn_toggle_settings:hover {
    color: #1d4ed8;
}

QPushButton#btn_theme_toggle, QPushButton#btn_lang_toggle, QPushButton#btn_about {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 14px;
    padding: 4px 12px;
    font-size: 9.5pt;
    font-weight: 600;
    color: #334155;
}
QPushButton#btn_theme_toggle:hover, QPushButton#btn_lang_toggle:hover, QPushButton#btn_about:hover {
    background-color: #f1f5f9;
    border-color: #2563eb;
    color: #2563eb;
}

QPushButton#btn_sponsor {
    background-color: #fdf2f8;
    border: 1px solid #fbcfe8;
    border-radius: 14px;
    padding: 4px 12px;
    font-size: 9.5pt;
    font-weight: 600;
    color: #db2777;
}
QPushButton#btn_sponsor:hover {
    background-color: #fce7f3;
    border-color: #f472b6;
    color: #be185d;
}

QPushButton[segment="true"] {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 5px;
    padding: 6px 16px;
    color: #64748b;
    font-weight: 600;
}
QPushButton[segment="true"]:hover {
    background-color: #e2e8f0;
    color: #0f172a;
}
QPushButton[segment="true"]:checked {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #1d4ed8;
}

QPushButton[chip="true"] {
    background-color: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 9pt;
    color: #334155;
}
QPushButton[chip="true"]:hover {
    background-color: #e2e8f0;
    border-color: #2563eb;
    color: #2563eb;
}

QProgressBar {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    text-align: center;
    background-color: #e2e8f0;
    color: #0f172a;
    font-weight: bold;
    font-size: 10pt;
    min-height: 22px;
}
QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 5px;
}

QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    gridline-color: #f1f5f9;
    color: #0f172a;
    font-size: 10pt;
}
QHeaderView::section {
    background-color: #f8fafc;
    color: #475569;
    padding: 6px;
    border: 1px solid #e2e8f0;
    font-weight: bold;
    font-size: 10pt;
}

QSlider::groove:horizontal {
    border: 1px solid #cbd5e1;
    height: 8px;
    background: #f1f5f9;
    border-radius: 4px;
}
QSlider::sub-page:horizontal {
    background: #2563eb;
    border-radius: 4px;
}
QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #2563eb;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}

QRadioButton {
    background-color: transparent;
    spacing: 10px;
    font-size: 10.5pt;
    color: #334155;
}
QRadioButton:checked {
    color: #2563eb;
    font-weight: bold;
}
QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 10px;
    border: 2px solid #94a3b8;
    background-color: #ffffff;
}
QRadioButton::indicator:checked {
    border: 2px solid #2563eb;
    background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 0.45, fx: 0.5, fy: 0.5,
        stop: 0 #ffffff,
        stop: 0.65 #ffffff,
        stop: 0.66 #2563eb,
        stop: 1 #2563eb);
}

QCheckBox {
    background-color: transparent;
    spacing: 10px;
    font-size: 10.5pt;
    color: #334155;
}
QCheckBox:checked {
    color: #2563eb;
    font-weight: bold;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 2px solid #94a3b8;
    background-color: #ffffff;
}
QCheckBox::indicator:checked {
    border: 2px solid #2563eb;
    background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 0.45, fx: 0.5, fy: 0.5,
        stop: 0 #ffffff,
        stop: 0.65 #ffffff,
        stop: 0.66 #2563eb,
        stop: 1 #2563eb);
}

QSpinBox, QComboBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 5px 8px;
    color: #0f172a;
    font-size: 10pt;
}

QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    border: none;
    background: #f8fafc;
    width: 8px;
    border-radius: 4px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #cbd5e1;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""


class DropAreaWidget(QFrame):
    """파일 및 폴더 드래그 앤 드롭을 지원하는 시각적 수신 영역"""

    files_dropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(90)
        self.is_hovered = False
        self.theme = "dark"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_icon = QLabel("📂")
        self.label_icon.setStyleSheet("font-size: 24pt; background: transparent;")
        self.label_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_text = QLabel(
            "이미지 또는 폴더를 드래그 앤 드롭하세요\n"
            f"(지원: {', '.join(sorted(SUPPORTED_EXTENSIONS))})"
        )
        self.label_text.setStyleSheet(
            "font-size: 10pt; font-weight: 500; background: transparent;"
        )
        self.label_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label_icon)
        layout.addWidget(self.label_text)
        self.lang = "ko"

    def set_language(self, lang: str):
        self.lang = lang
        title = I18N[lang]["drop_title"]
        prefix = "지원" if lang == "ko" else "Supports"
        exts = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        self.label_text.setText(f"{title}\n({prefix}: {exts})")

    def set_theme(self, theme: str):
        self.theme = theme
        if theme == "light":
            self.label_text.setStyleSheet(
                "color: #475569; font-size: 10pt; font-weight: 500; background: transparent;"
            )
        else:
            self.label_text.setStyleSheet(
                "color: #94a3b8; font-size: 10pt; font-weight: 500; background: transparent;"
            )
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen()
        if self.theme == "light":
            border_color = QColor("#2563eb") if self.is_hovered else QColor("#cbd5e1")
            bg_color = QColor("#eff6ff" if self.is_hovered else "#ffffff")
        else:
            border_color = QColor("#38bdf8") if self.is_hovered else QColor("#282d3c")
            bg_color = QColor("#1e293b" if self.is_hovered else "#141720")

        pen.setColor(border_color)
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.SolidLine if self.is_hovered else Qt.PenStyle.DashLine)

        painter.setPen(pen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 8, 8)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self.is_hovered = True
            self.update()
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.is_hovered = False
        self.update()

    def dropEvent(self, event: QDropEvent):
        self.is_hovered = False
        self.update()
        urls = event.mimeData().urls()
        paths = [Path(url.toLocalFile()) for url in urls if url.isLocalFile()]
        if paths:
            self.files_dropped.emit(paths)
        event.acceptProposedAction()


class ConversionWorker(QThread):
    """UI 프리징을 방지하는 백그라운드 변환 작업자 스레드"""

    progress = Signal(int, int, object)  # current, total, FileResult
    finished = Signal(int, int, int, int, int, dict)  # total, success, skipped, errors, total_orig_size, total_sizes

    def __init__(self, files: list[Path], options: ConversionOptions):
        super().__init__()
        self.files = files
        self.options = options
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        total = len(self.files)
        success_count = 0
        skipped_count = 0
        error_count = 0
        total_orig_size = 0
        total_new_sizes: dict[str, int] = {fmt: 0 for fmt in self.options.output_formats}

        for idx, file_path in enumerate(self.files, start=1):
            if self._is_cancelled:
                break

            try:
                res = process_single_file(file_path, self.options)
            except Exception as e:
                res = FileResult(
                    file_path=file_path,
                    status="error",
                    orig_size=file_path.stat().st_size if file_path.exists() else 0,
                    error_message=str(e),
                )

            if res.status == "success":
                success_count += 1
                total_orig_size += res.orig_size
                for fmt, sz in res.new_sizes.items():
                    total_new_sizes[fmt] = total_new_sizes.get(fmt, 0) + sz
            elif res.status == "skipped":
                skipped_count += 1
            else:
                error_count += 1

            self.progress.emit(idx, total, res)

        self.finished.emit(
            total, success_count, skipped_count, error_count, total_orig_size, total_new_sizes
        )


class QueueListDialog(QDialog):
    """최적화 대상 이미지 목록을 보여주고 선택 항목을 제외할 수 있는 팝업 창"""

    def __init__(self, queued_files: list[Path], parent=None, theme: str = "dark", lang: str = "ko"):
        super().__init__(parent)
        self.queued_files = queued_files
        self.selected_indices: set[int] = set()
        self.theme = theme
        self.lang = lang

        count = len(self.queued_files)
        self.setWindowTitle(I18N[lang]["queue_dlg_title"].format(count=count))
        self.resize(720, 500)
        self.setMinimumSize(480, 320)
        self.setStyleSheet(LIGHT_STYLE if theme == "light" else DARK_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # 상단 설명 라벨 및 팁
        header_layout = QHBoxLayout()
        self.lbl_info = QLabel(I18N[lang]["queue_dlg_info"].format(count=count))
        self.lbl_info.setStyleSheet(
            "color: #2563eb; font-weight: bold; font-size: 11pt;"
            if theme == "light"
            else "color: #38bdf8; font-weight: bold; font-size: 11pt;"
        )
        self.lbl_hint = QLabel(I18N[lang]["queue_dlg_hint"])
        self.lbl_hint.setStyleSheet(
            "color: #059669; font-size: 9.5pt; font-weight: 500;"
            if theme == "light"
            else "color: #4ade80; font-size: 9.5pt; font-weight: 500;"
        )

        header_layout.addWidget(self.lbl_info)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_hint)
        layout.addLayout(header_layout)

        # 테이블 위젯
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(I18N[lang]["queue_dlg_headers"])
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )
        # 단일/다중 클릭 시 직관적인 토글을 위해 NoSelection 모드로 두고 직접 색상 관리
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setCursor(Qt.CursorShape.PointingHandCursor)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.cellClicked.connect(self.on_cell_clicked)
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        layout.addWidget(self.table)

        self.populate_table()

        # 하단 제어 버튼
        btn_layout = QHBoxLayout()
        self.btn_select_all = QPushButton(I18N[lang]["queue_dlg_btn_all"])
        self.btn_select_all.clicked.connect(self.select_all_items)

        self.btn_deselect_all = QPushButton(I18N[lang]["queue_dlg_btn_deselect"])
        self.btn_deselect_all.clicked.connect(self.deselect_all_items)

        self.btn_remove_selected = QPushButton(I18N[lang]["queue_dlg_btn_remove"])
        self.btn_remove_selected.setStyleSheet("""
            QPushButton:enabled {
                background-color: #7f1d1d;
                color: #ffffff;
                border: 1px solid #ef4444;
                font-weight: bold;
            }
            QPushButton:enabled:hover {
                background-color: #991b1b;
            }
        """)
        self.btn_remove_selected.clicked.connect(self.remove_selected)

        self.btn_close = QPushButton(I18N[lang]["queue_dlg_btn_close"])
        self.btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_select_all)
        btn_layout.addWidget(self.btn_deselect_all)
        btn_layout.addWidget(self.btn_remove_selected)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

        self.update_action_buttons()

    def populate_table(self):
        self.table.setRowCount(0)
        for idx, file_path in enumerate(self.queued_files, start=1):
            row = self.table.rowCount()
            self.table.insertRow(row)

            size_str = (
                format_bytes(file_path.stat().st_size)
                if file_path.exists()
                else "0 B"
            )
            self.table.setItem(row, 0, QTableWidgetItem(str(idx)))
            self.table.setItem(row, 1, QTableWidgetItem(file_path.name))
            self.table.setItem(row, 2, QTableWidgetItem(size_str))
            self.table.setItem(row, 3, QTableWidgetItem(str(file_path.parent)))

            self.update_row_style(row)

    def update_row_style(self, row: int):
        """선택 여부에 따라 행의 글자색(초록색), 배경색, 볼드 여부 및 체크 표시 토글"""
        is_selected = row in self.selected_indices

        if self.theme == "light":
            fg_color = QColor("#059669") if is_selected else QColor("#1e293b")
            bg_color = QColor("#ecfdf5") if is_selected else QColor("#ffffff")
        else:
            fg_color = QColor("#4ade80") if is_selected else QColor("#f1f5f9")
            bg_color = QColor("#143823") if is_selected else QColor("#161922")

        font = self.table.font()
        font.setBold(is_selected)

        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item:
                item.setForeground(fg_color)
                item.setBackground(bg_color)
                item.setFont(font)

        # 1번째 열(#)에 체크 아이콘 표시
        item_idx = self.table.item(row, 0)
        if item_idx:
            prefix = "✅ " if is_selected else ""
            item_idx.setText(f"{prefix}{row + 1}")

    def on_cell_clicked(self, row: int, column: int):
        """행 클릭 시 선택 상태 토글 (재선택 시 선택 해제)"""
        if row in self.selected_indices:
            self.selected_indices.remove(row)
        else:
            self.selected_indices.add(row)

        self.update_row_style(row)
        self.update_action_buttons()

    def on_cell_double_clicked(self, row: int, column: int):
        """더블 클릭 시 해당 폴더 탐색기 열기 (더블클릭 중 발생한 클릭 토글은 원복)"""
        if row in self.selected_indices:
            self.selected_indices.remove(row)
        else:
            self.selected_indices.add(row)
        self.update_row_style(row)
        self.update_action_buttons()

        if 0 <= row < len(self.queued_files):
            target_path = self.queued_files[row]
            if target_path.exists():
                pa.open_folder(target_path.parent)

    def select_all_items(self):
        """전체 항목을 초록색(선택 상태)으로 지정"""
        self.selected_indices = set(range(len(self.queued_files)))
        for r in range(self.table.rowCount()):
            self.update_row_style(r)
        self.update_action_buttons()

    def deselect_all_items(self):
        """전체 항목 선택 해제"""
        self.selected_indices.clear()
        for r in range(self.table.rowCount()):
            self.update_row_style(r)
        self.update_action_buttons()

    def update_action_buttons(self):
        """선택된 개수에 따라 제외 버튼 텍스트 및 활성화 상태 갱신"""
        count = len(self.selected_indices)
        if count > 0:
            self.btn_remove_selected.setText(I18N[self.lang]["queue_dlg_btn_remove_n"].format(count=count))
            self.btn_remove_selected.setEnabled(True)
        else:
            self.btn_remove_selected.setText(I18N[self.lang]["queue_dlg_btn_remove"])
            self.btn_remove_selected.setEnabled(False)

    def remove_selected(self):
        """선택된 초록색 항목들을 대기 목록에서 제외"""
        if not self.selected_indices:
            QMessageBox.information(
                self,
                I18N[self.lang]["queue_dlg_no_selection_title"],
                I18N[self.lang]["queue_dlg_no_selection_text"],
            )
            return

        for r in sorted(self.selected_indices, reverse=True):
            if 0 <= r < len(self.queued_files):
                self.queued_files.pop(r)

        self.selected_indices.clear()
        self.populate_table()
        self.lbl_info.setText(I18N[self.lang]["queue_dlg_info"].format(count=len(self.queued_files)))
        self.update_action_buttons()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.remove_selected()
        else:
            super().keyPressEvent(event)


class AboutLicenseDialog(QDialog):
    """앱 정보, 자체 라이선스 및 제3자 오픈소스 라이선스 고지 대화상자"""

    def __init__(self, parent=None, theme: str = "dark", lang: str = "ko"):
        super().__init__(parent)
        self.theme = theme
        self.lang = lang

        self.setWindowTitle(I18N[lang]["about_dlg_title"])
        self.resize(680, 560)
        self.setMinimumSize(520, 400)
        self.setStyleSheet(LIGHT_STYLE if theme == "light" else DARK_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # 상단 헤더
        header_layout = QHBoxLayout()
        lbl_title = QLabel("Image Optimizer  <span style='font-size: 10pt; color: #38bdf8;'>v1.0.4</span>")
        lbl_title.setStyleSheet(
            "font-size: 14pt; font-weight: bold; color: #1e293b;"
            if theme == "light"
            else "font-size: 14pt; font-weight: bold; color: #f8fafc;"
        )
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # 라이선스 및 크레딧 내용 브라우저
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        bg_col = "#ffffff" if theme == "light" else "#0f131a"
        text_col = "#334155" if theme == "light" else "#cbd5e1"
        border_col = "#e2e8f0" if theme == "light" else "#252d3d"
        browser.setStyleSheet(
            f"QTextBrowser {{ background-color: {bg_col}; color: {text_col}; "
            f"border: 1px solid {border_col}; border-radius: 8px; padding: 12px; font-size: 9.5pt; }}"
        )

        browser.setHtml(self._get_about_html(theme, lang))
        layout.addWidget(browser)

        # 하단 버튼 영역
        btn_bar = QHBoxLayout()
        btn_repo = QPushButton(I18N[lang]["about_dlg_btn_repo"])
        btn_repo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_repo.clicked.connect(self._open_repo)

        btn_doc = QPushButton(I18N[lang]["about_dlg_btn_file"])
        btn_doc.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_doc.clicked.connect(self._open_license_file)

        btn_close = QPushButton(I18N[lang]["about_dlg_btn_close"])
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.accept)

        btn_bar.addWidget(btn_repo)
        btn_bar.addWidget(btn_doc)
        btn_bar.addStretch()
        btn_bar.addWidget(btn_close)
        layout.addLayout(btn_bar)

    def _get_about_html(self, theme: str, lang: str) -> str:
        link_col = "#2563eb" if theme == "light" else "#38bdf8"
        h_col = "#0f172a" if theme == "light" else "#f1f5f9"
        sub_col = "#475569" if theme == "light" else "#94a3b8"

        if lang == "ko":
            return f"""
            <div style='line-height: 1.5;'>
                <h3 style='color: {h_col}; margin-bottom: 4px;'>Image Optimizer (Source-Available Freeware)</h3>
                <p style='color: {sub_col}; margin-top: 0px;'>저작권 (c) 2026 smin987. All rights reserved.<br>
                공식 저장소: <a href='https://github.com/smin987/ImageOptimizer' style='color: {link_col};'>https://github.com/smin987/ImageOptimizer</a></p>

                <hr style='border: 0; border-top: 1px solid #334155; margin: 12px 0;'>

                <h4 style='color: {h_col}; margin-bottom: 6px;'>1. 소프트웨어 라이선스 정책</h4>
                <ul style='margin-top: 4px;'>
                    <li><b>컴파일 바이너리 (Freeware)</b>: 공식 배포되는 실행 파일(.exe, .dmg, .deb 등)은 개인, 교육 기관, 비영리 단체, 상업/기업 사용자 누구나 <b>100% 영구 무료</b>로 업무에 자유롭게 사용할 수 있습니다.</li>
                    <li><b>소스코드 (Source-Available)</b>: 개인 연구, 학습, 보안 감사 및 공식 저장소 기여(PR) 목적의 로컬 수정은 허용됩니다. 단, <b>영리 단체 및 기업 사용자의 소스코드 수정 및 커스텀 빌드 제작은 엄격히 금지</b>되며(공식 바이너리 사용 필수), 경쟁 제품 출시 목적의 수정 및 무단 배포는 금지됩니다. (제3자 오픈소스의 경우 해당 라이선스 고지를 따릅니다.)</li>
                </ul>

                <h4 style='color: {h_col}; margin-bottom: 6px;'>2. 사용된 제3자 오픈소스 소프트웨어 (Third-Party OSS)</h4>
                <p style='color: {sub_col};'>본 애플리케이션은 검증된 우수한 오픈소스 생태계의 소프트웨어와 라이브러리를 기반으로 제작되었습니다.</p>
                <table style='width: 100%; border-collapse: collapse; margin-top: 6px;'>
                    <tr style='border-bottom: 1px solid #475569;'>
                        <th style='text-align: left; padding: 4px;'>컴포넌트</th>
                        <th style='text-align: left; padding: 4px;'>라이선스</th>
                        <th style='text-align: left; padding: 4px;'>저작권자 / 비고</th>
                    </tr>
                    <tr>
                        <td style='padding: 5px;'><b>PySide6 (Qt 6)</b></td>
                        <td style='padding: 5px;'><a href='https://www.gnu.org/licenses/lgpl-3.0.html' style='color: {link_col};'>LGPLv3</a></td>
                        <td style='padding: 5px;'>The Qt Company Ltd. (GUI 프레임워크)</td>
                    </tr>
                    <tr>
                        <td style='padding: 5px;'><b>Pillow</b></td>
                        <td style='padding: 5px;'><a href='https://github.com/python-pillow/Pillow/blob/main/LICENSE' style='color: {link_col};'>HPND</a></td>
                        <td style='padding: 5px;'>Jeffrey A. Clark and contributors (이미지 코어)</td>
                    </tr>
                    <tr>
                        <td style='padding: 5px;'><b>└ libwebp</b></td>
                        <td style='padding: 5px;'>BSD 3-Clause</td>
                        <td style='padding: 5px;'>Google Inc. (WebP 인코더/디코더)</td>
                    </tr>
                    <tr>
                        <td style='padding: 5px;'><b>└ libjpeg-turbo</b></td>
                        <td style='padding: 5px;'>IJG / BSD-3</td>
                        <td style='padding: 5px;'>libjpeg-turbo Project (JPEG 코덱)</td>
                    </tr>
                    <tr>
                        <td style='padding: 5px;'><b>Send2Trash</b></td>
                        <td style='padding: 5px;'><a href='https://github.com/arsenetar/send2trash/blob/master/LICENSE' style='color: {link_col};'>BSD 3-Clause</a></td>
                        <td style='padding: 5px;'>Virgil Dupras and contributors (휴지통 이동)</td>
                    </tr>
                    <tr>
                        <td style='padding: 5px;'><b>Python Runtime</b></td>
                        <td style='padding: 5px;'><a href='https://docs.python.org/3/license.html' style='color: {link_col};'>PSF License</a></td>
                        <td style='padding: 5px;'>Python Software Foundation</td>
                    </tr>
                    <tr>
                        <td style='padding: 5px;'><b>PyInstaller</b></td>
                        <td style='padding: 5px;'>GPLv2 with Exception</td>
                        <td style='padding: 5px;'>PyInstaller Team (부트로더 패키징)</td>
                    </tr>
                </table>

                <h4 style='color: {h_col}; margin-bottom: 6px; margin-top: 14px;'>3. LGPLv3 컴플라이언스 및 라이브러리 교체 권리 안내</h4>
                <p style='color: {sub_col};'>
                    GNU LGPLv3 조건에 따라, 사용자는 본 프로그램에 포함된 PySide6/Qt 라이브러리를 자체 수정한 버전으로 교체하여 디버깅 및 실행할 수 있는 권리를 가집니다.<br>
                    Image Optimizer는 전체 소스코드가 공개되어 있으므로, 저장소를 클론(Clone)하여 독립된 파이썬 가상환경에서 원하는 버전의 Qt 및 PySide6를 설치해 실행하실 수 있습니다.<br>
                    상세 라이선스 고지는 배포 디렉터리의 <code>THIRD_PARTY_LICENSES.md</code> 문서를 참조해 주십시오.
                </p>
            </div>
            """
        else:
            return f"""
            <div style='line-height: 1.5;'>
                <h3 style='color: {h_col}; margin-bottom: 4px;'>Image Optimizer (Source-Available Freeware)</h3>
                <p style='color: {sub_col}; margin-top: 0px;'>Copyright (c) 2026 smin987. All rights reserved.<br>
                Official Repository: <a href='https://github.com/smin987/ImageOptimizer' style='color: {link_col};'>https://github.com/smin987/ImageOptimizer</a></p>

                <hr style='border: 0; border-top: 1px solid #334155; margin: 12px 0;'>

                <h4 style='color: {h_col}; margin-bottom: 6px;'>1. Licensing Terms</h4>
                <ul style='margin-top: 4px;'>
                    <li><b>Compiled Binaries (Freeware)</b>: Officially distributed executables (.exe, .dmg, .deb, etc.) are <b>100% free</b> for individuals, non-profits, educational use, and <b>commercial/corporate enterprises of any size</b>.</li>
                    <li><b>Source Code (Source-Available)</b>: Free for personal research, educational study, and Pull Requests. However, <b>modifying or creating custom builds of the Source Code by commercial/corporate entities is strictly prohibited</b> (commercial users must use the official free binaries). Modifying the code to release competing products is strictly prohibited. (Third-party open-source components follow their respective license notices.)</li>
                </ul>

                <h4 style='color: {h_col}; margin-bottom: 6px;'>2. Third-Party Open Source Components</h4>
                <p style='color: {sub_col};'>This software builds upon and bundles several open-source libraries:</p>
                <table style='width: 100%; border-collapse: collapse; margin-top: 6px;'>
                    <tr style='border-bottom: 1px solid #475569;'>
                        <th style='text-align: left; padding: 4px;'>Component</th>
                        <th style='text-align: left; padding: 4px;'>License</th>
                        <th style='text-align: left; padding: 4px;'>Copyright / Role</th>
                    </tr>
                    <tr>
                        <td style='padding: 5px;'><b>PySide6 (Qt 6)</b></td>
                        <td style='padding: 5px;'><a href='https://www.gnu.org/licenses/lgpl-3.0.html' style='color: {link_col};'>LGPLv3</a></td>
                        <td style='padding: 5px;'>The Qt Company Ltd. (GUI Framework)</td>
                    </tr>
                    <tr>
                        <td style='padding: 5px;'><b>Pillow</b></td>
                        <td style='padding: 5px;'><a href='https://github.com/python-pillow/Pillow/blob/main/LICENSE' style='color: {link_col};'>HPND</a></td>
                        <td style='padding: 5px;'>Jeffrey A. Clark and contributors (Image Engine)</td>
                    </tr>
                    <tr>
                        <td style='padding: 5px;'><b>└ libwebp</b></td>
                        <td style='padding: 5px;'>BSD 3-Clause</td>
                        <td style='padding: 5px;'>Google Inc. (WebP Codec)</td>
                    </tr>
                    <tr>
                        <td style='padding: 5px;'><b>└ libjpeg-turbo</b></td>
                        <td style='padding: 5px;'>IJG / BSD-3</td>
                        <td style='padding: 5px;'>libjpeg-turbo Project (JPEG Codec)</td>
                    </tr>
                    <tr>
                        <td style='padding: 5px;'><b>Send2Trash</b></td>
                        <td style='padding: 5px;'><a href='https://github.com/arsenetar/send2trash/blob/master/LICENSE' style='color: {link_col};'>BSD 3-Clause</a></td>
                        <td style='padding: 5px;'>Virgil Dupras and contributors (Safe Trash)</td>
                    </tr>
                    <tr>
                        <td style='padding: 5px;'><b>Python Runtime</b></td>
                        <td style='padding: 5px;'><a href='https://docs.python.org/3/license.html' style='color: {link_col};'>PSF License</a></td>
                        <td style='padding: 5px;'>Python Software Foundation</td>
                    </tr>
                    <tr>
                        <td style='padding: 5px;'><b>PyInstaller</b></td>
                        <td style='padding: 5px;'>GPLv2 with Exception</td>
                        <td style='padding: 5px;'>PyInstaller Team (Bootloader Packaging)</td>
                    </tr>
                </table>

                <h4 style='color: {h_col}; margin-bottom: 6px; margin-top: 14px;'>3. LGPLv3 Relinking Compliance Notice</h4>
                <p style='color: {sub_col};'>
                    In accordance with GNU LGPLv3, you are free to replace or relink the PySide6/Qt libraries with your own modified versions for debugging purposes.<br>
                    Because Image Optimizer source code is available on GitHub, you can clone the repository and run it with any custom Qt installation in a virtual environment.<br>
                    For complete attribution texts, please consult <code>THIRD_PARTY_LICENSES.md</code> included in the installation directory.
                </p>
            </div>
            """

    def _open_repo(self):
        try:
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl("https://github.com/smin987/ImageOptimizer"))
        except Exception:
            pass

    def _open_license_file(self):
        target = resource_path("THIRD_PARTY_LICENSES.md")
        if not target.exists():
            target = resource_path("LICENSE")
        if target.exists():
            pa.open_in_file_manager(target)
        else:
            self._open_repo()


class MainWindow(QWidget):
    """메인 애플리케이션 윈도우"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Optimizer")
        self.resize(720, 680)
        self.setMinimumSize(420, 380)

        # 앱 아이콘 설정 (Windows 작업표시줄 및 창 좌측 상단)
        icon_path = get_resource_path("assets/icon.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.queued_files: list[Path] = []
        self.worker: Optional[ConversionWorker] = None
        self.last_output_dir: Optional[Path] = None
        self.current_theme = "light"  # 기본 테마: 라이트(기본)
        self.current_lang = "ko"      # 기본 언어: 한국어
        self.lang = self.current_lang
        self.last_stat_result = None
        self.is_log_expanded = False       # 실시간 로그 접힘/펼침 상태 (기본값: 접힘)
        self.is_settings_expanded = False  # 변환 설정 접힘/펼침 상태 (기본값: 접힘)

        self.init_ui()

    def init_ui(self):
        # 창 크기가 작아져도 스크롤 가능하도록 루트 스크롤 영역 구성
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # 0. 최상단 미니 헤더 (앱 브랜딩, 언어 전환, 테마 전환 버튼)
        header_bar = QHBoxLayout()
        header_bar.setContentsMargins(2, 2, 2, 2)

        lbl_brand = QLabel("🚀 Image Optimizer")
        lbl_brand.setStyleSheet("font-size: 13pt; font-weight: bold; background: transparent;")

        lbl_badge = QLabel("v1.0")
        lbl_badge.setStyleSheet("""
            background-color: rgba(37, 99, 235, 0.12);
            color: #2563eb;
            font-size: 8.5pt;
            font-weight: bold;
            padding: 2px 7px;
            border-radius: 4px;
        """)

        self.btn_sponsor = QPushButton("💖 후원하기")
        self.btn_sponsor.setObjectName("btn_sponsor")
        self.btn_sponsor.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sponsor.clicked.connect(self.open_sponsor_page)

        self.btn_about = QPushButton(I18N[self.current_lang]["btn_about"])
        self.btn_about.setObjectName("btn_about")
        self.btn_about.setToolTip(I18N[self.current_lang]["btn_about_tip"])
        self.btn_about.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_about.clicked.connect(self.show_about_dialog)

        self.btn_lang_toggle = QPushButton("🌐 English")
        self.btn_lang_toggle.setObjectName("btn_lang_toggle")
        self.btn_lang_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang_toggle.clicked.connect(self.toggle_language)

        self.btn_theme_toggle = QPushButton("🌙 다크 모드로 전환")
        self.btn_theme_toggle.setObjectName("btn_theme_toggle")
        self.btn_theme_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme_toggle.clicked.connect(self.toggle_theme)

        header_bar.addWidget(lbl_brand)
        header_bar.addWidget(lbl_badge)
        header_bar.addStretch()
        header_bar.addWidget(self.btn_sponsor)
        header_bar.addWidget(self.btn_about)
        header_bar.addWidget(self.btn_lang_toggle)
        header_bar.addWidget(self.btn_theme_toggle)
        main_layout.addLayout(header_bar)

        # 0-1. 최상단 앱 안내 설명 카드
        self.desc_card = QFrame()
        desc_layout = QHBoxLayout(self.desc_card)
        desc_layout.setContentsMargins(6, 4, 6, 4)
        desc_layout.setSpacing(10)

        lbl_desc_icon = QLabel("💡")
        lbl_desc_icon.setStyleSheet(
            "font-size: 16pt; background: transparent; border: none;"
        )
        lbl_desc_icon.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.lbl_desc_text = QLabel(
            "원본 이미지를 웹사이트 게시전용으로 최적화하여 경량화된 이미지로 변경해주는 도구입니다.\n"
            "원본 이미지와 화질차이는 거의 없지만 최대 90% 정도의 이미지 용량을 줄일 수 있습니다. "
            "('이미지 품질' 설정값에 따라 달라질 수 있음)\n"
            "※ 애니메이션 GIF도 WebP로 변환 가능"
        )
        self.lbl_desc_text.setWordWrap(True)

        desc_layout.addWidget(lbl_desc_icon)
        desc_layout.addWidget(self.lbl_desc_text, 1)
        main_layout.addWidget(self.desc_card)

        # 1. 파일 상태 알림 라벨 및 파일 추가 버튼 툴바 (드롭 영역 상단 배치)
        self.lbl_queue_status = QLabel("최적화할 이미지 또는 폴더를 드래그하거나 버튼으로 추가하세요.")
        self.lbl_queue_status.setStyleSheet("color: #8899aa; font-size: 9.5pt; padding: 2px 4px;")
        main_layout.addWidget(self.lbl_queue_status)

        file_btn_layout = QHBoxLayout()
        self.btn_add_files = QPushButton("📄 파일 추가")
        self.btn_add_files.clicked.connect(self.choose_files)
        self.btn_add_folder = QPushButton("📁 폴더 추가")
        self.btn_add_folder.clicked.connect(self.choose_folder)
        self.btn_clear_list = QPushButton("🗑️ 대기 목록 비우기")
        self.btn_clear_list.clicked.connect(self.clear_files)

        self.btn_queue_count = QPushButton("최적화 대상 이미지: 0개 🔍")
        self.btn_queue_count.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_queue_count.setToolTip("클릭하면 최적화 대상 이미지 전체 목록을 확인하고 개별 제외할 수 있습니다.")
        self.btn_queue_count.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #4da3ff;
                font-weight: bold;
                font-size: 10.5pt;
                border: 1px dashed #3a4a6b;
                border-radius: 6px;
                padding: 5px 10px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #80c0ff;
                background-color: #1e2638;
                border: 1px solid #0070f3;
            }
        """)
        self.btn_queue_count.clicked.connect(self.show_queued_files_dialog)

        file_btn_layout.addWidget(self.btn_add_files)
        file_btn_layout.addWidget(self.btn_add_folder)
        file_btn_layout.addWidget(self.btn_clear_list)
        file_btn_layout.addStretch()
        file_btn_layout.addWidget(self.btn_queue_count)
        main_layout.addLayout(file_btn_layout)

        # 2. 드래그 앤 드롭 영역
        self.drop_area = DropAreaWidget()
        self.drop_area.files_dropped.connect(self.on_files_added)
        main_layout.addWidget(self.drop_area)

        # 2. 작업 액션 버튼 바 ([변환 시작] [작업 중단] [결과 열기] 1:1:1 균등 배치)
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(10)

        self.btn_start = QPushButton("🚀 변환 시작")
        self.btn_start.setObjectName("btn_start")
        self.btn_start.setMinimumHeight(44)
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.clicked.connect(self.start_conversion)

        self.btn_cancel = QPushButton("⏹️ 작업 중단")
        self.btn_cancel.setObjectName("btn_cancel")
        self.btn_cancel.setMinimumHeight(44)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_conversion)

        self.btn_open_folder = QPushButton("📂 결과 열기")
        self.btn_open_folder.setObjectName("btn_open_folder")
        self.btn_open_folder.setMinimumHeight(44)
        self.btn_open_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_folder.setEnabled(False)
        self.btn_open_folder.clicked.connect(self.open_output_folder)

        ctrl_layout.addWidget(self.btn_start, 1)
        ctrl_layout.addWidget(self.btn_cancel, 1)
        ctrl_layout.addWidget(self.btn_open_folder, 1)
        main_layout.addLayout(ctrl_layout)

        # 3. 실시간 진행 상태 및 진행률 바
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(6)
        progress_layout.setContentsMargins(0, 2, 0, 4)

        status_header_layout = QHBoxLayout()
        self.lbl_status = QLabel("파일을 드래그하여 추가한 후 [변환 시작]을 누르세요.")
        self.lbl_status.setStyleSheet("color: #8892b0; font-size: 9.5pt;")
        status_header_layout.addWidget(self.lbl_status)
        status_header_layout.addStretch()

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(20)

        progress_layout.addLayout(status_header_layout)
        progress_layout.addWidget(self.progress_bar)
        main_layout.addLayout(progress_layout)

        # 3. 변환 설정 패널 (모던 카드 형태)
        self.settings_card = QFrame()
        self.settings_card.setObjectName("settings_card")
        settings_card_layout = QVBoxLayout(self.settings_card)
        settings_card_layout.setContentsMargins(16, 12, 16, 12)
        settings_card_layout.setSpacing(6)

        # 설정 헤더 (접이식 토글 버튼)
        settings_header_layout = QHBoxLayout()
        settings_header_layout.setContentsMargins(0, 0, 0, 0)
        self.btn_toggle_settings = QPushButton("▼ ⚙️ 설정")
        self.btn_toggle_settings.setObjectName("btn_toggle_settings")
        self.btn_toggle_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_settings.clicked.connect(self.toggle_settings_section)
        settings_header_layout.addWidget(self.btn_toggle_settings)
        settings_header_layout.addStretch()
        settings_card_layout.addLayout(settings_header_layout)

        # 설정 세부 내용 컨테이너 (접힘/펼침 대상 - 초기값: 접힘)
        self.settings_body = QWidget()
        self.settings_body.setVisible(False)
        settings_layout = QVBoxLayout(self.settings_body)
        settings_layout.setContentsMargins(0, 4, 0, 0)
        settings_layout.setSpacing(10)

        # 2-1. 포맷 선택 (모던 세그먼트 컨트롤)
        fmt_layout = QHBoxLayout()
        self.lbl_fmt = QLabel("출력 포맷:")
        self.lbl_fmt.setFixedWidth(80)

        seg_frame = QFrame()
        seg_frame.setObjectName("seg_frame")
        seg_frame.setStyleSheet("""
            QFrame#seg_frame {
                background-color: rgba(148, 163, 184, 0.12);
                border-radius: 6px;
                padding: 2px;
            }
        """)
        seg_layout = QHBoxLayout(seg_frame)
        seg_layout.setContentsMargins(2, 2, 2, 2)
        seg_layout.setSpacing(2)

        self.btn_fmt_webp = QPushButton("WebP")
        self.btn_fmt_webp.setProperty("segment", "true")
        self.btn_fmt_webp.setCheckable(True)
        self.btn_fmt_webp.setChecked(True)

        self.btn_fmt_jpg = QPushButton("JPG")
        self.btn_fmt_jpg.setProperty("segment", "true")
        self.btn_fmt_jpg.setCheckable(True)

        self.btn_fmt_both = QPushButton("둘 다(BOTH)")
        self.btn_fmt_both.setProperty("segment", "true")
        self.btn_fmt_both.setCheckable(True)

        self.fmt_group = QButtonGroup(self)
        self.fmt_group.setExclusive(True)
        self.fmt_group.addButton(self.btn_fmt_webp, 1)
        self.fmt_group.addButton(self.btn_fmt_jpg, 2)
        self.fmt_group.addButton(self.btn_fmt_both, 3)

        seg_layout.addWidget(self.btn_fmt_webp)
        seg_layout.addWidget(self.btn_fmt_jpg)
        seg_layout.addWidget(self.btn_fmt_both)

        fmt_layout.addWidget(self.lbl_fmt)
        fmt_layout.addWidget(seg_frame)
        fmt_layout.addStretch()
        settings_layout.addLayout(fmt_layout)

        # 2-2. 품질 슬라이더 및 수치 뱃지
        quality_layout = QHBoxLayout()
        self.lbl_quality = QLabel("이미지 품질:")
        self.lbl_quality.setFixedWidth(80)
        self.slider_quality = QSlider(Qt.Orientation.Horizontal)
        self.slider_quality.setRange(1, 100)
        self.slider_quality.setValue(90)

        self.lbl_quality_val = QLabel("90%")
        self.lbl_quality_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_quality_val.setFixedWidth(50)
        self.lbl_quality_val.setStyleSheet("""
            background-color: rgba(37, 99, 235, 0.14);
            color: #2563eb;
            font-weight: bold;
            font-size: 9.5pt;
            border-radius: 4px;
            padding: 2px 6px;
        """)
        self.slider_quality.valueChanged.connect(
            lambda v: self.lbl_quality_val.setText(f"{v}%")
        )

        quality_layout.addWidget(self.lbl_quality)
        quality_layout.addWidget(self.slider_quality)
        quality_layout.addWidget(self.lbl_quality_val)
        settings_layout.addLayout(quality_layout)

        # 2-3. 리사이즈 모드 (좁은 화면에서도 2줄로 깔끔히 정렬)
        resize_grid = QGridLayout()
        resize_grid.setSpacing(6)
        self.lbl_resize = QLabel("해상도 조절:")
        self.lbl_resize.setFixedWidth(80)

        self.combo_resize_mode = QComboBox()
        self.combo_resize_mode.addItems(
            [
                "선택하세요",
                "최대 가로폭에 맞춤",
                "비율(%) 축소 (Scale %)",
                "🌟 SNS / 인플루언서 맞춤 프리셋",
                "원본 크기 유지 (100%)",
            ]
        )
        self.combo_resize_mode.currentIndexChanged.connect(self.on_resize_mode_changed)

        resize_grid.addWidget(self.lbl_resize, 0, 0)
        resize_grid.addWidget(self.combo_resize_mode, 0, 1, 1, 4)

        # 리사이즈 세부 수치 입력 및 프리셋 버튼 라인 (Row 1)
        self.resize_detail_widget = QWidget()
        resize_detail_layout = QHBoxLayout(self.resize_detail_widget)
        resize_detail_layout.setContentsMargins(0, 0, 0, 0)
        resize_detail_layout.setSpacing(6)

        self.spin_max_width = QSpinBox()
        self.spin_max_width.setRange(100, 16383)
        self.spin_max_width.setValue(1920)
        self.spin_max_width.setSuffix(" px")

        self.spin_scale_percent = QSpinBox()
        self.spin_scale_percent.setRange(1, 100)
        self.spin_scale_percent.setValue(50)
        self.spin_scale_percent.setSuffix(" %")
        self.spin_scale_percent.setVisible(False)

        self.btn_preset_fhd = QPushButton("FHD(1920)")
        self.btn_preset_fhd.setProperty("chip", "true")
        self.btn_preset_fhd.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_preset_fhd.clicked.connect(lambda: self.spin_max_width.setValue(1920))

        self.btn_preset_4k = QPushButton("4K(3840)")
        self.btn_preset_4k.setProperty("chip", "true")
        self.btn_preset_4k.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_preset_4k.clicked.connect(lambda: self.spin_max_width.setValue(3840))

        self.btn_preset_8k = QPushButton("8K(7680)")
        self.btn_preset_8k.setProperty("chip", "true")
        self.btn_preset_8k.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_preset_8k.clicked.connect(lambda: self.spin_max_width.setValue(7680))

        self.btn_preset_50 = QPushButton("50%")
        self.btn_preset_50.setProperty("chip", "true")
        self.btn_preset_50.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_preset_50.clicked.connect(
            lambda: self.spin_scale_percent.setValue(50)
        )
        self.btn_preset_50.setVisible(False)

        self.btn_preset_75 = QPushButton("75%")
        self.btn_preset_75.setProperty("chip", "true")
        self.btn_preset_75.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_preset_75.clicked.connect(
            lambda: self.spin_scale_percent.setValue(75)
        )
        self.btn_preset_75.setVisible(False)

        resize_detail_layout.addWidget(self.spin_max_width)
        resize_detail_layout.addWidget(self.spin_scale_percent)
        resize_detail_layout.addWidget(self.btn_preset_fhd)
        resize_detail_layout.addWidget(self.btn_preset_4k)
        resize_detail_layout.addWidget(self.btn_preset_8k)
        resize_detail_layout.addWidget(self.btn_preset_50)
        resize_detail_layout.addWidget(self.btn_preset_75)
        resize_detail_layout.addStretch()

        resize_grid.addWidget(self.resize_detail_widget, 1, 1, 1, 4)

        # SNS 프리셋 전용 패널 (Row 2)
        self.sns_detail_widget = QWidget()
        sns_main_layout = QVBoxLayout(self.sns_detail_widget)
        sns_main_layout.setContentsMargins(0, 4, 0, 0)
        sns_main_layout.setSpacing(6)

        sns_top_row = QHBoxLayout()
        self.lbl_sns_preset = QLabel("플랫폼:")
        self.lbl_sns_preset.setFixedWidth(50)
        self.combo_sns_preset = QComboBox()
        self.combo_sns_preset.addItems(I18N[self.current_lang]["sns_presets"])

        self.lbl_sns_crop = QLabel("맞춤 방식:")
        self.lbl_sns_crop.setFixedWidth(65)
        self.combo_sns_crop = QComboBox()
        self.combo_sns_crop.addItems(I18N[self.current_lang]["sns_crop_modes"])

        sns_top_row.addWidget(self.lbl_sns_preset)
        sns_top_row.addWidget(self.combo_sns_preset, 3)
        sns_top_row.addWidget(self.lbl_sns_crop)
        sns_top_row.addWidget(self.combo_sns_crop, 2)
        sns_main_layout.addLayout(sns_top_row)

        # 원클릭 퀵 칩 버튼 2줄 배치 (한 줄에 3개씩 정렬)
        sns_chips_grid = QGridLayout()
        sns_chips_grid.setSpacing(6)

        self.btn_sns_yt = QPushButton("🎬 유튜브 (1920×1080)")
        self.btn_sns_yt.setProperty("chip", "true")
        self.btn_sns_yt.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sns_yt.clicked.connect(lambda: self.combo_sns_preset.setCurrentIndex(0))

        self.btn_sns_standard = QPushButton("📱 SNS표준 (1080×1350)")
        self.btn_sns_standard.setProperty("chip", "true")
        self.btn_sns_standard.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sns_standard.clicked.connect(lambda: self.combo_sns_preset.setCurrentIndex(3))

        self.btn_sns_insta_3_4 = QPushButton("📸 인스타 (1080×1440)")
        self.btn_sns_insta_3_4.setProperty("chip", "true")
        self.btn_sns_insta_3_4.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sns_insta_3_4.clicked.connect(lambda: self.combo_sns_preset.setCurrentIndex(5))

        self.btn_sns_insta_feed = QPushButton("🔲 인스타 (1080×1080)")
        self.btn_sns_insta_feed.setProperty("chip", "true")
        self.btn_sns_insta_feed.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sns_insta_feed.clicked.connect(lambda: self.combo_sns_preset.setCurrentIndex(6))

        self.btn_sns_reels = QPushButton("🚀 릴스/쇼츠 (1080×1920)")
        self.btn_sns_reels.setProperty("chip", "true")
        self.btn_sns_reels.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sns_reels.clicked.connect(lambda: self.combo_sns_preset.setCurrentIndex(2))

        self.btn_sns_blog = QPushButton("📝 블로그 (1200px)")
        self.btn_sns_blog.setProperty("chip", "true")
        self.btn_sns_blog.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sns_blog.clicked.connect(lambda: self.combo_sns_preset.setCurrentIndex(9))

        # 1행 (3개)
        sns_chips_grid.addWidget(self.btn_sns_yt, 0, 0)
        sns_chips_grid.addWidget(self.btn_sns_standard, 0, 1)
        sns_chips_grid.addWidget(self.btn_sns_insta_3_4, 0, 2)

        # 2행 (3개)
        sns_chips_grid.addWidget(self.btn_sns_insta_feed, 1, 0)
        sns_chips_grid.addWidget(self.btn_sns_reels, 1, 1)
        sns_chips_grid.addWidget(self.btn_sns_blog, 1, 2)

        sns_main_layout.addLayout(sns_chips_grid)

        self.sns_detail_widget.setVisible(False)
        resize_grid.addWidget(self.sns_detail_widget, 2, 1, 1, 4)

        settings_layout.addLayout(resize_grid)

        # 2-4. 저장 위치 설정 (그리드 2줄 배치)
        dest_grid = QGridLayout()
        dest_grid.setSpacing(6)
        self.lbl_dest = QLabel("저장 위치:")
        self.lbl_dest.setFixedWidth(80)

        self.radio_dest_sub = QRadioButton("하위 'optimized' 폴더")
        self.radio_dest_sub.setChecked(True)
        self.radio_dest_same = QRadioButton("원본과 동일 폴더")
        self.radio_dest_custom = QRadioButton("지정 폴더")

        self.dest_group = QButtonGroup(self)
        self.dest_group.addButton(self.radio_dest_sub, 1)
        self.dest_group.addButton(self.radio_dest_same, 2)
        self.dest_group.addButton(self.radio_dest_custom, 3)
        self.radio_dest_custom.toggled.connect(self.on_dest_custom_toggled)

        self.custom_dir_path: Optional[Path] = None
        self.btn_browse_dest = QPushButton("찾아보기...")
        self.btn_browse_dest.setVisible(False)
        self.btn_browse_dest.clicked.connect(self.choose_custom_dir)

        dest_grid.addWidget(self.lbl_dest, 0, 0)
        dest_grid.addWidget(self.radio_dest_sub, 0, 1)
        dest_grid.addWidget(self.radio_dest_same, 0, 2)
        dest_grid.addWidget(self.radio_dest_custom, 1, 1)
        dest_grid.addWidget(self.btn_browse_dest, 1, 2)
        settings_layout.addLayout(dest_grid)

        # 2-5. 옵션 체크박스들 (세로 2줄로 배치하여 가로폭 최소화)
        opt_chk_layout = QVBoxLayout()
        opt_chk_layout.setSpacing(6)
        self.chk_remove_alpha = QCheckBox(
            "투명 배경(Alpha Channel) 제거"
        )
        self.chk_remove_alpha.setChecked(False)  # 기본값: 해제 (투명 배경 보존)
        self.chk_remove_alpha.setToolTip(
            "체크 시: 투명 배경을 제거하고 흰색 배경으로 합성합니다.\n"
            "체크 해제(기본): 투명 배경(Alpha Channel)을 100% 그대로 유지하며 WebP로 최적화합니다."
        )

        self.chk_delete_orig = QCheckBox("변환 성공 시 원본 파일을 휴지통으로 이동")
        self.chk_delete_orig.setChecked(False)
        self.chk_delete_orig.toggled.connect(self.on_delete_orig_toggled)

        opt_chk_layout.addWidget(self.chk_remove_alpha)
        opt_chk_layout.addWidget(self.chk_delete_orig)
        settings_layout.addLayout(opt_chk_layout)
        settings_card_layout.addWidget(self.settings_body)

        main_layout.addWidget(self.settings_card)

        # 4. 실시간 로그 테이블 (접이식 섹션 - 초기값: 접힘)
        log_header_layout = QHBoxLayout()
        log_header_layout.setContentsMargins(0, 2, 0, 0)

        self.btn_toggle_log = QPushButton("▼ 📋 실시간 변환 로그")
        self.btn_toggle_log.setObjectName("btn_toggle_log")
        self.btn_toggle_log.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_log.clicked.connect(self.toggle_log_section)

        log_header_layout.addWidget(self.btn_toggle_log)
        log_header_layout.addStretch()
        main_layout.addLayout(log_header_layout)

        self.table_log = QTableWidget(0, 5)
        self.table_log.setHorizontalHeaderLabels(
            ["상태", "파일명", "유형", "용량 변화", "절감률"]
        )
        self.table_log.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table_log.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table_log.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table_log.setMinimumHeight(110)
        self.table_log.setVisible(False)
        main_layout.addWidget(self.table_log)

        # 5. 하단 종합 성과 대시보드 카드
        self.stat_card = QFrame()
        self.stat_card.setObjectName("stat_card")
        stat_card_layout = QVBoxLayout(self.stat_card)
        stat_card_layout.setContentsMargins(12, 10, 12, 10)
        stat_card_layout.setSpacing(6)

        stat_header_layout = QHBoxLayout()
        self.lbl_stat_title = QLabel("📊 최적화 성과 대시보드")
        self.lbl_stat_title.setStyleSheet("font-weight: bold; font-size: 10pt;")
        stat_header_layout.addWidget(self.lbl_stat_title)
        stat_header_layout.addStretch()

        self.lbl_stat_count = QLabel("대기 중 (0건)")
        self.lbl_stat_count.setStyleSheet("font-size: 9pt;")
        stat_header_layout.addWidget(self.lbl_stat_count)
        stat_card_layout.addLayout(stat_header_layout)

        stat_metrics_layout = QHBoxLayout()
        stat_metrics_layout.setSpacing(10)

        self.lbl_stat_size = QLabel("용량 변화: -")
        self.lbl_stat_size.setStyleSheet("font-size: 9.5pt;")

        self.lbl_stat_saving = QLabel("🚀 변환을 실행하면 총 용량 절감 성과가 여기에 집계됩니다.")
        self.lbl_stat_saving.setStyleSheet("""
            border-radius: 4px;
            padding: 4px 10px;
            font-weight: 600;
            font-size: 9.5pt;
        """)

        stat_metrics_layout.addWidget(self.lbl_stat_size)
        stat_metrics_layout.addStretch()
        stat_metrics_layout.addWidget(self.lbl_stat_saving)
        stat_card_layout.addLayout(stat_metrics_layout)

        main_layout.addWidget(self.stat_card)
        main_layout.addStretch()

        scroll_area.setWidget(container)
        root_layout.addWidget(scroll_area)

        # 마지막으로 저장된 사용자 설정 불러오기 (기본값: 원본 크기 유지)
        self.load_settings()

    def set_theme(self, theme: str):
        """라이트(기본) 테마와 다크 테마 간 UI 스타일 전환"""
        self.current_theme = theme
        lang = getattr(self, "current_lang", "ko")
        if theme == "light":
            self.setStyleSheet(LIGHT_STYLE)
            self.btn_theme_toggle.setText(I18N[lang]["theme_dark"])
            self.desc_card.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-left: 4px solid #2563eb;
                    border-radius: 6px;
                    padding: 8px 12px;
                }
            """)
            self.lbl_desc_text.setStyleSheet(
                "color: #475569; font-size: 10pt; line-height: 140%; background: transparent; border: none;"
            )
            self.btn_queue_count.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #2563eb;
                    font-weight: bold;
                    font-size: 10.5pt;
                    border: 1px dashed #93c5fd;
                    border-radius: 6px;
                    padding: 5px 10px;
                    text-decoration: underline;
                }
                QPushButton:hover {
                    color: #1d4ed8;
                    background-color: #eff6ff;
                    border: 1px solid #2563eb;
                }
            """)
            if hasattr(self, "stat_card"):
                self.stat_card.setStyleSheet("""
                    QFrame#stat_card {
                        background-color: #ffffff;
                        border: 1px solid #e2e8f0;
                        border-radius: 8px;
                    }
                """)
                self.lbl_stat_title.setStyleSheet("font-weight: bold; font-size: 10pt; color: #2563eb;")
                self.lbl_stat_count.setStyleSheet("font-size: 9pt; color: #64748b;")
                self.lbl_stat_size.setStyleSheet("font-size: 9.5pt; color: #1e293b;")
                if not getattr(self, "_has_stat_data", False):
                    self.lbl_stat_saving.setStyleSheet("""
                        background-color: #f1f5f9;
                        color: #64748b;
                        border-radius: 4px;
                        padding: 4px 10px;
                        font-weight: 600;
                        font-size: 9.5pt;
                    """)
                else:
                    self.lbl_stat_saving.setStyleSheet("""
                        background-color: #ecfdf5;
                        color: #059669;
                        border: 1px solid #a7f3d0;
                        border-radius: 4px;
                        padding: 4px 10px;
                        font-weight: bold;
                        font-size: 9.5pt;
                    """)
            if hasattr(self, "settings_card"):
                self.settings_card.setStyleSheet("""
                    QFrame#settings_card {
                        background-color: #ffffff;
                        border: 1px solid #e2e8f0;
                        border-radius: 8px;
                    }
                """)
            if hasattr(self, "lbl_status"):
                self.lbl_status.setStyleSheet("color: #64748b; font-size: 9.5pt;")
        else:
            self.setStyleSheet(DARK_STYLE)
            self.btn_theme_toggle.setText(I18N[lang]["theme_light"])
            self.desc_card.setStyleSheet("""
                QFrame {
                    background-color: #161922;
                    border: 1px solid #282d3c;
                    border-left: 4px solid #38bdf8;
                    border-radius: 6px;
                    padding: 8px 12px;
                }
            """)
            self.lbl_desc_text.setStyleSheet(
                "color: #94a3b8; font-size: 10pt; line-height: 140%; background: transparent; border: none;"
            )
            self.btn_queue_count.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #38bdf8;
                    font-weight: bold;
                    font-size: 10.5pt;
                    border: 1px dashed #38bdf8;
                    border-radius: 6px;
                    padding: 5px 10px;
                    text-decoration: underline;
                }
                QPushButton:hover {
                    color: #7dd3fc;
                    background-color: #1e293b;
                    border: 1px solid #0284c7;
                }
            """)
            if hasattr(self, "settings_card"):
                self.settings_card.setStyleSheet("""
                    QFrame#settings_card {
                        background-color: #161922;
                        border: 1px solid #282d3c;
                        border-radius: 8px;
                    }
                """)
            if hasattr(self, "lbl_status"):
                self.lbl_status.setStyleSheet("color: #94a3b8; font-size: 9.5pt;")
            if hasattr(self, "stat_card"):
                self.stat_card.setStyleSheet("""
                    QFrame#stat_card {
                        background-color: #161922;
                        border: 1px solid #282d3c;
                        border-radius: 8px;
                    }
                """)
                self.lbl_stat_title.setStyleSheet("font-weight: bold; font-size: 10pt; color: #38bdf8;")
                self.lbl_stat_count.setStyleSheet("font-size: 9pt; color: #94a3b8;")
                self.lbl_stat_size.setStyleSheet("font-size: 9.5pt; color: #f1f5f9;")
                if not getattr(self, "_has_stat_data", False):
                    self.lbl_stat_saving.setStyleSheet("""
                        background-color: #1e2430;
                        color: #94a3b8;
                        border-radius: 4px;
                        padding: 4px 10px;
                        font-weight: 600;
                        font-size: 9.5pt;
                    """)
                else:
                    self.lbl_stat_saving.setStyleSheet("""
                        background-color: #143823;
                        color: #4ade80;
                        border: 1px solid #22c55e;
                        border-radius: 4px;
                        padding: 4px 10px;
                        font-weight: bold;
                        font-size: 9.5pt;
                    """)

        if hasattr(self, "drop_area"):
            self.drop_area.set_theme(theme)

    def toggle_theme(self):
        """다크/라이트 테마 즉각 토글"""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.set_theme(new_theme)
        self.save_settings()

    def set_language(self, lang: str):
        """한국어('ko')와 영어('en') 간 UI 전체 다국어 즉각 전환"""
        self.current_lang = lang if lang in I18N else "ko"
        self.lang = self.current_lang
        i18n = I18N[self.current_lang]

        # 0. 헤더 바 버튼 문구
        if hasattr(self, "btn_sponsor"):
            self.btn_sponsor.setText(i18n.get("btn_sponsor", "💖 Sponsor"))
            self.btn_sponsor.setToolTip(i18n.get("btn_sponsor_tip", ""))
        if hasattr(self, "btn_about"):
            self.btn_about.setText(i18n.get("btn_about", "ℹ️ About / Licenses"))
            self.btn_about.setToolTip(i18n.get("btn_about_tip", ""))
        self.btn_lang_toggle.setText(i18n["lang_toggle"])
        if self.current_theme == "light":
            self.btn_theme_toggle.setText(i18n["theme_dark"])
        else:
            self.btn_theme_toggle.setText(i18n["theme_light"])

        # 0-1. 최상단 설명 카드
        self.lbl_desc_text.setText(i18n["desc_text"])

        # 1. 드롭 영역 및 대기 목록 상태
        if hasattr(self, "drop_area"):
            self.drop_area.set_language(self.current_lang)

        if not self.queued_files:
            self.lbl_queue_status.setText(i18n["queue_status_init"])
        else:
            self.lbl_queue_status.setText(
                i18n["queue_status_added"].format(count=len(self.queued_files))
            )

        self.btn_add_files.setText(i18n["btn_add_files"])
        self.btn_add_folder.setText(i18n["btn_add_folder"])
        self.btn_clear_list.setText(i18n["btn_clear_list"])
        self.update_queue_label()
        self.btn_queue_count.setToolTip(i18n["btn_queue_count_tip"])

        # 2. 변환 설정 패널
        self.update_settings_toggle_button()
        self.lbl_fmt.setText(i18n["lbl_format"])
        self.btn_fmt_both.setText(i18n["fmt_both"])
        self.lbl_quality.setText(i18n["lbl_quality"])
        self.lbl_resize.setText(i18n["lbl_resize"])

        cur_resize_idx = self.combo_resize_mode.currentIndex()
        self.combo_resize_mode.blockSignals(True)
        self.combo_resize_mode.clear()
        self.combo_resize_mode.addItems(i18n["resize_modes"])
        self.combo_resize_mode.setCurrentIndex(cur_resize_idx)
        self.combo_resize_mode.blockSignals(False)

        if hasattr(self, "combo_sns_preset"):
            cur_p_idx = self.combo_sns_preset.currentIndex()
            self.combo_sns_preset.blockSignals(True)
            self.combo_sns_preset.clear()
            self.combo_sns_preset.addItems(i18n["sns_presets"])
            self.combo_sns_preset.setCurrentIndex(cur_p_idx)
            self.combo_sns_preset.blockSignals(False)

        if hasattr(self, "combo_sns_crop"):
            cur_c_idx = self.combo_sns_crop.currentIndex()
            self.combo_sns_crop.blockSignals(True)
            self.combo_sns_crop.clear()
            self.combo_sns_crop.addItems(i18n["sns_crop_modes"])
            self.combo_sns_crop.setCurrentIndex(cur_c_idx)
            self.combo_sns_crop.blockSignals(False)

        if hasattr(self, "lbl_sns_preset"):
            self.lbl_sns_preset.setText(i18n["lbl_sns_preset"])
        if hasattr(self, "lbl_sns_crop"):
            self.lbl_sns_crop.setText(i18n["lbl_sns_crop"])

        self.lbl_dest.setText(i18n["lbl_dest"])
        self.radio_dest_sub.setText(i18n["dest_sub"])
        self.radio_dest_same.setText(i18n["dest_same"])
        self.radio_dest_custom.setText(i18n["dest_custom"])
        self.btn_browse_dest.setText(i18n["btn_browse"])

        self.chk_remove_alpha.setText(i18n["chk_remove_alpha"])
        self.chk_remove_alpha.setToolTip(i18n["chk_remove_alpha_tip"])
        self.chk_delete_orig.setText(i18n["chk_delete_orig"])

        # 3. 작업 제어 버튼 및 상태
        self.btn_start.setText(i18n["btn_start"])
        self.btn_cancel.setText(i18n["btn_cancel"])
        self.btn_open_folder.setText(i18n["btn_open_folder"])
        if not (self.worker and self.worker.isRunning()):
            self.lbl_status.setText(i18n["status_ready"])

        # 4. 실시간 로그 테이블 헤더 및 접기/펼치기 토글
        self.update_log_toggle_button()
        self.table_log.setHorizontalHeaderLabels(i18n["log_headers"])

        # 5. 하단 대시보드 카드
        self.lbl_stat_title.setText(i18n["stat_title"])
        self.update_stat_dashboard()

    def set_settings_expanded(self, expanded: bool, resize_window: bool = True):
        """변환 설정 패널 접힘/펼침 상태 명시적 설정 및 창 높이 동적 조절"""
        if getattr(self, "is_settings_expanded", None) == expanded:
            return
        self.is_settings_expanded = expanded

        if not hasattr(self, "settings_body"):
            return

        if not self.is_settings_expanded:
            # 접기: 현재 settings_body 높이를 기억하고 창 하단을 줄임
            body_h = self.settings_body.height()
            self.saved_settings_height = max(body_h, 240)
            self.settings_body.setVisible(False)
            if resize_window:
                new_h = max(self.minimumHeight(), self.height() - self.saved_settings_height)
                self.resize(self.width(), new_h)
        else:
            # 펼치기: settings_body를 표시하고 기억된 높이만큼 창 하단을 늘림
            self.settings_body.setVisible(True)
            if resize_window:
                expand_h = getattr(self, "saved_settings_height", 260)
                self.resize(self.width(), self.height() + expand_h)

        self.update_settings_toggle_button()
        self.save_settings()

    def toggle_settings_section(self):
        """변환 설정 패널 접기/펼치기 토글"""
        self.set_settings_expanded(not getattr(self, "is_settings_expanded", True), resize_window=True)

    def update_settings_toggle_button(self):
        """변환 설정 토글 버튼 텍스트 업데이트 (다국어 반영)"""
        if not hasattr(self, "btn_toggle_settings"):
            return
        i18n = I18N[self.current_lang]
        expanded = getattr(self, "is_settings_expanded", True)
        base_text = i18n["settings_toggle_hide"] if expanded else i18n["settings_toggle_show"]
        self.btn_toggle_settings.setText(base_text)

    def set_log_expanded(self, expanded: bool, resize_window: bool = True):
        """실시간 로그 테이블 접힘/펼침 상태 명시적 설정 및 창 높이 동적 조절"""
        if getattr(self, "is_log_expanded", None) == expanded:
            return
        self.is_log_expanded = expanded

        if not self.is_log_expanded:
            # 접기: 현재 로그 테이블 높이를 기록하고 창 하단을 줄임
            log_h = self.table_log.height()
            self.saved_log_height = max(log_h, 160)
            self.table_log.setVisible(False)
            if resize_window:
                new_h = max(self.minimumHeight(), self.height() - self.saved_log_height)
                self.resize(self.width(), new_h)
        else:
            # 펼치기: 로그 테이블을 표시하고 기억된 높이만큼 창 하단을 늘림
            self.table_log.setVisible(True)
            if resize_window:
                expand_h = getattr(self, "saved_log_height", 160)
                self.resize(self.width(), self.height() + expand_h)

        self.update_log_toggle_button()
        self.save_settings()

    def toggle_log_section(self):
        """실시간 로그 테이블 접기/펼치기 토글"""
        self.set_log_expanded(not getattr(self, "is_log_expanded", True), resize_window=True)

    def update_log_toggle_button(self):
        """로그 토글 버튼 텍스트 업데이트 (다국어 및 행 개수 반영)"""
        if not hasattr(self, "btn_toggle_log") or not hasattr(self, "table_log"):
            return
        i18n = I18N[self.current_lang]
        expanded = getattr(self, "is_log_expanded", True)
        base_text = i18n["log_toggle_hide"] if expanded else i18n["log_toggle_show"]
        row_count = self.table_log.rowCount()
        if row_count > 0:
            count_suffix = i18n["log_toggle_count_suffix"].format(count=row_count)
            base_text += count_suffix
        self.btn_toggle_log.setText(base_text)

    def toggle_language(self):
        """한국어 ↔ 영어 즉각 토글 및 저장"""
        new_lang = "en" if self.current_lang == "ko" else "ko"
        self.set_language(new_lang)
        self.save_settings()

    def update_stat_dashboard(self):
        """현재 언어 및 테마에 맞춰 하단 대시보드 통계 카드 서식화"""
        i18n = I18N[self.current_lang]
        if not getattr(self, "last_stat_result", None):
            self._has_stat_data = False
            self.lbl_stat_count.setText(i18n["stat_idle_count"])
            self.lbl_stat_size.setText(i18n["stat_size_label"])
            self.lbl_stat_saving.setText(i18n["stat_idle_saving"])
            self.set_theme(self.current_theme)
            return

        total, success, skipped, errors, total_orig_size, total_new_sizes = self.last_stat_result
        if success > 0 and total_orig_size > 0:
            self._has_stat_data = True
            if "WEBP" in total_new_sizes and "JPG" in total_new_sizes:
                webp_sz = total_new_sizes["WEBP"]
                jpg_sz = total_new_sizes["JPG"]
                diff = total_orig_size - webp_sz
                ratio = (diff / total_orig_size) * 100 if total_orig_size > 0 else 0
                new_str = f"WebP {format_bytes(webp_sz)} / JPG {format_bytes(jpg_sz)}"
                saving_str = i18n["stat_saving_both"].format(
                    diff=format_bytes(diff), ratio=ratio
                )
            else:
                new_sz = sum(total_new_sizes.values())
                diff = total_orig_size - new_sz
                ratio = (diff / total_orig_size) * 100 if total_orig_size > 0 else 0
                new_str = format_bytes(new_sz)
                if diff > 0:
                    saving_str = i18n["stat_saving_single"].format(
                        diff=format_bytes(diff), ratio=ratio
                    )
                else:
                    saving_str = i18n["stat_saving_negative"].format(
                        diff=format_bytes(abs(diff)), ratio=ratio
                    )

            self.lbl_stat_count.setText(
                i18n["stat_count_format"].format(
                    total=total, success=success, skipped=skipped, errors=errors
                )
            )
            self.lbl_stat_size.setText(
                i18n["stat_size_format"].format(
                    orig=format_bytes(total_orig_size), new_str=new_str
                )
            )
            self.lbl_stat_saving.setText(saving_str)
        else:
            self._has_stat_data = False
            self.lbl_stat_count.setText(
                i18n["stat_count_format"].format(
                    total=total, success=success, skipped=skipped, errors=errors
                )
            )
            self.lbl_stat_size.setText(i18n["stat_size_label"])
            self.lbl_stat_saving.setText(i18n["stat_no_data"])

        self.set_theme(self.current_theme)
        self.save_settings()

    def load_settings(self):
        """저장된 사용자 설정 불러오기 (없으면 기본값 적용)"""
        # 기본 언어 및 테마 적용
        self.set_language("ko")
        self.set_theme("light")

        # 기본값: 해상도 조절은 '선택하세요' (index 0)
        self.combo_resize_mode.setCurrentIndex(0)
        self.on_resize_mode_changed(0)

        if not SETTINGS_FILE.exists():
            return

        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 0. 언어 복원 (기본값: 'ko')
            saved_lang = data.get("lang", "ko")
            self.set_language(saved_lang)

            # 0-1. 테마 복원 (기본값: 'light')
            saved_theme = data.get("theme", "light")
            self.set_theme(saved_theme)

            # 1. 출력 포맷 복원
            fmt_id = data.get("format_id", 1)
            btn = self.fmt_group.button(fmt_id)
            if btn:
                btn.setChecked(True)

            # 2. 이미지 품질 복원
            q = data.get("quality", 90)
            self.slider_quality.setValue(q)

            # 3. 해상도 조절 모드 및 수치 복원 (기본값: 0)
            resize_idx = data.get("resize_mode_index", 0)
            self.combo_resize_mode.setCurrentIndex(resize_idx)
            self.on_resize_mode_changed(resize_idx)

            self.spin_max_width.setValue(data.get("max_width", 1920))
            self.spin_scale_percent.setValue(data.get("scale_percent", 50))
            if hasattr(self, "combo_sns_preset"):
                self.combo_sns_preset.setCurrentIndex(data.get("sns_preset_index", 0))
            if hasattr(self, "combo_sns_crop"):
                self.combo_sns_crop.setCurrentIndex(data.get("sns_crop_mode_index", 0))

            custom_dir = data.get("custom_dir", "")
            if custom_dir and Path(custom_dir).exists():
                self.custom_dir_path = Path(custom_dir)
                self.radio_dest_custom.setText(I18N[self.current_lang]["dest_custom"])
                self.radio_dest_custom.setToolTip(f"선택된 경로: {self.custom_dir_path}" if self.current_lang == "ko" else f"Selected path: {self.custom_dir_path}")
                self.btn_browse_dest.setToolTip(f"현재 선택된 폴더: {self.custom_dir_path}" if self.current_lang == "ko" else f"Selected folder: {self.custom_dir_path}")
            else:
                self.custom_dir_path = None
                self.radio_dest_custom.setText(I18N[self.current_lang]["dest_custom"])

            # 4. 저장 위치 복원
            dest_id = data.get("dest_id", 1)
            if dest_id == 3 and not self.custom_dir_path:
                dest_id = 1
            dest_btn = self.dest_group.button(dest_id)
            if dest_btn:
                dest_btn.setChecked(True)

            # 5. 체크박스 옵션 복원
            self.chk_remove_alpha.setChecked(data.get("remove_alpha", False))
            self.chk_delete_orig.blockSignals(True)
            self.chk_delete_orig.setChecked(data.get("delete_orig", False))
            self.chk_delete_orig.blockSignals(False)

            # 6. 접힘/펼침 상태 복원 (기본값: False 접힘)
            saved_settings_expanded = data.get("settings_expanded", False)
            self.set_settings_expanded(saved_settings_expanded, resize_window=False)

            saved_log_expanded = data.get("log_expanded", False)
            self.set_log_expanded(saved_log_expanded, resize_window=False)

            # 7. 창 크기 복원
            w = data.get("window_width", 720)
            h = data.get("window_height", 680)
            self.resize(w, h)
        except Exception as e:
            print(f"[Warning] 설정 불러오기 실패: {e}")

    def save_settings(self):
        """현재 UI 설정값을 JSON 파일로 영구 저장"""
        try:
            data = {
                "lang": self.current_lang,
                "theme": self.current_theme,
                "format_id": self.fmt_group.checkedId(),
                "quality": self.slider_quality.value(),
                "resize_mode_index": self.combo_resize_mode.currentIndex(),
                "max_width": self.spin_max_width.value(),
                "scale_percent": self.spin_scale_percent.value(),
                "sns_preset_index": self.combo_sns_preset.currentIndex() if hasattr(self, "combo_sns_preset") else 0,
                "sns_crop_mode_index": self.combo_sns_crop.currentIndex() if hasattr(self, "combo_sns_crop") else 0,
                "dest_id": self.dest_group.checkedId(),
                "custom_dir": str(self.custom_dir_path) if self.custom_dir_path else "",
                "remove_alpha": self.chk_remove_alpha.isChecked(),
                "delete_orig": self.chk_delete_orig.isChecked(),
                "settings_expanded": getattr(self, "is_settings_expanded", False),
                "log_expanded": getattr(self, "is_log_expanded", False),
                "window_width": self.width(),
                "window_height": self.height(),
            }
            SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Warning] 설정 저장 실패: {e}")

    def closeEvent(self, event):
        """앱 종료 시 자동으로 현재 설정 저장"""
        self.save_settings()
        event.accept()

    def on_resize_mode_changed(self, index: int):
        # 0: 선택하세요(none), 1: Max Width, 2: Scale Percent, 3: SNS 맞춤 프리셋, 4: 원본 크기 유지(none)
        is_max_w = index == 1
        is_scale = index == 2
        is_sns = index == 3

        if hasattr(self, "resize_detail_widget"):
            self.resize_detail_widget.setVisible(is_max_w or is_scale)

        self.spin_max_width.setVisible(is_max_w)
        self.btn_preset_fhd.setVisible(is_max_w)
        self.btn_preset_4k.setVisible(is_max_w)
        self.btn_preset_8k.setVisible(is_max_w)

        self.spin_scale_percent.setVisible(is_scale)
        self.btn_preset_50.setVisible(is_scale)
        self.btn_preset_75.setVisible(is_scale)

        if hasattr(self, "sns_detail_widget"):
            self.sns_detail_widget.setVisible(is_sns)

    def on_dest_custom_toggled(self, checked: bool):
        self.btn_browse_dest.setVisible(checked)
        if checked and not self.custom_dir_path:
            self.choose_custom_dir()

    def choose_custom_dir(self):
        folder = QFileDialog.getExistingDirectory(
            self, I18N[self.current_lang]["dlg_select_dest"]
        )
        if folder:
            self.custom_dir_path = Path(folder)
            self.radio_dest_custom.setText(I18N[self.current_lang]["dest_custom"])
            self.radio_dest_custom.setToolTip(f"선택된 경로: {self.custom_dir_path}" if self.current_lang == "ko" else f"Selected path: {self.custom_dir_path}")
            self.btn_browse_dest.setToolTip(f"현재 선택된 폴더: {self.custom_dir_path}" if self.current_lang == "ko" else f"Selected folder: {self.custom_dir_path}")
        else:
            if not self.custom_dir_path:
                self.radio_dest_sub.setChecked(True)

    def on_delete_orig_toggled(self, checked: bool):
        if checked:
            reply = QMessageBox.warning(
                self,
                I18N[self.current_lang]["msg_del_warn_title"],
                I18N[self.current_lang]["msg_del_warn_text"],
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                self.chk_delete_orig.setChecked(False)

    def update_queue_label(self):
        """최적화 대상 이미지 수 라벨 버튼 텍스트 동기화"""
        count = len(self.queued_files)
        self.btn_queue_count.setText(
            I18N[self.current_lang]["btn_queue_count"].format(count=count)
        )

    def show_queued_files_dialog(self):
        """'최적화 대상 이미지' 클릭 시 세부 목록 팝업 창 표시"""
        if not self.queued_files:
            QMessageBox.information(
                self,
                I18N[self.current_lang]["dlg_queue_empty_title"],
                I18N[self.current_lang]["dlg_queue_empty_text"],
            )
            return

        dlg = QueueListDialog(
            self.queued_files, self, theme=self.current_theme, lang=self.current_lang
        )
        dlg.exec()
        self.update_queue_label()

    def on_files_added(self, paths: list[Path]):
        new_targets = collect_target_files(paths)
        existing_set = {p.resolve() for p in self.queued_files}
        added_count = 0
        for t in new_targets:
            if t.resolve() not in existing_set:
                self.queued_files.append(t)
                existing_set.add(t.resolve())
                added_count += 1

        self.update_queue_label()
        self.lbl_queue_status.setText(
            I18N[self.current_lang]["queue_status_added"].format(count=added_count)
        )
        self.lbl_queue_status.setStyleSheet("color: #4da3ff; font-size: 9.5pt; padding: 2px 4px; font-weight: 500;")

    def choose_files(self):
        ext_filter = " ".join([f"*{ext}" for ext in SUPPORTED_EXTENSIONS])
        files, _ = QFileDialog.getOpenFileNames(
            self, I18N[self.current_lang]["dlg_select_files"], "", f"Image Files ({ext_filter})"
        )
        if files:
            self.on_files_added([Path(f) for f in files])

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, I18N[self.current_lang]["dlg_select_folder"]
        )
        if folder:
            self.on_files_added([Path(folder)])

    def clear_files(self):
        """최적화 대상 대기 목록만 초기화 (변환 결과 로그는 보존)"""
        self.queued_files.clear()
        self.update_queue_label()
        self.lbl_queue_status.setText(I18N[self.current_lang]["queue_status_cleared"])
        self.lbl_queue_status.setStyleSheet("color: #ffb74d; font-size: 9.5pt; padding: 2px 4px; font-weight: 500;")

    def get_options_from_ui(self) -> ConversionOptions:
        if self.btn_fmt_webp.isChecked():
            fmts = ["WEBP"]
        elif self.btn_fmt_jpg.isChecked():
            fmts = ["JPG"]
        else:
            fmts = ["WEBP", "JPG"]

        resize_idx = self.combo_resize_mode.currentIndex()
        if resize_idx == 1:
            resize_mode = "max_width"
        elif resize_idx == 2:
            resize_mode = "scale_percent"
        elif resize_idx == 3:
            resize_mode = "sns_preset"
        else:
            resize_mode = "none"

        sns_preset_target = "youtube_thumb"
        if hasattr(self, "combo_sns_preset"):
            p_idx = self.combo_sns_preset.currentIndex()
            if 0 <= p_idx < len(SNS_PRESET_KEYS):
                sns_preset_target = SNS_PRESET_KEYS[p_idx]

        sns_crop_mode = "fit"
        if hasattr(self, "combo_sns_crop"):
            c_idx = self.combo_sns_crop.currentIndex()
            if 0 <= c_idx < len(SNS_CROP_MODE_KEYS):
                sns_crop_mode = SNS_CROP_MODE_KEYS[c_idx]

        if self.radio_dest_same.isChecked():
            output_mode = "same"
        elif self.radio_dest_custom.isChecked():
            output_mode = "custom"
        else:
            output_mode = "sub"

        return ConversionOptions(
            output_formats=fmts,
            quality=self.slider_quality.value(),
            resize_mode=resize_mode,
            max_width=self.spin_max_width.value(),
            scale_percent=self.spin_scale_percent.value(),
            sns_preset_target=sns_preset_target,
            sns_crop_mode=sns_crop_mode,
            remove_alpha=self.chk_remove_alpha.isChecked(),
            delete_originals=self.chk_delete_orig.isChecked(),
            output_mode=output_mode,
            custom_output_dir=self.custom_dir_path,
        )

    def start_conversion(self):
        if not self.queued_files:
            QMessageBox.information(
                self,
                I18N[self.current_lang]["msg_no_files_title"],
                I18N[self.current_lang]["msg_no_files_text"],
            )
            return

        self.save_settings()
        options = self.get_options_from_ui()
        self.btn_start.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.btn_open_folder.setEnabled(False)
        self.progress_bar.setValue(0)
        self.table_log.setRowCount(0)
        self.update_log_toggle_button()

        # 마지막 출력 폴더 기억용
        if options.output_mode == "custom" and options.custom_output_dir:
            self.last_output_dir = options.custom_output_dir
        elif options.output_mode == "sub":
            self.last_output_dir = (
                self.queued_files[0].parent / options.subfolder_name
            )
        else:
            self.last_output_dir = self.queued_files[0].parent

        self.worker = ConversionWorker(self.queued_files, options)
        self.worker.progress.connect(self.on_worker_progress)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def cancel_conversion(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.lbl_status.setText(I18N[self.current_lang]["status_cancelling"])
            self.btn_cancel.setEnabled(False)

    def on_worker_progress(self, current: int, total: int, res: FileResult):
        pct = int((current / total) * 100)
        self.progress_bar.setValue(pct)
        self.lbl_status.setText(
            I18N[self.current_lang]["status_progress"].format(
                name=res.file_path.name, cur=current, total=total
            )
        )

        row = self.table_log.rowCount()
        self.table_log.insertRow(row)

        if res.status == "success":
            status_item = QTableWidgetItem(I18N[self.current_lang]["log_done"])
            status_item.setForeground(QColor("#4caf50"))
            tag_text = res.tag
            orig_txt = format_bytes(res.orig_size)
            new_txt = ", ".join(
                [f"{fmt}: {format_bytes(sz)}" for fmt, sz in res.new_sizes.items()]
            )
            size_text = f"{orig_txt} -> {new_txt}"
            # 대표 절감률
            first_sz = next(iter(res.new_sizes.values()))
            reduc = (1 - (first_sz / res.orig_size)) * 100
            reduc_text = I18N[self.current_lang]["log_saving_suffix"].format(reduc=reduc)
        elif res.status == "skipped":
            status_item = QTableWidgetItem(I18N[self.current_lang]["log_skipped"])
            status_item.setForeground(QColor("#ffb74d"))
            tag_text = res.note or I18N[self.current_lang]["log_alpha_note"]
            size_text = format_bytes(res.orig_size)
            reduc_text = "-"
        else:
            status_item = QTableWidgetItem(I18N[self.current_lang]["log_error"])
            status_item.setForeground(QColor("#ef5350"))
            tag_text = res.error_message or I18N[self.current_lang]["log_error"]
            size_text = format_bytes(res.orig_size)
            reduc_text = "-"

        self.table_log.setItem(row, 0, status_item)
        self.table_log.setItem(row, 1, QTableWidgetItem(res.file_path.name))
        self.table_log.setItem(row, 2, QTableWidgetItem(tag_text))
        self.table_log.setItem(row, 3, QTableWidgetItem(size_text))
        self.table_log.setItem(row, 4, QTableWidgetItem(reduc_text))
        self.table_log.scrollToBottom()
        self.update_log_toggle_button()

    def on_worker_finished(
        self,
        total: int,
        success: int,
        skipped: int,
        errors: int,
        total_orig_size: int,
        total_new_sizes: dict,
    ):
        self.btn_start.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.btn_open_folder.setEnabled(True)
        self.progress_bar.setValue(100)

        msg = I18N[self.current_lang]["msg_done_text"].format(
            total=total, success=success, skipped=skipped, errors=errors
        )
        self.lbl_status.setText(msg)

        # 마지막 통계 결과를 보관 (언어 변경 시 다시 렌더링할 수 있도록)
        self.last_stat_result = (total, success, skipped, errors, total_orig_size, total_new_sizes)
        self.update_stat_dashboard()

        QMessageBox.information(self, I18N[self.current_lang]["msg_done_title"], msg)

        # 변환이 완료될 때마다 자동으로 대기 목록 비우기 실행
        if success > 0 or total > 0:
            self.clear_files()
            self.lbl_queue_status.setText(
                I18N[self.current_lang]["queue_status_auto_cleared"]
            )
            self.lbl_queue_status.setStyleSheet(
                "color: #8899aa; font-size: 9.5pt; padding: 2px 4px;"
            )

    def open_output_folder(self):
        if self.last_output_dir and self.last_output_dir.exists():
            pa.open_folder(self.last_output_dir)
        elif self.queued_files:
            pa.open_folder(self.queued_files[0].parent)

    def open_sponsor_page(self):
        """GitHub Sponsors 개발자 후원 페이지 브라우저 열기"""
        url = "https://github.com/sponsors/smin987"
        try:
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            if not QDesktopServices.openUrl(QUrl(url)):
                import webbrowser
                webbrowser.open(url)
        except Exception:
            import webbrowser
            webbrowser.open(url)

    def show_about_dialog(self):
        """앱 정보 및 오픈소스 라이선스 고지 대화상자 표시"""
        dlg = AboutLicenseDialog(parent=self, theme=self.current_theme, lang=self.current_lang)
        dlg.exec()


def main():
    # Windows 환경에서 작업표시줄에 Python 기본 아이콘 대신 전용 앱 아이콘 표시
    if sys.platform == "win32":
        try:
            import ctypes
            myappid = "mycompany.imageoptimizer.app.v1"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    # 고해상도(4K / HiDPI) 모니터 스케일링 정책 활성화
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
