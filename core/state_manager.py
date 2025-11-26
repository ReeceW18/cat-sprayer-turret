"""
Contains types and classes for handling the SystemState including simple configuration variables.

Also contains class for thread safe frame history deque

TODO:
- implement 'global' values stored within system state
"""

import numpy as np
from collections import deque
from enum import auto, StrEnum
from threading import Lock
from typing import Tuple

FrameData = Tuple[np.ndarray, float]

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

class ThreadingDeque:
    def __init__(self, max_length: int):
        self._deque = deque(maxlen=max_length)
        self._lock = Lock()

    def append(self, data):
        with self._lock:
            self._deque.append(data)

    def get_snapshot(self):
        with self._lock:
            return list(self._deque)

    def clear(self):
        with self._lock:
            self._deque.clear()

    def size(self) -> int:
        with self._lock:
            return len(self._deque)