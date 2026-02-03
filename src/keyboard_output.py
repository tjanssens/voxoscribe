"""Keyboard output simulation for VoxoScribe."""

import time
from typing import Optional
from pynput.keyboard import Controller, Key
import pyperclip


class KeyboardOutput:
    """Types text into the active window."""

    def __init__(self):
        self._keyboard = Controller()
        self._typing_delay = 0.01

    def type_text(self, text: str, use_clipboard: bool = False) -> bool:
        """Type text into the active window.

        Args:
            text: Text to type
            use_clipboard: If True, use clipboard paste instead of typing

        Returns:
            True if successful
        """
        if not text:
            return False

        try:
            if use_clipboard:
                return self._paste_text(text)
            else:
                return self._type_text_direct(text)
        except Exception as e:
            print(f"Error typing text: {e}")
            try:
                return self._paste_text(text)
            except Exception:
                return False

    def _type_text_direct(self, text: str) -> bool:
        """Type text character by character.

        Args:
            text: Text to type

        Returns:
            True if successful
        """
        try:
            for char in text:
                self._keyboard.type(char)
                time.sleep(self._typing_delay)
            return True
        except Exception as e:
            print(f"Direct typing error: {e}")
            return False

    def _paste_text(self, text: str) -> bool:
        """Paste text using clipboard.

        Args:
            text: Text to paste

        Returns:
            True if successful
        """
        try:
            old_clipboard = None
            try:
                old_clipboard = pyperclip.paste()
            except Exception:
                pass

            pyperclip.copy(text)
            time.sleep(0.05)

            self._keyboard.press(Key.ctrl)
            self._keyboard.press('v')
            self._keyboard.release('v')
            self._keyboard.release(Key.ctrl)

            time.sleep(0.1)

            if old_clipboard is not None:
                try:
                    pyperclip.copy(old_clipboard)
                except Exception:
                    pass

            return True
        except Exception as e:
            print(f"Paste error: {e}")
            return False

    def press_key(self, key: Key) -> None:
        """Press a special key.

        Args:
            key: Key to press
        """
        self._keyboard.press(key)
        self._keyboard.release(key)


keyboard_output = KeyboardOutput()
