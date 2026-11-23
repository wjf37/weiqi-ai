from game_logic.game import Game
from dataclasses import dataclass

@dataclass
class Game_Session:
    game_id: str
    game: Game
    player1_id: int | None = None
    player2_id: int | None = None
