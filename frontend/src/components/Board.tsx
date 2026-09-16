import { BoardBackground } from "./BoardBackground.tsx";
import { Stones } from "./Stones.tsx";

interface BoardProps {
    size?: number;
    gameState: number[][];
    offset?: number;
    onPlaceStone: (x:number, y:number)=> void;
}

function Board({ size=19, gameState, offset=10, onPlaceStone }: BoardProps) {
    const cellSpacing: number = 80/(size-1)

    return (
        <svg viewBox="0 0 100 100" preserveAspectRatio="XMidYMid" role="img">
        <BoardBackground
            size={size}
            cellSpacing={cellSpacing}
            offset={offset}
        />
        <Stones
            gameState={gameState}
            cellSpacing={cellSpacing}
            offset={offset}
            onPlaceStone={onPlaceStone}
        />
        </svg>
    );
}

export { Board };