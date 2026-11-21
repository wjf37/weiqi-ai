from uuid import uuid4 #temp until database 
from fastapi import APIRouter, Depends
from backend.schemas import GameResponse, MoveRequest, CreateGameReq
from backend.dependencies import get_game
from backend.game_logic.game import Game
from typing import Annotated

router = APIRouter(
    prefix="/games",
    tags=["Games"]
)

GameDependency = Annotated[Game, Depends(get_game)]

@router.post("", response_model=GameResponse, response_model_exclude_none=True, status_code=201)
def create_game(game_settings: CreateGameReq) -> GameResponse:
    game_id: str = str(uuid4())
    game = Game(size=game_settings.board_size, komi=game_settings.komi) 
    return GameResponse(
        game_id = game_id,
        game_board = game.board,
        next_player = game.current_player,
        game_status=game.state,
        player1_id=game_settings.player1_id,
    )

@router.post("/join/{game_id}")
def join_game(game_id: int):
    pass

@router.post("/{game_id}/move")
def make_move(game_id: int, move_request: MoveRequest):
    pass