from typing import Literal 
from pydantic import BaseModel
from backend.game_logic.game import Game, GameState

class CreateGameReq(BaseModel):
    board_size: Literal[9, 13, 19] = 19
    komi: float = 6.5
    player1_id: int | None = None

class GameResponse(BaseModel):
    game_id: str
    game_board: list[list[int]]
    player1_id: int | None = None #For non-registered users playing locally
    player2_id: int | None = None
    next_player: int
    game_status: GameState

class MoveRequest(BaseModel):
    x: int
    y: int
    colour: int
