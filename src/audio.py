import math
import threading
import time
from typing import Optional
import pyaudio


class AudioInput:
    CHUNK = 1024
    CHANNELS = 1
    RATE = 44100

    def __init__(self):
        self._pa = pyaudio
        self._pa_instance = None
        self._stream = None
        self._available = False
        self._level = 0.0
        self._last_error: Optional[str] = None
        self._lock = threading.Lock()
        self._reader_thread: Optional[threading.Thread] = None
        self._running = False

    def _compute_rms(self, frame_bytes: bytes) -> float:
        if not frame_bytes:
            return 0.0
        import struct

        count = len(frame_bytes) // 2
        if count == 0:
            return 0.0
        fmt = "<%dh" % count
        try:
            samples = struct.unpack(fmt, frame_bytes)
        except Exception:
            return 0.0
        sum_sqr = 0.0
        for s in samples:
            v = s / 32768.0
            sum_sqr += v * v
        return math.sqrt(sum_sqr / count)

    def _reader(self):
        while self._running and self._stream:
            try:
                data = self._stream.read(self.CHUNK, exception_on_overflow=False)
                rms = self._compute_rms(data)
                with self._lock:
                    self._level = rms
            except Exception as e:
                with self._lock:
                    self._last_error = str(e)
                time.sleep(0.1)

    def start(self, device_index: Optional[int] = None) -> bool:
        self._last_error = None
        if self._pa is None:
            self._last_error = "PyAudio not available"
            self._available = False
            return False

        try:
            self._pa_instance = self._pa.PyAudio()
            kwargs = dict(
                format=self._pa.paInt16,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK,
            )
            if device_index is not None:
                kwargs["input_device_index"] = int(device_index)

            self._stream = self._pa_instance.open(**kwargs)
        except Exception as e:
            self._last_error = str(e)
            self._available = False
            self._stream = None
            if self._pa_instance:
                try:
                    self._pa_instance.terminate()
                except Exception:
                    pass
                self._pa_instance = None
            return False

        self._running = True
        self._reader_thread = threading.Thread(
            target=self._reader, name="audio-reader", daemon=True
        )
        self._reader_thread.start()
        self._available = True
        return True

    def list_input_devices(self):
        """Return a list of input-capable devices as dicts: {'index': int, 'name': str, 'maxInputChannels': int}.

        This method creates a temporary PyAudio instance to query devices and then terminates it.
        """
        devices = []
        try:
            pa = self._pa.PyAudio()
        except Exception:
            return devices

        try:
            count = pa.get_device_count()
            for i in range(count):
                try:
                    info = pa.get_device_info_by_index(i)
                    if int(info.get("maxInputChannels", 0)) > 0:
                        devices.append(
                            {
                                "index": int(info.get("index", i)),
                                "name": str(info.get("name", "device-" + str(i))),
                                "maxInputChannels": int(
                                    info.get("maxInputChannels", 0)
                                ),
                            }
                        )
                except Exception:
                    continue
        finally:
            try:
                pa.terminate()
            except Exception:
                pass

        return devices

    def stop(self):
        self._running = False
        try:
            if self._stream is not None:
                self._stream.stop_stream()
                self._stream.close()
        except Exception:
            pass
        self._stream = None
        if self._pa_instance is not None:
            try:
                self._pa_instance.terminate()
            except Exception:
                pass
        self._pa_instance = None
        self._available = False

    def update(self, dt: float, cfg: Optional[dict] = None) -> float:
        cfg = cfg or {}
        smoothing = cfg.get("audio_smoothing", cfg.get("audioSmoothing", 0.85))
        with self._lock:
            measured = self._level
            self._level = smoothing * self._level + (1.0 - smoothing) * measured
            return self._level

    def is_available(self) -> bool:
        return self._available

    def get_level(self) -> float:
        with self._lock:
            return float(self._level)

    def get_last_error(self) -> Optional[str]:
        return self._last_error

    def is_speaking(self, cfg: Optional[dict] = None) -> bool:
        cfg = cfg or {}
        threshold = cfg.get("audio_threshold", cfg.get("audioThreshold", 0.02))
        return self.get_level() > threshold
