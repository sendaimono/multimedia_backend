from chalicelib.types import HEADERS
from chalicelib.database.db import Session, User
import logging as log

def validate(uuid: str) -> User:
    if not uuid:
        return None
    session = Session()
    try:
        user: User = session.query(User).filter_by(
            uuid=uuid).one_or_none()
        return user
    except Exception as e:
        log.error(e)
        return None
    finally:
        session.close()

def validate_http(headers: HEADERS):
    uuid = headers.get('authorization')
    return validate(uuid)