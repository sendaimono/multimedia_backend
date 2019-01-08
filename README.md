# ChatBackend

This is python **Chalice** project

## Current features

List of features **ChatBackend** provides(in braces are endpoints):

### Register user (/register) POST

**Request body**:
```json
{
	"login": "aaa",
	"password": "password",
	"username": "Mikolaj"
}
```
**Response**:
```json
{
	"ok": true|false
}
```
### Login user (/login) POST
**Request body**:
```json
{
	"login": "aaa",
	"password": "password"
}
```
**Response**:
```json
{
    "ok": true,
    "data": {
        "username": "sendaimono",
        "uuid": "99f0e998-1360-11e9-ab6c-00e04c681690"
    }
}
```
### Create chat room(/create-room) POST
**Request headers**:
```json
{
    "content-type": "application/json",
    "user": "99f0e998-1360-11e9-ab6c-00e04c681690"
}
```
**Request body**:
```json
{}
```
**Response**:
```json
{
    "ok": true,
    "data": {
        "room_gid": "S6VibswP"
    }
}
```
### Send message to room(/send-message) POST
**Request headers**:
```json
{
    "content-type": "application/json",
    "user": "99f0e998-1360-11e9-ab6c-00e04c681690"
}
```
**Request body**:
```json
{
	"room_gid": "wjLJb3Jo",
	"msg": "asdfasdfjkll asdf asdf asdf2!"
}
```
**Response**:
```json
{
    "ok": true|false,
}
```
### Retrieve channel history(/get-room-history) GET
**Request headers**:
```json
{
    "content-type": "application/json",
    "user": "99f0e998-1360-11e9-ab6c-00e04c681690"
}
```
**Request**: 
```
/get-room-history?room_gid=wjLJb3Jo
```
**Response**:
```json
{
    "ok": true,
    "data": [
        {
            "sender": {
                "uuid": "99f0e998-1360-11e9-ab6c-00e04c681690",
                "username": "sendaimono"
            },
            "msg": {
                "msgId": 2,
                "txt": "asdfasdfjkll asdf asdf asdf2!",
                "timestamp": 1546981723.656864
            }
        }
    ]
}
```

## Start from scratch

You need python 3.6 and pip3.6 installed

### Create virtualenv and open it

Do this inside cloned repo(where `app.py` is located)

```bash
$  python3.6 -m pip install virtualenv
$  virtualenv venv
$  source venv/bin/activate
(venv)$  pip install -r requirements.txt
```

### Run migration script for PostgreSQL

Install PosgreSQL server locally, set username to `postgres`(default) and password to `root` and create db `chat` inside it.

Go to folder repo folder and run
```sh
(venv)$ cd db_schema
(venv)$ alembic upgrade head
```

### Run server

In folder where `app.py` is located run:
```sh
(venv)$ chalice local
```