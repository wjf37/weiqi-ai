function getStarPoints(size: number): number[][] {
  if (size !== 9 && size !== 13 && size !== 19) {
    return [];
  }

  var distance: number = 3;
  if (size == 9) {
     distance = 2;
  }
  const last: number = size - 1;
  const middle: number = Math.floor(size / 2);

  const points: number[][] = [
    [distance, distance],
    [distance, last - distance],
    [last - distance, distance],
    [last - distance, last - distance],
    [middle, middle],
  ];

  if (size === 19) {
    points.push(
      [middle, distance],
      [middle, last - distance],
      [distance, middle],
      [last - distance, middle],
    )
  }

  return points;
}

interface BoardBackgroundProps {
    size: number;
    cellSpacing: number;
    offset: number;
}

function BoardBackground({ size, cellSpacing, offset }: BoardBackgroundProps) {
// TODO: change cell size to be calculated from a hook checking the window size when a prototype can be shown
    //const windowSize = useWindowSize()
    //const cellSize: number = 40;
    const points: number[][] = getStarPoints(size);

    return (
        <>
            <title>Go Board</title>
            <rect
                x="5"
                y = "5"
                width="90"
                height="90"
                fill="#EBBF6C"
                stroke="black"
                strokeWidth="0.3"
            />
            {Array.from({ length: size }, (_,i) => {
                return (
                    <line
                        key={`h-${i}`}
                        x1={offset}
                        y1={offset + cellSpacing*i}
                        x2={100 - offset}
                        //look at changing 100-offset if needed
                        y2={offset+ cellSpacing*i}
                        stroke="black"
                        strokeWidth={0.3}
                    />
                );
            })}
            {Array.from({ length: size }, (_,i) => {
                return (
                    <line
                        key={`v-${i}`}
                        x1={offset + cellSpacing*i}
                        y1={offset}
                        x2={offset + cellSpacing*i}
                        y2={100 - offset}
                        stroke="black"
                        strokeWidth={0.3}
                    />
                );
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
    );
}

export { BoardBackground };