# Third-Party Open Source Software Notices

Image Optimizer utilizes several third-party open-source libraries and components. This document provides copyright attributions, license identifiers, and terms as required by their respective licenses.

---

## 1. PySide6 (Qt for Python) / Qt 6

- **Project URL**: [https://wiki.qt.io/Qt_for_Python](https://wiki.qt.io/Qt_for_Python) / [https://www.qt.io/](https://www.qt.io/)
- **Copyright**: Copyright (C) 2026 The Qt Company Ltd. and other contributors.
- **License**: **GNU Lesser General Public License version 3 (LGPL-3.0-only)** / GNU General Public License version 2 / Commercial License
- **License Links**:
  - LGPLv3: [https://www.gnu.org/licenses/lgpl-3.0.html](https://www.gnu.org/licenses/lgpl-3.0.html)
  - GPLv3: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)
- **Compliance & Relinking Information**:
  - Image Optimizer uses PySide6 to provide its user interface.
  - In accordance with the LGPLv3 terms, users have the right to modify the Qt / PySide6 libraries and run this application with the modified versions.
  - Because the source code for Image Optimizer is publicly available at [https://github.com/smin987/ImageOptimizer](https://github.com/smin987/ImageOptimizer), users can install their own custom or updated version of PySide6 into a Python virtual environment and run the application (`python main_gui.py`).
  - Source code for PySide6 and Qt is available at [https://code.qt.io/cgit/pyside/pyside-setup.git](https://code.qt.io/cgit/pyside/pyside-setup.git) and [https://download.qt.io/](https://download.qt.io/).

---

## 2. Pillow (Python Imaging Library Fork)

- **Project URL**: [https://python-pillow.org/](https://python-pillow.org/)
- **Copyright**:
  - Copyright (C) 2010-2026 by Jeffrey A. Clark (Alex) and contributors.
  - Copyright (C) 1997-2011 by Secret Labs AB.
  - Copyright (C) 1995-2011 by Fredrik Lundh.
- **License**: **Historical Permission Notice and Disclaimer (HPND-sell-variant)**
- **License Link**: [https://github.com/python-pillow/Pillow/blob/main/LICENSE](https://github.com/python-pillow/Pillow/blob/main/LICENSE)

### Bundled Codec Libraries in Pillow Wheels
Pre-compiled Pillow wheels dynamically or statically link with underlying open-source codecs:
- **libwebp**: Copyright (C) Google Inc. (BSD-3-Clause)
- **libjpeg-turbo / libjpeg**: Copyright (C) Independent JPEG Group / The libjpeg-turbo Project (IJG / BSD-3-Clause / zlib)
- **zlib**: Copyright (C) Jean-loup Gailly and Mark Adler (zlib License)
- **libpng**: Copyright (C) PNG Development Group (libpng License)
- **libtiff**: Copyright (C) Frank Warmerdam, Andrey Kiselev, and Silicon Graphics (libtiff License)
- **FreeType 2**: Copyright (C) The FreeType Project (FreeType License / GPLv2)
- **HarfBuzz**: Copyright (C) HarfBuzz contributors (MIT License)

---

## 3. send2trash

- **Project URL**: [https://github.com/arsenetar/send2trash](https://github.com/arsenetar/send2trash)
- **Copyright**: Copyright (C) 2010-2026 Virgil Dupras and contributors.
- **License**: **BSD 3-Clause License**
- **License Link**: [https://github.com/arsenetar/send2trash/blob/master/LICENSE](https://github.com/arsenetar/send2trash/blob/master/LICENSE)

---

## 4. Python Runtime (CPython)

- **Project URL**: [https://www.python.org/](https://www.python.org/)
- **Copyright**: Copyright (C) 2001-2026 Python Software Foundation. All rights reserved.
- **License**: **Python Software Foundation (PSF) License Agreement**
- **License Link**: [https://docs.python.org/3/license.html](https://docs.python.org/3/license.html)

---

## 5. PyInstaller

- **Project URL**: [https://pyinstaller.org/](https://pyinstaller.org/)
- **Copyright**: Copyright (C) 2005-2026 PyInstaller Development Team.
- **License**: **GNU General Public License version 2 (GPL-2.0) with Bootloader Exception**
- **Note**: The Bootloader Exception permits distribution of self-contained executables created by PyInstaller under the author's chosen license without requiring the application code to be GPL licensed.

---

## 6. Inno Setup (Windows Installer Builder)

- **Project URL**: [https://jrsoftware.org/isinfo.php](https://jrsoftware.org/isinfo.php)
- **Copyright**: Copyright (C) 1997-2026 Jordan Russell. Portions Copyright (C) 2000-2026 Martijn Laan.
- **License**: **Inno Setup License (Permissive)**


---
---

# 제3자 오픈소스 소프트웨어 라이선스 고지문 (한국어 안내)

Image Optimizer는 여러 제3자 오픈소스 라이브러리 및 컴포넌트를 기반으로 동작합니다. 본 문서는 각 오픈소스 라이선스에 따라 요구되는 저작권 고지, 라이선스 식별자 및 관련 약관을 제공합니다.

---

## 1. PySide6 (Qt for Python) / Qt 6
- **저작권**: Copyright (C) 2026 The Qt Company Ltd. 및 기여자 일동.
- **라이선스**: **GNU Lesser General Public License version 3 (LGPL-3.0-only)**
- **준수 및 리링킹(Relinking) 안내**:
  - Image Optimizer는 사용자 인터페이스(GUI)를 위해 PySide6를 사용합니다.
  - LGPLv3 약관에 따라, 사용자는 Qt/PySide6 라이브러리를 직접 수정하고 수정된 버전으로 본 애플리케이션을 실행할 권리를 가집니다.
  - 본 애플리케이션의 소스코드는 GitHub(https://github.com/smin987/ImageOptimizer)에 공개되어 있으므로, 가상 환경에 커스텀 PySide6를 설치하여 자유롭게 실행할 수 있습니다.

---

## 2. Pillow (파이썬 이미지 처리 라이브러리)
- **저작권**: Copyright (C) 2010-2026 Jeffrey A. Clark 및 기여자 일동.
- **라이선스**: **Historical Permission Notice and Disclaimer (HPND)**
- **번들된 코덱 라이브러리**:
  - libwebp (BSD-3-Clause, Google Inc.)
  - libjpeg-turbo (IJG / BSD-3-Clause)
  - zlib, libpng, libtiff, FreeType 2, HarfBuzz 등 포함.

---

## 3. send2trash (안전 휴지통 삭제)
- **저작권**: Copyright (C) 2010-2026 Virgil Dupras 및 기여자 일동.
- **라이선스**: **BSD 3-Clause License**

---

## 4. Python Runtime (CPython)
- **저작권**: Copyright (C) 2001-2026 Python Software Foundation.
- **라이선스**: **PSF License Agreement**

---

## 5. PyInstaller (실행 파일 패키징)
- **저작권**: Copyright (C) 2005-2026 PyInstaller Development Team.
- **라이선스**: **GPL-2.0 with Bootloader Exception** (독립 실행 파일 제작 시 앱 코드에 GPL 전파 면제)

---

## 6. Inno Setup (Windows 설치 프로그램 제작기)
- **저작권**: Copyright (C) 1997-2026 Jordan Russell.
- **라이선스**: **Inno Setup License (Permissive)**
