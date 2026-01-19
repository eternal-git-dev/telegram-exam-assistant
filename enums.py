from enum import IntEnum, Enum

class OperationResult(IntEnum):
    SUCCESS = 1
    EXISTS = -1
    FAILED = -2
    UNKNOWN_ERROR = -3
    NOT_FOUND = -4

class OrderStatus(str, Enum):
    PENDING = "В ожидании"
    COMPLETED = "Завершен"
    CANCELLED = "Отменен"

class AdminDataType(str, Enum):
    UNIVERSITIES = "Университеты"
    SUBJECTS = "Предметы"
    TYPEWORKS = "Типы работ"