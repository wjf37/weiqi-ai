function Board({ size = 19 }) {
// TODO: change cell size to be calculated from a hook checking the window size when a prototype can be shown
    //const windowSize = useWindowSize()
    const cellSize = 40
    const boardSize = size * cellSize
    const cellSpacing = 80/(size-1)

    return (
        //show the basic light brown board with enough intersection lines for the type of board being played
        //on top have an invisible grid of circles that line up with the intersections and get updated to 
        //become visible upon receiving board state update from backend
        
        //example horizontal line for the intersections. the start and end points need to be calculated per board size.
        //<line x1="10" y1="10" x2="10" y2="90" stroke="black" stroke-width="0.2"/> 
        //lines: start = (5,5) end = (95,95)
        //split this 90 into n lines for the board size using i. 90/size = spacing starting from 5
        //horizontal lines: x1
        //board svg
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
            
        </svg>
    )
}

function Stones() {
    //stone grid svg

    //receive updates from backend board state and display stones and their colours as dictated. 

    //draw interactable grid --later maybe can also display ghost stone on hover for player who's turn it is
}

export { Board, Stones }