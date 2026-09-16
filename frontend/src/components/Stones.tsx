interface StonesProps {
    gameState: number[][];
    cellSpacing: number;
    offset: number;
    onPlaceStone: (x: number, y: number) => void;
}
function Stones({gameState, cellSpacing, offset, onPlaceStone}: StonesProps) {
    //stone grid svg
    //invisible stone and clickable if board state is 0, else show the stone in its colour according to backend
    //receive updates from backend board state and display stones and their colours as dictated. 
    //draw interactable grid --later maybe can also display ghost stone on hover for player who's turn it is

    const clickRadius: number = cellSpacing * 0.45;
    const stoneRadius: number = clickRadius * 0.9;

    return (
        <>
        {gameState.map((row, y) =>
            row.map((value, x) => {
                const cx = offset + x*cellSpacing
                const cy = offset + y*cellSpacing

                if (value != 0) {
                    return (
                        <circle
                            key={`stone-${x}-${y}`}
                            cx={cx}
                            cy={cy}
                            r={stoneRadius}
                            fill={value == 1 ? "black":"white"}
                            //test and see if an outline is needed
                        />
                    );
                }

                return (
                    <circle
                        key={`lib-${x}-${y}`}
                        cx={cx}
                        cy={cy}
                        r={clickRadius}
                        fill="transparent" //thinking about changing to a ghost stone on hover
                        onClick={() => onPlaceStone(x,y)}
                        style={{ cursor: "pointer" }}
                    />
                );
            }))}
        </>
    );
}

export { Stones };