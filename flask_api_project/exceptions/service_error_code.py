from enum import unique

from ..exceptions.enum_core import BaseEnum


# service error level(202xxx)
@unique
class ServiceErrorEnum(BaseEnum):
    REQUEST_ERROR = {"202001": "!"}
