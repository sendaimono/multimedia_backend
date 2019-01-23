import enum


class EventType(enum.Enum):
    JOIN_ROOM = 1
    LEAVE_ROOM = 2
    MESSAGE = 3


class ChatEvent:
    room_gid: str
    _e_type: EventType
    data = None

    @property
    def event_type(self) -> str:
        return self._e_type.name.lower()

    def __init__(self, room_gid: str, e_type: EventType, data = None):
        self.room_gid = room_gid
        self._e_type = e_type
        self.data = data

