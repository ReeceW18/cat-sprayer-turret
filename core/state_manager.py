from enum import StrEnum, auto
from threading import Lock
from collections import deque
from typing import Tuple
import numpy as np

FrameData = Tuple[np.ndarray, float, int]

class SystemMode(StrEnum):
    STARTUP = auto()
    SENTRY = auto()
    AIMING = auto()
    FIRE = auto()
    COOLDOWN = auto()
    SHUTDOWN = auto()

class SystemState():
    def __init__(self):
        self.lock = Lock()
        self._mode = SystemMode.STARTUP
        # INSERT OTHER SHARED VARIABLES

    # GETTERS AND SETTERS
    @property
    def mode(self):
        with self.lock:
            return self._mode
        
    @mode.setter
    def mode(self, new_mode: SystemMode):
        if not isinstance(new_mode, SystemMode):
            raise TypeError("Mode must be a SystemMode Enum member.")
        with self.lock:
            self._mode = new_mode

    # OTHER GETTER AND SETTERS 

class RollingFrameBuffer:
    def __init__(self, max_length: int):
        self._deque = deque(maxlen=max_length)
        self._lock = Lock()

    def append(self, data: FrameData):
        with self._lock:
            self._deque.append(data)

    def get_snapshot(self) -> list[FrameData]:
        with self._lock:
            return list(self._deque)

    def clear(self):
        with self._lock:
            self._deque.clear()