from enum import unique

from ..exceptions.enum_core import BaseEnum


# system error level:
# server source  (100xxx)
# destination    (101xxx)
@unique
class SystemErrorEnum(BaseEnum):
    INTERNAL_SYSTEM_ERROR = {"100001": "Service error code out of range, check it out please!"}
    REMOTE_SERVICE_ERROR = {"101001": "System busy(101001)"}
    READ_TIMED_OUT_ERROR = {"101002": "System busy(101002)"}
    DATABASE_ERROR = {"101003": "System busy(101003)"}
    REDIS_ERROR = {"101004": "System busy(101004)"}
