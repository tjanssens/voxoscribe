"""Audio device detection and management for VoxoScribe."""

from typing import List, Optional, Tuple
import sounddevice as sd


class AudioDeviceManager:
    """Manages audio input devices."""

    def __init__(self):
        self._cached_devices: List[Tuple[int, str]] = []
        self.refresh_devices()

    def refresh_devices(self) -> List[Tuple[int, str]]:
        """Refresh and return list of available input devices.

        Returns:
            List of tuples (device_id, device_name)
        """
        self._cached_devices = []

        try:
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    name = device['name']
                    self._cached_devices.append((i, name))
        except Exception:
            pass

        return self._cached_devices

    def get_devices(self) -> List[Tuple[int, str]]:
        """Get cached list of input devices.

        Returns:
            List of tuples (device_id, device_name)
        """
        return self._cached_devices

    def get_device_id_by_name(self, name: Optional[str]) -> Optional[int]:
        """Get device ID by name.

        Args:
            name: Device name or None for default

        Returns:
            Device ID or None for default
        """
        if name is None:
            return None

        for device_id, device_name in self._cached_devices:
            if device_name == name:
                return device_id

        return None

    def get_default_device(self) -> Optional[Tuple[int, str]]:
        """Get the default input device.

        Returns:
            Tuple of (device_id, device_name) or None
        """
        try:
            default = sd.query_devices(kind='input')
            if default:
                device_id = sd.default.device[0]
                return (device_id, default['name'])
        except Exception:
            pass

        return None

    def is_device_available(self, name: str) -> bool:
        """Check if a device with the given name is available.

        Args:
            name: Device name to check

        Returns:
            True if device is available
        """
        self.refresh_devices()
        return any(device_name == name for _, device_name in self._cached_devices)


audio_device_manager = AudioDeviceManager()
