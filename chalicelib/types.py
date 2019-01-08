# -*- coding: utf-8 -*-
from typing import Any, Dict, Sequence, Union, List

DICT = Dict[str, Any]
HEADERS = Dict[str, Any]
REQUEST = Dict[str, Any]
ARRAY_REQUEST = List[REQUEST]
EVENT = Dict[str, Any]
EVENTS = Sequence[EVENT]
CONTENT = Dict[str, Union[int, str, Sequence[str]]]
DATA = Union[CONTENT, Sequence[CONTENT]]
RESPONSE = Dict[str, Any]
ASSIGNMENT = Dict[str, Any]
PROGRESS = Sequence[ASSIGNMENT]