from fastapi import Depends, HTTPException, Request
from backend.models.game_session import Game_Session
from typing import Annotated
 
def get_games(request: Request) -> dict[str, Game_Session]:
    return request.app.state.sessions

def get_game(game_id: str,
             games: Annotated[dict[str, Game_Session], Depends(get_games)]
             ) -> Game_Session:
    game = games.get(game_id)
    
    if game is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return game