# VoxoScribe

*Your voice, transcribed locally.*

A lightweight Windows 11 application that provides real-time speech-to-text dictation using local Whisper models. The app runs in the system tray and types transcribed text directly into the currently focused input field.

## Overview

A lightweight Windows 11 application that provides real-time speech-to-text dictation using local Whisper models. The app runs in the system tray and types transcribed text directly into the currently focused input field.

## Core Requirements

### Functional Requirements

1. **Hotkey Activation**
   - Global hotkey `Ctrl+Shift+Space` to start/stop recording (configurable)
   - When pressed: start listening and show visual feedback
   - When pressed again (or after silence): stop listening, transcribe, and type result

2. **Speech Recognition**
   - Use `faster-whisper` with CTranslate2 for optimized local inference
   - Default model: `small` (good balance speed/accuracy, ~500MB)
   - Support for `base`, `small`, `medium` models (user configurable)
   - Language options: Dutch (nl), English (en), or auto-detect

3. **Text Output**
   - Type transcribed text directly into the currently focused input field
   - Use `pyautogui` or `keyboard` library for simulating keystrokes
   - Support for special characters and punctuation

4. **System Tray Application**
   - Minimize to system tray on startup
   - Tray icon indicates status:
     - Gray: idle
     - Red: recording
     - Yellow: processing
   - Right-click menu:
     - Microphone selection (list all available input devices)
     - Language selection (Dutch / English / Auto)
     - Model selection
     - Settings
     - Exit

5. **Microphone Selection**
   - Detect all available audio input devices on startup
   - Show device names in submenu (e.g., "Headset Microphone", "Laptop Mic", "USB Microphone")
   - Remember selected device between sessions
   - Default to system default microphone if none selected
   - Refresh device list when opening menu (to detect newly connected devices)
   - Show indicator (checkmark) next to currently selected device

6. **Visual Feedback**
   - Small overlay window near cursor or in corner showing:
     - Recording indicator (pulsing dot)
     - "Processing..." when transcribing
   - Auto-hides after text is typed

### Non-Functional Requirements

1. **Performance**
   - Transcription should complete within 2-3 seconds for ~10 seconds of audio
   - Minimal memory footprint when idle (~100MB)
   - Model loaded in memory for instant response

2. **Local Processing**
   - All processing happens locally, no internet required after model download
   - No data sent to external services

3. **Startup**
   - Option to start with Windows (optional, disabled by default)
   - Remember last used language setting

## Technical Specifications

### Technology Stack

- **Language**: Python 3.11+
- **Speech Recognition**: `faster-whisper` (CTranslate2 optimized Whisper)
- **Audio Capture**: `sounddevice` or `pyaudio`
- **GUI Framework**: `pystray` for system tray, `tkinter` for overlay
- **Keyboard Simulation**: `pynput` (for typing output and global hotkeys)
- **Configuration**: JSON config file in user's AppData folder

### Dependencies

```
faster-whisper
sounddevice
numpy
pystray
pillow
pynput
```

### Project Structure

```
voxoscribe/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── audio_recorder.py    # Audio capture logic
│   ├── audio_devices.py     # Microphone detection and selection
│   ├── transcriber.py       # Whisper transcription
│   ├── keyboard_output.py   # Type text into active window
│   ├── tray_app.py          # System tray icon and menu
│   ├── overlay.py           # Visual feedback overlay
│   ├── config.py            # Configuration management
│   └── hotkey_manager.py    # Global hotkey handling
├── assets/
│   ├── icon.ico              # Windows executable icon
│   ├── icon_idle.png
│   ├── icon_recording.png
│   └── icon_processing.png
├── config.json
├── requirements.txt
├── setup.py
└── README.md
```

### Configuration File (config.json)

```json
{
  "hotkey": "ctrl+shift+space",
  "language": "nl",
  "model": "small",
  "microphone": null,
  "auto_detect_language": false,
  "silence_timeout_ms": 1500,
  "start_with_windows": false,
  "show_overlay": true
}
```

> **Note:** `microphone: null` means use system default. When a specific device is selected, this stores the device name or ID.

## User Flow

1. User starts the app → icon appears in system tray
2. User clicks in any input field (browser, terminal, editor, etc.)
3. User presses `Ctrl+Shift+Space`
4. Overlay shows "Listening..." with red recording dot
5. User speaks in Dutch or English
6. User presses hotkey again OR pauses for 1.5 seconds
7. Overlay shows "Processing..."
8. Transcribed text is typed into the input field
9. Overlay disappears, tray icon returns to idle

