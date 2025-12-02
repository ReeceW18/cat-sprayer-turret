"""
Code for controlling hardware that is agnostic to specific hardware type
"""
from enum import StrEnum, auto
from queue import Queue, Empty
from threading import Lock



class HardwareCommand(StrEnum):
    AIM_LEFT = auto()
    AIM_RIGHT = auto()

    FIRE = auto()

    NULL = auto()

class HardwareQueue():
    def __init__(self):
        self._queue = Queue()
        self._lock = Lock()

        self._last_command = HardwareCommand.NULL

    @property
    def current_status(self) -> str:
        with self._lock:
            return self._last_command

    def put(self, command: HardwareCommand):
        with self._lock:
            self._last_command = command
            is_fire = self._purge_stale_moves()
            if is_fire:
                return
            else:
                self._queue.put(command)


    def _purge_stale_moves(self) -> bool:
        '''
        Docstring for _purge_stale_moves
        
        :param self: Description
        :return: true if a fire command is already in list
        :rtype: bool
        '''
        temp_list = []
        try:
            while True:
                item = self._queue.get_nowait()
                if item == HardwareCommand.FIRE:
                    temp_list.append(item)
        except Empty:
            pass

        for item in temp_list:
            self._queue.put(item)
            return True
        return False

    def get(self) -> HardwareCommand:
        return self._queue.get()

    def __str__(self):
        with self._queue.mutex:
            return str(list(self._queue.queue))


