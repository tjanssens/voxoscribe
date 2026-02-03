"""Speech transcription using faster-whisper for VoxoScribe."""

import threading
from typing import Callable, Optional
import numpy as np

from .config import config


class Transcriber:
    """Handles speech-to-text transcription using faster-whisper."""

    def __init__(self):
        self._model = None
        self._model_name: Optional[str] = None
        self._loading = False
        self._lock = threading.Lock()

    def load_model(self, model_name: Optional[str] = None,
                   on_progress: Optional[Callable[[str], None]] = None) -> bool:
        """Load the Whisper model.

        Args:
            model_name: Model name (base, small, medium) or None for config default
            on_progress: Callback for progress updates

        Returns:
            True if model loaded successfully
        """
        if model_name is None:
            model_name = config.model

        with self._lock:
            if self._loading:
                return False

            if self._model is not None and self._model_name == model_name:
                return True

            self._loading = True

        try:
            if on_progress:
                on_progress(f"Loading model '{model_name}'...")

            from faster_whisper import WhisperModel

            self._model = WhisperModel(
                model_name,
                device="cpu",
                compute_type="int8"
            )
            self._model_name = model_name

            if on_progress:
                on_progress("Model loaded successfully")

            return True
        except Exception as e:
            if on_progress:
                on_progress(f"Error loading model: {e}")
            return False
        finally:
            self._loading = False

    def is_model_loaded(self) -> bool:
        """Check if a model is loaded."""
        return self._model is not None

    def transcribe(self, audio: np.ndarray,
                   language: Optional[str] = None) -> str:
        """Transcribe audio to text.

        Args:
            audio: Audio data as numpy array (float32, 16kHz)
            language: Language code or None for auto-detect/config

        Returns:
            Transcribed text
        """
        if self._model is None:
            self.load_model()

        if self._model is None:
            return ""

        if language is None:
            if config.auto_detect_language:
                language = None
            else:
                language = config.language

        try:
            segments, info = self._model.transcribe(
                audio,
                language=language,
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                    speech_pad_ms=200
                )
            )

            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())

            return " ".join(text_parts)
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""

    def transcribe_async(self, audio: np.ndarray,
                         callback: Callable[[str], None],
                         language: Optional[str] = None) -> None:
        """Transcribe audio asynchronously.

        Args:
            audio: Audio data as numpy array
            callback: Callback with transcribed text
            language: Language code or None
        """
        def _transcribe():
            result = self.transcribe(audio, language)
            callback(result)

        thread = threading.Thread(target=_transcribe, daemon=True)
        thread.start()

    def change_model(self, model_name: str,
                     on_progress: Optional[Callable[[str], None]] = None) -> bool:
        """Change to a different model.

        Args:
            model_name: New model name
            on_progress: Progress callback

        Returns:
            True if successful
        """
        with self._lock:
            self._model = None
            self._model_name = None

        config.model = model_name
        return self.load_model(model_name, on_progress)


transcriber = Transcriber()
