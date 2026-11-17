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
