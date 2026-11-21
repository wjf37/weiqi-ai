from fastapi import Depends, HTTPException, Request
from backend.game_logic.game import Game
from typing import Annotated
 
def get_games(request: Request) -> dict[int, Game]:
    return request.app.state.games

def get_game(game_id: int,
             games: Annotated[dict[int, Game], Depends(get_games)]
             ) -> Game:
    game = games.get(game_id)
    
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return game