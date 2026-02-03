"""Global hotkey management for VoxoScribe."""

import threading
from typing import Callable, Optional, Set
from pynput import keyboard

from .config import config


class HotkeyManager:
    """Manages global hotkeys."""

    def __init__(self):
        self._listener: Optional[keyboard.Listener] = None
        self._callback: Optional[Callable] = None
        self._current_keys: Set[keyboard.Key] = set()
        self._hotkey_parts: Set[str] = set()
        self._lock = threading.Lock()

    def start(self, callback: Callable) -> None:
        """Start listening for hotkeys.

        Args:
            callback: Function to call when hotkey is pressed
        """
        self._callback = callback
        self._parse_hotkey(config.hotkey)

        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.start()

    def stop(self) -> None:
        """Stop listening for hotkeys."""
        if self._listener:
            self._listener.stop()
            self._listener = None

    def update_hotkey(self, hotkey: str) -> None:
        """Update the hotkey combination.

        Args:
            hotkey: New hotkey string (e.g., "ctrl+shift+space")
        """
        self._parse_hotkey(hotkey)
        config.hotkey = hotkey

    def _parse_hotkey(self, hotkey: str) -> None:
        """Parse hotkey string into components.

        Args:
            hotkey: Hotkey string like "ctrl+shift+space"
        """
        self._hotkey_parts = set()
        parts = hotkey.lower().split('+')

        for part in parts:
            part = part.strip()
            if part:
                self._hotkey_parts.add(part)

    def _on_press(self, key: keyboard.Key) -> None:
        """Handle key press event."""
        key_name = self._get_key_name(key)
        if key_name:
            with self._lock:
                self._current_keys.add(key_name)
                self._check_hotkey()

    def _on_release(self, key: keyboard.Key) -> None:
        """Handle key release event."""
        key_name = self._get_key_name(key)
        if key_name:
            with self._lock:
                self._current_keys.discard(key_name)

    def _get_key_name(self, key: keyboard.Key) -> Optional[str]:
        """Get normalized key name.

        Args:
            key: Key object

        Returns:
            Normalized key name or None
        """
        try:
            if hasattr(key, 'char') and key.char:
                return key.char.lower()

            if hasattr(key, 'name'):
                name = key.name.lower()

                if name in ('ctrl_l', 'ctrl_r'):
                    return 'ctrl'
                if name in ('shift_l', 'shift_r', 'shift'):
                    return 'shift'
                if name in ('alt_l', 'alt_r', 'alt_gr'):
                    return 'alt'
                if name in ('cmd', 'cmd_l', 'cmd_r'):
                    return 'cmd'

                return name
        except Exception:
            pass

        return None

    def _check_hotkey(self) -> None:
        """Check if current keys match the hotkey."""
        if self._hotkey_parts and self._hotkey_parts <= self._current_keys:
            if self._callback:
                threading.Thread(target=self._callback, daemon=True).start()


hotkey_manager = HotkeyManager()
