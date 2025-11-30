"""
Contains types and classes for handling the SystemState including simple configuration variables.

Also contains class for thread safe frame history deque

TODO:
- Add system variables to systemstate
"""

from collections import deque
from enum import auto, StrEnum
from threading import Lock
from typing import Any

class SystemMode(StrEnum):
    STARTUP = auto()
    SENTRY = auto()
    AIMING = auto()
    FIRE = auto() # TODO: remove if unused
    COOLDOWN = auto()
    SHUTDOWN = auto()

class SystemState():
    """
    This class allows for threads to share system information safely. Contains
    the system mode and other shared variables that use simple types.

    Attributes:
        mode (SystemMode): determines the current system mode
        #TODO add system variables (not constants)
    """
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
    """
    A wrapper class for deque that makes it thread safe.

    TODO:
        - Potentially make child classes that specify type within the deque
    """
    def __init__(self, max_length: int):
        self._deque = deque(maxlen=max_length)
        self._lock = Lock()

    def append(self, data):
        with self._lock:
            self._deque.append(data)

    def get_snapshot(self) -> list[Any]:
        with self._lock:
            return list(self._deque)

    def clear(self):
        with self._lock:
            self._deque.clear()

    def size(self) -> int:
        with self._lock:
            return len(self._deque)