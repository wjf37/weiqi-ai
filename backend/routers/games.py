from uuid import uuid4 #temp until database 
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from backend.models.game_session import Game_Session
from backend.schemas import GameResponse, MoveRequest, CreateGameReq, JoinGameReq, PassReq
from backend.dependencies import get_game, get_games
from backend.game_logic.game import Game
from backend.game_logic.exceptions import MoveRejected

router = APIRouter(
    prefix="/games",
    tags=["Games"]
)

GameDependency = Annotated[Game_Session, Depends(get_game)]
SessionsDependency = Annotated[dict, Depends(get_games)]

def session_to_response(session: Game_Session) -> GameResponse:
    return GameResponse(
        game_id = session.game_id,
        game_board = session.game.board,
        player1_id = session.player1_id,
        player2_id = session.player2_id,
        game_status = session.game.state,
        turn_num= session.game.turn_counter,
        next_player = session.game.current_player
    )

@router.post(
    "",
    response_model=GameResponse,
    response_model_exclude_none=True,
    status_code=201
)
def create_game(
    game_settings: CreateGameReq,
    games: SessionsDependency
) -> GameResponse:
    game_id: str = str(uuid4())
    game = Game(
        size=game_settings.board_size,
        komi=game_settings.komi
    )
    session = Game_Session(
        game_id=game_id,
        game=game,
        player1_id=game_settings.player1_id
    )
    games[game_id] = session
    return GameResponse(
        game_id = game_id,
        game_board = game.board,
        next_player = game.current_player,
        game_status=game.state,
        turn_num= game.turn_counter,
        player1_id=game_settings.player1_id,
    )

#Not necessary for the prototype so it is only going to be very basic
@router.post(
    "/{game_id}/join",
    response_model=GameResponse
)
def join_game(
    player_id: JoinGameReq,
    session: GameDependency
) -> GameResponse:  
    #if player already part of session
    if player_id in (session.player1_id, session.player2_id):
        return session_to_response(session)
    #check if p2 exists for said match
    if session.player2_id is not None:
        raise HTTPException(
            status_code=409,
            detail="Game is full!",
        )
    #join game
    session.player2_id = player_id.player_id
    return session_to_response(session)
    

@router.post(
    "/{game_id}/move",
    response_model=GameResponse
)
def make_move(
    move_request: MoveRequest,
    existing_game: GameDependency
) -> GameResponse:
    #checks at this point:
    #existing game checked
    #correct player to check
    if existing_game.game.current_player != move_request.colour:
        raise HTTPException(
            status_code=409,
            detail="Not your turn!"
        )
    #send move request to backend
    #see if any problems get passed back e.g. illegal move
    #occupied spaces should be handled at frontend
    rejection_reason = existing_game.game.place_stone((move_request.x, move_request.y),move_request.colour)

    if rejection_reason is not None:
        status_code = 422 if rejection_reason is MoveRejected.OUT_OF_BOUNDS else 409
        raise HTTPException(
            status_code=status_code,
            detail={"reason": rejection_reason.value}
        )
    #once move request goes through send the new board state back
    return session_to_response(existing_game)

@router.post(
    "/{game_id}/pass",
    response_model=GameResponse
)
def pass_turn(pass_req: PassReq, existing_game: GameDependency) -> GameResponse:
    rejection_reason = existing_game.game.pass_turn(pass_req.colour)
    if rejection_reason:
        raise HTTPException(
            status_code=409,
            detail={"reason": rejection_reason.value}
        )
    
    return session_to_response(existing_game)