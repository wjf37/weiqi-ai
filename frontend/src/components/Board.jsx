import { BoardBackground } from "./BoardBackground";
import { Stones } from "./Stones";

function Board({ size=19, gameState, offset=10, onPlaceStone }) {
    const cellSpacing = 80/(size-1)

    return (
        <svg viewBox="0 0 100 100" preserveAspectRatio="XMidYMid" role="img">
        <BoardBackground size={size} cellSpacing={cellSpacing} offset={offset}/>
        <Stones gameState={gameState} cellSpacing={cellSpacing} offset={offset} onPlaceStone={onPlaceStone}/>
        </svg>
    )
}

export { Board }