# VoxoScribe

*Your voice, transcribed locally.*

A lightweight Windows 11 application that provides real-time speech-to-text dictation using local Whisper models. The app runs in the system tray and types transcribed text directly into the currently focused input field.

## Features

- **Local Processing**: All speech recognition happens on your device - no internet required after initial model download
- **Global Hotkey**: Press `Ctrl+Shift+Space` to start/stop recording from anywhere
- **Multiple Languages**: Support for Dutch, English, and auto-detection
- **System Tray**: Runs quietly in your system tray with status indicators
- **Visual Feedback**: Overlay shows recording and processing status
- **Microphone Selection**: Choose from all available input devices
- **Model Selection**: Choose between base, small, and medium Whisper models

## Installation

### From Release (Recommended)

1. Go to the [Releases](../../releases) page on GitHub
2. Download `VoxoScribe.exe` from the latest release
3. Run the executable (Windows may show SmartScreen warning - click "More info" then "Run anyway")
4. On first run, the app downloads the speech model (~500MB) - this only happens once
5. The app appears in your system tray - right-click to configure

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/voxoscribe.git
cd voxoscribe

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate icons
cd assets
python generate_icons.py
cd ..

# Run the application
python -m src.main
```

## Usage

1. **Start the app**: Run VoxoScribe - it will appear in your system tray
2. **Click in any text field**: Browser, terminal, editor, notepad, etc.
3. **Press the hotkey**: `Ctrl+Shift+Space` (default)
4. **Speak**: You'll see a recording indicator
5. **Stop**: Press the hotkey again or pause speaking for 1.5 seconds
6. **Done**: Your transcribed text is typed into the focused field

## Configuration

Right-click the tray icon to access settings:

- **Microphone**: Select your preferred input device
- **Language**: Choose Dutch, English, or Auto-detect
- **Model**: Select base (fastest), small (balanced), or medium (most accurate)

Settings are saved automatically and persist between sessions.

## System Requirements

- Windows 11 (Windows 10 may work but is not officially supported)
- Python 3.11+ (for running from source)
- ~2GB RAM (when model is loaded)
- ~500MB disk space for speech model

## Technical Details

### Speech Recognition

VoxoScribe uses [faster-whisper](https://github.com/guillaumekln/faster-whisper), a CTranslate2-optimized implementation of OpenAI's Whisper model. This provides:

- Fast transcription (2-3 seconds for ~10 seconds of audio)
- High accuracy for Dutch and English
- Completely offline operation

### Models

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| base | ~150MB | Fastest | Good |
| small | ~500MB | Balanced | Better |
| medium | ~1.5GB | Slower | Best |

### Configuration File

Settings are stored in `%APPDATA%\VoxoScribe\config.json`:

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

## Building

To build the standalone executable:

```bash
pip install -r requirements-build.txt
cd assets && python generate_icons.py && cd ..
pyinstaller voxoscribe.spec
```

The executable will be in the `dist/` folder.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [faster-whisper](https://github.com/guillaumekln/faster-whisper) for the optimized Whisper implementation
- [OpenAI Whisper](https://github.com/openai/whisper) for the original speech recognition model
