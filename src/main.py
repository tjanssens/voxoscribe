"""Main entry point for VoxoScribe."""

import sys
import threading
import time
from typing import Optional

from .config import config
from .audio_recorder import audio_recorder
from .audio_devices import audio_device_manager
from .transcriber import transcriber
from .keyboard_output import keyboard_output
from .overlay import overlay
from .hotkey_manager import hotkey_manager
from .tray_app import tray_app


class VoxoScribe:
    """Main application controller."""

    def __init__(self):
        self._recording = False
        self._processing = False
        self._running = False
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start the application."""
        self._running = True

        overlay.start()

        self._check_microphone()

        tray_app.show_notification(
            "VoxoScribe",
            "Loading speech model, please wait..."
        )
        self._load_model()

        tray_app.start(
            on_exit=self._on_exit,
            on_language_change=self._on_language_change,
            on_model_change=self._on_model_change,
            on_microphone_change=self._on_microphone_change
        )

        hotkey_manager.start(self._on_hotkey)

        tray_app.show_notification(
            "VoxoScribe Ready",
            f"Press {config.hotkey.replace('+', ' + ').title()} to start dictating"
        )

        self._main_loop()

    def _main_loop(self) -> None:
        """Main application loop."""
        try:
            while self._running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self._on_exit()

    def _load_model(self) -> None:
        """Load the Whisper model."""
        def on_progress(message: str):
            print(message)

        transcriber.load_model(on_progress=on_progress)

    def _check_microphone(self) -> None:
        """Check if selected microphone is available."""
        if config.microphone:
            if not audio_device_manager.is_device_available(config.microphone):
                tray_app.show_notification(
                    "Microphone Not Found",
                    f"'{config.microphone}' not available. Using system default."
                )
                config.microphone = None

    def _on_hotkey(self) -> None:
        """Handle hotkey press."""
        with self._lock:
            if self._processing:
                return

            if self._recording:
                self._stop_recording()
            else:
                self._start_recording()

    def _start_recording(self) -> None:
        """Start recording audio."""
        self._recording = True
        tray_app.set_status('recording')

        if config.show_overlay:
            overlay.show_recording()

        success = audio_recorder.start_recording(
            on_silence=self._on_silence_detected
        )

        if not success:
            self._recording = False
            tray_app.set_status('idle')
            overlay.hide()
            tray_app.show_notification(
                "Recording Failed",
                "Could not start recording. Check your microphone."
            )

    def _stop_recording(self) -> None:
        """Stop recording and start transcription."""
        self._recording = False
        self._processing = True
        tray_app.set_status('processing')

        if config.show_overlay:
            overlay.show_processing()

        audio_data = audio_recorder.stop_recording()

        if audio_data is not None and len(audio_data) > 0:
            transcriber.transcribe_async(
                audio_data,
                callback=self._on_transcription_complete
            )
        else:
            self._on_transcription_complete("")

    def _on_silence_detected(self) -> None:
        """Handle silence detection."""
        with self._lock:
            if self._recording and not self._processing:
                self._stop_recording()

    def _on_transcription_complete(self, text: str) -> None:
        """Handle transcription completion.

        Args:
            text: Transcribed text
        """
        self._processing = False
        tray_app.set_status('idle')
        overlay.hide()

        if text.strip():
            time.sleep(0.1)
            success = keyboard_output.type_text(text.strip())

            if not success:
                keyboard_output.type_text(text.strip(), use_clipboard=True)

    def _on_exit(self) -> None:
        """Handle application exit."""
        self._running = False
        hotkey_manager.stop()
        overlay.stop()
        tray_app.stop()

    def _on_language_change(self, language: Optional[str]) -> None:
        """Handle language change.

        Args:
            language: New language code or None for auto-detect
        """
        pass

    def _on_model_change(self, model: str) -> None:
        """Handle model change.

        Args:
            model: New model name
        """
        tray_app.show_notification(
            "Changing Model",
            f"Loading '{model}' model, please wait..."
        )

        def change():
            transcriber.change_model(model)
            tray_app.show_notification(
                "Model Changed",
                f"Now using '{model}' model"
            )

        threading.Thread(target=change, daemon=True).start()

    def _on_microphone_change(self, device_name: Optional[str]) -> None:
        """Handle microphone change.

        Args:
            device_name: New device name or None for default
        """
        name = device_name if device_name else "System Default"
        tray_app.show_notification(
            "Microphone Changed",
            f"Now using: {name}"
        )


def main():
    """Application entry point."""
    app = VoxoScribe()
    app.start()


if __name__ == '__main__':
    main()
