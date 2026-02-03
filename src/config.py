"""Configuration management for VoxoScribe."""

import json
import os
from pathlib import Path
from typing import Optional


class Config:
    """Manages application configuration with persistence."""

    DEFAULT_CONFIG = {
        "hotkey": "ctrl+shift+space",
        "language": "nl",
        "model": "small",
        "microphone": None,
        "auto_detect_language": False,
        "silence_timeout_ms": 1500,
        "start_with_windows": False,
        "show_overlay": True
    }

    def __init__(self):
        self._config = self.DEFAULT_CONFIG.copy()
        self._config_path = self._get_config_path()
        self.load()

    def _get_config_path(self) -> Path:
        """Get the configuration file path in AppData."""
        if os.name == 'nt':
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            config_dir = Path(app_data) / 'VoxoScribe'
        else:
            config_dir = Path.home() / '.config' / 'voxoscribe'

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'config.json'

    def load(self) -> None:
        """Load configuration from file."""
        if self._config_path.exists():
            try:
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    for key in self.DEFAULT_CONFIG:
                        if key in loaded:
                            self._config[key] = loaded[key]
            except (json.JSONDecodeError, IOError):
                pass

    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
        except IOError:
            pass

    @property
    def hotkey(self) -> str:
        return self._config["hotkey"]

    @hotkey.setter
    def hotkey(self, value: str) -> None:
        self._config["hotkey"] = value
        self.save()

    @property
    def language(self) -> str:
        return self._config["language"]

    @language.setter
    def language(self, value: str) -> None:
        self._config["language"] = value
        self.save()

    @property
    def model(self) -> str:
        return self._config["model"]

    @model.setter
    def model(self, value: str) -> None:
        self._config["model"] = value
        self.save()

    @property
    def microphone(self) -> Optional[str]:
        return self._config["microphone"]

    @microphone.setter
    def microphone(self, value: Optional[str]) -> None:
        self._config["microphone"] = value
        self.save()

    @property
    def auto_detect_language(self) -> bool:
        return self._config["auto_detect_language"]

    @auto_detect_language.setter
    def auto_detect_language(self, value: bool) -> None:
        self._config["auto_detect_language"] = value
        self.save()

    @property
    def silence_timeout_ms(self) -> int:
        return self._config["silence_timeout_ms"]

    @silence_timeout_ms.setter
    def silence_timeout_ms(self, value: int) -> None:
        self._config["silence_timeout_ms"] = value
        self.save()

    @property
    def start_with_windows(self) -> bool:
        return self._config["start_with_windows"]

    @start_with_windows.setter
    def start_with_windows(self, value: bool) -> None:
        self._config["start_with_windows"] = value
        self.save()

    @property
    def show_overlay(self) -> bool:
        return self._config["show_overlay"]

    @show_overlay.setter
    def show_overlay(self, value: bool) -> None:
        self._config["show_overlay"] = value
        self.save()


config = Config()
