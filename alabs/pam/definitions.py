import enum


################################################################################
class AutoName(enum.Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


################################################################################
class OperationReturnCode(str, AutoName):
    """
    오퍼레이션의 동작 이후 결과에 따라 시나리오의 진행여부를 결정.
    """
    SUCCEED_CONTINUE = enum.auto()
    SUCCEED_ABORT = enum.auto()
    FAILED_CONTINUE = enum.auto()
    FAILED_ABORT = enum.auto()





