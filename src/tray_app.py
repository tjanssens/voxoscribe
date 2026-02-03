"""System tray application for VoxoScribe."""

import os
import sys
import threading
from typing import Optional, Callable

from PIL import Image
import pystray
from pystray import MenuItem as Item

from .config import config
from .audio_devices import audio_device_manager


class TrayApp:
    """System tray application with menu."""

    LANGUAGES = [
        ("Nederlands", "nl"),
        ("English", "en"),
        ("Auto-detect", None)
    ]

    MODELS = ["base", "small", "medium"]

    def __init__(self):
        self._icon: Optional[pystray.Icon] = None
        self._status = "idle"
        self._on_exit: Optional[Callable] = None
        self._on_language_change: Optional[Callable] = None
        self._on_model_change: Optional[Callable] = None
        self._on_microphone_change: Optional[Callable] = None
        self._assets_path = self._get_assets_path()

    def _get_assets_path(self) -> str:
        """Get path to assets directory."""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        return os.path.join(base_path, 'assets')

    def _load_icon(self, name: str) -> Image.Image:
        """Load an icon image.

        Args:
            name: Icon name (without extension)

        Returns:
            PIL Image
        """
        icon_path = os.path.join(self._assets_path, f'{name}.png')
        if os.path.exists(icon_path):
            return Image.open(icon_path)

        return self._create_default_icon(name)

    def _create_default_icon(self, status: str) -> Image.Image:
        """Create a default icon programmatically.

        Args:
            status: Status name for color selection

        Returns:
            PIL Image
        """
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))

        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)

        colors = {
            'icon_idle': '#808080',
            'icon_recording': '#ff4444',
            'icon_processing': '#ffaa00'
        }

        color = colors.get(status, '#808080')

        padding = 4
        draw.ellipse(
            [padding, padding, size - padding, size - padding],
            fill=color
        )

        inner_padding = size // 4
        draw.ellipse(
            [inner_padding, inner_padding, size - inner_padding, size - inner_padding],
            fill='white'
        )

        return image

    def start(self, on_exit: Optional[Callable] = None,
              on_language_change: Optional[Callable] = None,
              on_model_change: Optional[Callable] = None,
              on_microphone_change: Optional[Callable] = None) -> None:
        """Start the system tray application.

        Args:
            on_exit: Callback when exit is selected
            on_language_change: Callback when language changes
            on_model_change: Callback when model changes
            on_microphone_change: Callback when microphone changes
        """
        self._on_exit = on_exit
        self._on_language_change = on_language_change
        self._on_model_change = on_model_change
        self._on_microphone_change = on_microphone_change

        icon_image = self._load_icon('icon_idle')

        self._icon = pystray.Icon(
            name='VoxoScribe',
            icon=icon_image,
            title='VoxoScribe - Press Ctrl+Shift+Space to dictate',
            menu=self._create_menu()
        )

        self._icon.run_detached()

    def _create_menu(self) -> pystray.Menu:
        """Create the tray menu."""
        return pystray.Menu(
            Item('Microphone', pystray.Menu(self._get_microphone_items)),
            Item('Language', pystray.Menu(self._get_language_items)),
            Item('Model', pystray.Menu(self._get_model_items)),
            pystray.Menu.SEPARATOR,
            Item('Settings', self._on_settings),
            pystray.Menu.SEPARATOR,
            Item('Exit', self._exit)
        )

    def _get_microphone_items(self) -> tuple:
        """Get microphone menu items dynamically."""
        audio_device_manager.refresh_devices()
        devices = audio_device_manager.get_devices()

        items = []

        items.append(Item(
            'System Default',
            self._make_microphone_callback(None),
            checked=lambda item: config.microphone is None
        ))

        if devices:
            items.append(pystray.Menu.SEPARATOR)

        for device_id, device_name in devices:
            items.append(Item(
                device_name,
                self._make_microphone_callback(device_name),
                checked=lambda item, name=device_name: config.microphone == name
            ))

        return tuple(items)

    def _make_microphone_callback(self, device_name: Optional[str]) -> Callable:
        """Create callback for microphone selection."""
        def callback(icon, item):
            config.microphone = device_name
            if self._on_microphone_change:
                self._on_microphone_change(device_name)
        return callback

    def _get_language_items(self) -> tuple:
        """Get language menu items."""
        items = []

        for display_name, lang_code in self.LANGUAGES:
            if lang_code is None:
                items.append(Item(
                    display_name,
                    self._make_language_callback(None, True),
                    checked=lambda item: config.auto_detect_language
                ))
            else:
                items.append(Item(
                    display_name,
                    self._make_language_callback(lang_code, False),
                    checked=lambda item, lc=lang_code: (
                        not config.auto_detect_language and config.language == lc
                    )
                ))

        return tuple(items)

    def _make_language_callback(self, lang_code: Optional[str],
                                auto_detect: bool) -> Callable:
        """Create callback for language selection."""
        def callback(icon, item):
            config.auto_detect_language = auto_detect
            if lang_code:
                config.language = lang_code
            if self._on_language_change:
                self._on_language_change(lang_code if not auto_detect else None)
        return callback

    def _get_model_items(self) -> tuple:
        """Get model menu items."""
        items = []

        for model_name in self.MODELS:
            items.append(Item(
                model_name.capitalize(),
                self._make_model_callback(model_name),
                checked=lambda item, mn=model_name: config.model == mn
            ))

        return tuple(items)

    def _make_model_callback(self, model_name: str) -> Callable:
        """Create callback for model selection."""
        def callback(icon, item):
            if config.model != model_name:
                config.model = model_name
                if self._on_model_change:
                    self._on_model_change(model_name)
        return callback

    def _on_settings(self, icon, item) -> None:
        """Handle settings menu click."""
        pass

    def _exit(self, icon, item) -> None:
        """Handle exit menu click."""
        if self._on_exit:
            self._on_exit()
        self.stop()

    def stop(self) -> None:
        """Stop the tray application."""
        if self._icon:
            self._icon.stop()

    def set_status(self, status: str) -> None:
        """Set the tray icon status.

        Args:
            status: One of 'idle', 'recording', 'processing'
        """
        self._status = status

        icon_name = f'icon_{status}'
        if self._icon:
            self._icon.icon = self._load_icon(icon_name)

            titles = {
                'idle': 'VoxoScribe - Press Ctrl+Shift+Space to dictate',
                'recording': 'VoxoScribe - Recording...',
                'processing': 'VoxoScribe - Processing...'
            }
            self._icon.title = titles.get(status, titles['idle'])

    def show_notification(self, title: str, message: str) -> None:
        """Show a notification.

        Args:
            title: Notification title
            message: Notification message
        """
        if self._icon:
            self._icon.notify(message, title)


tray_app = TrayApp()
