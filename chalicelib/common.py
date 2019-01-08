
class classproperty(object):

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)

class ENV_VARIABLES:
    ABS_PATH = ''

    DATABASE_URL = 'postgres://postgres:root@localhost:5432/chat'

    # @classproperty
    # def DATABASE_URL(cls) -> str:
    #     return f'sqlite:///{ENV_VARIABLES.ABS_PATH}/chat.db'
