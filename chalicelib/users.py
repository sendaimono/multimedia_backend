from chalicelib.types import REQUEST, RESPONSE
from chalicelib.common import ENV_VARIABLES
import logging as log
import chalicelib.json_proto as proto
from uuid import uuid1
from chalicelib.database.db import Session, User


def login_user(request: REQUEST) -> RESPONSE:
    for p in ['login', 'password']:
        if not request.get(p):
            return proto.malformed_request(
                'login_user',
                request,
                f'Missing param: {p}')
    login = request.get('login')
    password = request.get('password')
    log.debug(f'login: {login}, password: {password}')
    session = Session()
    try:
        user: User = session.query(User).filter_by(
            login=login, password=password).one_or_none()
        if not user:
            return proto.error(400, 'Login or password is invalid')
        return proto.ok({
            'username': user.username,
            'uuid': user.uuid,
        })
    except Exception as e:
        session.close()
        log.error(e)
        return proto.internal_error('Error while retrieving users')
    finally:
        session.close()


def register_user(request: REQUEST) -> RESPONSE:
    for p in ['login', 'password', 'username']:
        if not request.get(p):
            return proto.malformed_request(
                'register_user',
                request,
                f'Missing param: {p}')
    user = User()
    user.login = request.get('login')
    user.password = request.get('password')
    user.username = request.get('username')
    user.uuid = str(uuid1())
    session = Session()
    try:
        users = session.query(User).filter_by(login=user.login).one_or_none()
    except Exception as e:
        session.close()
        log.error(e)
        return proto.internal_error('Error while retrieving users')

    if users:
        return proto.error(400, 'User already exists')
    try:
        session.add(user)
        session.commit()
        return proto.ok()
    except Exception as e:
        log.error(e)
        return proto.internal_error('Error while registering user')
    finally:
        session.close()
