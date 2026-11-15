# 🚀 Image Optimizer

<div align="center">

<p>
  <b>English</b> • <a href="README.ko.md"><b>한국어 (Korean)</b></a>
</p>

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-41cd52.svg)](https://www.qt.io/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](#-platform-support)
[![Sponsor](https://img.shields.io/badge/Sponsor-💖-ff69b4.svg)](#-support--sponsorship)

**All-in-one Cross-Platform Image & Animation Optimizer for Web & Desktop**  
*Ultra-efficient WebP / JPG conversion, animated GIF optimization, alpha channel preservation, and smart resizing.*

[Key Features](#-key-features) • [Platform Support](#-platform-support) • [Downloads](#-downloads) • [Build from Source](#-build--run-from-source) • [Sponsor](#-support--sponsorship)

</div>

---

## 🌟 Overview

**Image Optimizer** is an open-source, cross-platform desktop application designed to drastically compress image files by up to **90%** while preserving outstanding visual fidelity. It accelerates website load times, reduces bandwidth usage, and optimizes local storage.

In addition to static formats (`PNG`, `JPG`, `BMP`, `TIFF`, etc.), it fully supports **Animated GIF optimization**, retaining every frame and animation timing while converting them into lightweight **Animated WebP** files.

---

## ✨ Key Features

- ⚡ **Ultra-Efficient Format Conversion**
  - `WebP`: High-compression modern web format (up to 90% size reduction)
  - `JPG`: Highly compatible standard image compression
  - `BOTH`: Generates both WebP and JPG simultaneously with a single click
- 🎞️ **Animated GIF Optimization**
  - Keeps all animation frames and durations intact while converting bulky GIFs to ultra-lightweight **Animated WebP**
  - Optional still-image JPG extraction from the first frame
- 📐 **3 Smart Resizing Modes**
  - **Fit Max Width**: Scales down large images (e.g., 4K, FHD) while preserving the original aspect ratio
  - **Scale %**: Proportionally resizes images by percentage (25%, 50%, 75%, etc.)
  - **Keep Original Size (100%)**: Pure format compression without resolution changes
- 🎨 **Alpha Channel (Transparency) Preservation**
  - Retain 100% transparent backgrounds in WebP or optionally flatten onto solid white
- 🌐 **One-Click Bilingual UI**
  - Instant live toggle between **English** and **한국어 (Korean)** with persistent preferences
- 🌗 **Dark Mode & Light Mode**
  - Modern, elegant themes designed for visual comfort
- 🗑️ **Safe Original File Disposal**
  - Safely sends original files to the **System Trash / Recycle Bin** instead of permanent deletion
- 📊 **Real-Time Savings Dashboard**
  - Tracks total files processed, success rates, cumulative data saved (MB), and percentage reduction in real time
- 💖 **Integrated Sponsor Button**
  - One-click access to the author's GitHub Sponsors page directly from the app header

---

## 💻 Platform Support

| Operating System | Architecture | Binary Format | Support Status |
| :--- | :--- | :--- | :--- |
| **Windows 11 / 10** | x64 (AMD64) | Standalone `.exe` / Installer | ✅ Fully Supported |
| **macOS (Apple Silicon & Intel)** | Universal (M1/M2/M3/M4 & Intel) | Disk Image (`.dmg`) / App Bundle (`.app`) | ✅ Fully Supported |
| **Linux (Ubuntu, Debian, Fedora)** | x86_64 | Standalone ELF Binary | ✅ Fully Supported |
| **Linux (Raspberry Pi, SBCs)** | ARM64 (aarch64) | Standalone ELF Binary | ✅ Fully Supported |

---

## 📥 Downloads

Pre-compiled standalone binaries are available on the **[GitHub Releases](https://github.com/smin987/ImageOptimizer/releases)** page (no Python installation required):

- **Windows**: `ImageOptimizer-windows-x64.exe` (Standalone portable executable)
- **macOS**: `ImageOptimizer-macos.dmg` (Open disk image and drag to Applications)
- **Linux x86_64**: `ImageOptimizer-linux-x86_64` (Make executable: `chmod +x` and run)
- **Linux ARM64**: `ImageOptimizer-linux-arm64` (For Raspberry Pi 4/5, AWS Graviton, ARM SBCs)

---

## 🛠️ Build & Run from Source

### 1. Requirements
- Python 3.10 or higher

### 2. Run Directly
```bash
# Clone the repository
git clone https://github.com/smin987/ImageOptimizer.git
cd ImageOptimizer

# Install dependencies
pip install -r requirements.txt

# Launch application
python main_gui.py
```

### 3. Build Standalone Binaries Locally
- **Windows**:
  ```cmd
  build\build_windows.bat
  ```
- **Linux**:
  ```bash
  chmod +x build/build_linux.sh
  ./build/build_linux.sh
  ```
- **macOS**:
  ```bash
  chmod +x build/build_macos.sh
  ./build/build_macos.sh
  ```

---

## 💖 Support & Sponsorship

**Image Optimizer** is free and open-source software distributed under the **Apache License 2.0**.  
If you find this project valuable, please consider sponsoring the developer. Your support helps maintain the project, improve performance, and build new features! ☕✨

<div align="center">

[![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa?style=for-the-badge&logo=github&logoColor=white)](https://github.com/sponsors/smin987)

**Sponsor Page**: **[https://github.com/sponsors/smin987](https://github.com/sponsors/smin987)**

</div>

---

## 📄 License

This project is licensed under the **[Apache License 2.0](LICENSE)**.  
You are free to use, modify, distribute, and integrate this software for both personal and commercial purposes.
