from enum import StrEnum, auto

class MoveRejected(StrEnum):
    OUT_OF_BOUNDS = "out_of_bounds"
    WRONG_PLAYER = "wrong_player"
    SUICIDE = "suicide"
    KO = "ko"
    GAME_OVER = "game_over"
    INVALID_COLOUR = "invalid_colour"
    OCCUPIED_POINT = "occupied"

class Error(StrEnum):
    ERROR = "error"