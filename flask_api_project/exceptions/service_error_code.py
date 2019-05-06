from enum import unique

from ..exceptions.enum_core import BaseEnum


# service error level(202xxx)
@unique
class ServiceErrorEnum(BaseEnum):
    REQUEST_ERROR = {"202001": "test"}
    SOURCE_HAS_SOLD_OUT = {"202002": "SOURCE HAS SOLD OUT!"}
    NOT_GRABBED = {"202003": "NOT GRABBED!"}
