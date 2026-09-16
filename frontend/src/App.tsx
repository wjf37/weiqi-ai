//import { useState } from 'react'
import './App.css'
import { Board } from './components/Board.tsx'

function App() {
  //const [count, setCount] = useState(0)
  const gameStateTemp: number[][] = [[0]]
  const handlePlaceStone = (x: number, y: number): void => {
    console.log('Placing stone at', x, y);
  };

  return (
    <>
      <section id="top">
        <div className="navbar">
          <h3>Weiqi AI</h3>
        </div>
      </section>
      <section id="center">
      </section>
      <Board 
        size={19}
        gameState={gameStateTemp}
        offset={10}
        onPlaceStone={handlePlaceStone}
      />
      <section id="next-steps">
        <div id="player1">
          <h2>Player 1</h2>
        </div>
        <div id="player2">
          <h2>Player 2</h2>
        </div>
      </section>

      <div className="ticks"></div>
      <section id="spacer"></section>
    </>
  );
}

export default App;
