function getStarPoints(size) {
  if (size !== 9 && size !== 13 && size !== 19) {
    return []
  }

  var distance = 3
  if (size == 9) {
     distance = 2
  }
  const last = size - 1
  const middle = Math.floor(size / 2)

  const points = [
    [distance, distance],
    [distance, last - distance],
    [last - distance, distance],
    [last - distance, last - distance],
    [middle, middle],
  ]

  if (size === 19) {
    points.push(
      [middle, distance],
      [middle, last - distance],
      [distance, middle],
      [last - distance, middle],
    )
  }

  return points
}

function Board({ size = 19 }) {
// TODO: change cell size to be calculated from a hook checking the window size when a prototype can be shown
    //const windowSize = useWindowSize()
    const cellSize = 40
    const boardSize = size * cellSize
    const cellSpacing = 80/(size-1)
    const points = getStarPoints(size)

    return (
        <svg viewBox="0 0 100 100" preserveAspectRatio="XMidYMid" role="img">
            <title>Go Board</title>
            <rect x="5" y = "5" width="90" height="90" fill="#EBBF6C" stroke="black" strokeWidth="0.3"/>
            {Array.from({ length: size }, (_,i) => {
                return <line
                    key={`h-${i}`}
                    x1={10}
                    y1={10 + cellSpacing*i}
                    x2={90}
                    y2={10+ cellSpacing*i}
                    stroke="black"
                    strokeWidth={0.3}
                />
            })}
            {Array.from({ length: size }, (_,i) => {
                return <line
                    key={`v-${i}`}
                    x1={10 + cellSpacing*i}
                    y1={10}
                    x2={10 + cellSpacing*i}
                    y2={90}
                    stroke="black"
                    strokeWidth={0.3}
                />
            })}

            {points.map(([x,y]) => (
                <circle
                    key={`${x}-${y}`}
                    cx={10 + x*cellSpacing}
                    cy={10 + y*cellSpacing}
                    r={0.5}
                    fill="black"
                />
            ))}
            
        </svg>
    )
}

function Stones(board, cellSpacing, offset) {
    //stone grid svg
    //stone size = cellSpacing * 0.9
    //invisible stone and clickable if board state is 0, else show the stone in its colour according to backend
    //receive updates from backend board state and display stones and their colours as dictated. 
    //draw interactable grid --later maybe can also display ghost stone on hover for player who's turn it is

    const clickRadius = cellSpacing * 0.45
    const stoneRadius = clickRadius * 0.9

    return (
        <>
        {board.map((row, y) =>
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
                    )
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
                )
            }))}
        </>
    )
}

export { Board, Stones }