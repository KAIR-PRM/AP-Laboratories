import enum


class ControllerStrategy(enum.Enum):
    PID_PURE_PURSUIT = enum.auto()
    LATERAL_LOOKAHEAD_PURE_PURSUIT = enum.auto()
