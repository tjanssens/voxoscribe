"""Audio recording module for VoxoScribe."""

import threading
import time
from typing import Callable, Optional
import numpy as np
import sounddevice as sd

from .config import config
from .audio_devices import audio_device_manager


class AudioRecorder:
    """Records audio from microphone with silence detection."""

    SAMPLE_RATE = 16000
    CHANNELS = 1
    DTYPE = np.float32
    CHUNK_DURATION = 0.1  # seconds per chunk
    SILENCE_THRESHOLD = 0.01

    def __init__(self):
        self._recording = False
        self._audio_data: list = []
        self._stream: Optional[sd.InputStream] = None
        self._record_thread: Optional[threading.Thread] = None
        self._last_sound_time: float = 0
        self._on_silence_callback: Optional[Callable] = None
        self._lock = threading.Lock()

    def start_recording(self, on_silence: Optional[Callable] = None) -> bool:
        """Start recording audio.

        Args:
            on_silence: Callback when silence is detected

        Returns:
            True if recording started successfully
        """
        if self._recording:
            return False

        self._audio_data = []
        self._on_silence_callback = on_silence
        self._last_sound_time = time.time()

        device_id = audio_device_manager.get_device_id_by_name(config.microphone)

        try:
            self._stream = sd.InputStream(
                samplerate=self.SAMPLE_RATE,
                channels=self.CHANNELS,
                dtype=self.DTYPE,
                device=device_id,
                callback=self._audio_callback,
                blocksize=int(self.SAMPLE_RATE * self.CHUNK_DURATION)
            )
            self._stream.start()
            self._recording = True

            self._record_thread = threading.Thread(target=self._monitor_silence, daemon=True)
            self._record_thread.start()

            return True
        except Exception as e:
            print(f"Error starting recording: {e}")
            return False

    def stop_recording(self) -> Optional[np.ndarray]:
        """Stop recording and return audio data.

        Returns:
            Numpy array of audio data or None
        """
        if not self._recording:
            return None

        self._recording = False

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._lock:
            if self._audio_data:
                return np.concatenate(self._audio_data)

        return None

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._recording

    def _audio_callback(self, indata: np.ndarray, frames: int,
                        time_info: dict, status: sd.CallbackFlags) -> None:
        """Callback for audio stream."""
        if status:
            print(f"Audio callback status: {status}")

        with self._lock:
            self._audio_data.append(indata.copy())

        amplitude = np.abs(indata).mean()
        if amplitude > self.SILENCE_THRESHOLD:
            self._last_sound_time = time.time()

    def _monitor_silence(self) -> None:
        """Monitor for silence and trigger callback."""
        silence_timeout = config.silence_timeout_ms / 1000.0

        while self._recording:
            time.sleep(0.1)

            time_since_sound = time.time() - self._last_sound_time
            if time_since_sound >= silence_timeout and len(self._audio_data) > 0:
                if self._on_silence_callback:
                    self._on_silence_callback()
                break


audio_recorder = AudioRecorder()