## Edge Cases to Handle

- No microphone available → show error notification
- Selected microphone disconnected → fall back to system default, show notification
- Model not yet downloaded → prompt to download on first run
- Hotkey conflict with other app → allow customization
- Very long recording (>30s) → process in chunks
- Application in focus doesn't accept keyboard input → copy to clipboard as fallback

## Future Enhancements (Out of Scope for V1)

- Custom vocabulary/terminology support
- Multiple hotkeys for different languages
- Audio history/log
- Punctuation commands ("period", "comma", "new line")
- GPU acceleration option (CUDA)

## Installation (End User)

1. Go to the [Releases](../../releases) page on GitHub
2. Download `VoxoScribe.exe` from the latest release
3. Run the executable (Windows may show SmartScreen warning - click "More info" → "Run anyway")
4. On first run, the app downloads the speech model (~500MB) - this only happens once
5. The app appears in your system tray - right-click to configure

## Development Setup

### First Run Experience

On first run:
1. Check if Whisper model is downloaded
2. If not, show dialog: "Downloading speech model (~500MB). This only happens once."
3. Download model to `~/.cache/huggingface/` (faster-whisper default location)
4. Show success notification when ready

### Testing

Test with:
- Claude Code terminal input
- Browser text fields
- Notepad
- VS Code

### Building Executable

Use PyInstaller to create standalone .exe. This is automated via GitHub Actions.

## CI/CD Pipeline (GitHub Actions)

### Project Structure (Updated)

```
voxoscribe/
├── .github/
│   └── workflows/
│       └── build-release.yml    # Build and release workflow
├── src/
│   └── ...
├── assets/
│   └── ...
├── voxoscribe.spec               # PyInstaller spec file
├── config.json
├── requirements.txt
├── requirements-build.txt       # Build dependencies (pyinstaller)
├── setup.py
└── README.md
```

### GitHub Actions Workflow (.github/workflows/build-release.yml)

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'  # Trigger on version tags like v1.0.0
  workflow_dispatch:  # Manual trigger

jobs:
  build:
    runs-on: windows-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-build.txt
      
      - name: Build executable
        run: |
          pyinstaller voxoscribe.spec
      
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: VoxoScribe-Windows
          path: dist/VoxoScribe.exe
          retention-days: 30

  release:
    needs: build
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/')
    
    permissions:
      contents: write
    
    steps:
      - name: Download artifact
        uses: actions/download-artifact@v4
        with:
          name: VoxoScribe-Windows
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: VoxoScribe.exe
          generate_release_notes: true
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### PyInstaller Spec File (voxoscribe.spec)

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/*.png', 'assets'),
        ('config.json', '.'),
    ],
    hiddenimports=[
        'faster_whisper',
        'ctranslate2',
        'sounddevice',
        'pystray',
        'pynput',
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VoxoScribe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
```

### requirements-build.txt

```
pyinstaller>=6.0
```

### Release Process

1. **Development:** Push code to `main` branch
2. **Create Release:** 
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. **Automatic Build:** GitHub Actions builds the .exe on Windows
4. **Automatic Release:** Creates GitHub Release with downloadable .exe

### Manual Build Trigger

Go to Actions → "Build and Release" → "Run workflow" to build without creating a release.

### Important Notes for Building

1. **Model NOT included in .exe:** The Whisper model (~500MB) is downloaded on first run to keep the executable small (~50MB)

2. **First Run:** User needs internet connection to download the model once

3. **Icon file:** Create `assets/icon.ico` (Windows icon format) for the .exe icon

4. **Code signing (optional):** For trusted installs without Windows SmartScreen warnings, consider signing the .exe with a code signing certificate

## Acceptance Criteria

### Application
- [ ] App starts and shows tray icon
- [ ] Hotkey triggers recording with visual feedback
- [ ] Dutch speech is transcribed correctly
- [ ] English speech is transcribed correctly
- [ ] Text is typed into active input field
- [ ] Language can be switched via tray menu
- [ ] Microphone can be selected via tray menu
- [ ] Selected microphone persists between sessions
- [ ] App can be closed via tray menu
- [ ] Settings persist between sessions

### CI/CD Pipeline
- [ ] GitHub Action triggers on version tag push
- [ ] Builds successfully on windows-latest runner
- [ ] Produces working VoxoScribe.exe artifact
- [ ] Creates GitHub Release with .exe attached
- [ ] Manual workflow dispatch works
- [ ] .exe runs standalone without Python installed
