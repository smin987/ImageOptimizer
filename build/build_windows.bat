@echo off
chcp 65001 > nul
echo ====================================================
echo  Image Optimizer - Windows 11 빌드 스크립트
echo ====================================================

:: 가상환경 활성화 (필요 시)
:: call venv\Scripts\activate

echo [1/3] 필수 패키지 확인 및 설치...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [2/3] PyInstaller 단일 .exe 빌드 시작...
python -m PyInstaller --noconsole ^
            --onefile ^
            --clean ^
            --icon="assets/icon.ico" ^
            --add-data="assets;assets" ^
            --name="ImageOptimizer" ^
            main_gui.py

echo.
echo [3/3] 빌드 완료!
echo 결과 파일 위치: dist\ImageOptimizer.exe
echo ====================================================
pause
