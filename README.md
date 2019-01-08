# ChatBackend

This is python **Chalice** project

## Current features

List of features **ChatBackend** provides(in braces are endpoints):

*   Register user (/register)
*   Login user (/login)

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