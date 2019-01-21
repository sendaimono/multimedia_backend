import enum


class EventType(enum.Enum):
    JOIN = 1
    LEAVE = 2
    NEW_MSG = 3


class ChatEvent:
    user_uuid: str
    room_gid: str
    e_type: EventType
    data = None

    def __init__(self, user_uuid: str, room_gid: str, e_type: EventType, data = None):
        self.user_uuid = user_uuid
        self.room_gid = room_gid
        self.e_type = e_type
        self.data = data

    def to_json(self):
        if self.data:
            # return {
            #     'user_uuid' : self.user_uuid,
            #     'room_gid': self.room_gid,
            #     'e_type': self.e_type.name,
            #     'data': self.data
            # }
            return self.data
        else:
            return {
                'user_uuid' : self.user_uuid,
                'room_gid': self.room_gid,
                'e_type': self.e_type.name,
            }
