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

function BoardBackground({ size, cellSpacing, offset }) {
// TODO: change cell size to be calculated from a hook checking the window size when a prototype can be shown
    //const windowSize = useWindowSize()
    const cellSize = 40
    const points = getStarPoints(size)

    return (
        <>
            <title>Go Board</title>
            <rect x="5" y = "5" width="90" height="90" fill="#EBBF6C" stroke="black" strokeWidth="0.3"/>
            {Array.from({ length: size }, (_,i) => {
                return <line
                    key={`h-${i}`}
                    x1={offset}
                    y1={offset + cellSpacing*i}
                    x2={100 - offset}
                    //look at changing 100-offset if needed
                    y2={offset+ cellSpacing*i}
                    stroke="black"
                    strokeWidth={0.3}
                />
            })}
            {Array.from({ length: size }, (_,i) => {
                return <line
                    key={`v-${i}`}
                    x1={offset + cellSpacing*i}
                    y1={offset}
                    x2={offset + cellSpacing*i}
                    y2={100 - offset}
                    stroke="black"
                    strokeWidth={0.3}
                />
            })}

            {points.map(([x,y]) => (
                <circle
                    key={`${x}-${y}`}
                    cx={offset + x*cellSpacing}
                    cy={offset + y*cellSpacing}
                    r={0.5}
                    fill="black"
                />
            ))}
            
        </>
    )
}

export { BoardBackground }