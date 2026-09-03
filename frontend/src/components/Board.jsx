function Board({ size, stones }) {
// TODO: change cell size to be calculated from a hook checking the window size when a prototype can be shown
    const windowSize = useWindowSize()
    const cellSize = 40
    const boardSize = size * cellSize

    return (
        <svg width={boardSize} height={boardSize}>
        {/* grid lines */}
        {Array.from({ length: size }, (_, i) => (
            <line
            key={`h-${i}`}
            x1={cellSize / 2} y1={i * cellSize + cellSize / 2}
            x2={boardSize - cellSize / 2} y2={i * cellSize + cellSize / 2}
            stroke="black"
            />
        ))}
        {Array.from({ length: size }, (_, i) => (
            <line
            key={`v-${i}`}
            x1={i * cellSize + cellSize / 2} y1={cellSize / 2}
            x2={i * cellSize + cellSize / 2} y2={boardSize - cellSize / 2}
            stroke="black"
            />
        ))}
        {/* stones */}
        {stones.map((stone) => (
            <circle
            key={`${stone.x}-${stone.y}`}
            cx={stone.x * cellSize + cellSize / 2}
            cy={stone.y * cellSize + cellSize / 2}
            r={cellSize / 2 - 2}
            fill={stone.color === 1 ? "black" : "white"}
            stroke="black"
            />
        ))}
        </svg>
    )
}