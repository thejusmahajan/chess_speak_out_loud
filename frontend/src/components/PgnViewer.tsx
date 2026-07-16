import { useState, useEffect, useRef } from 'react';
import { Chessground } from 'chessground';
import 'chessground/assets/chessground.base.css';
import 'chessground/assets/chessground.brown.css';
import 'chessground/assets/chessground.cburnett.css';
import './PgnViewer.css';

// chessops
import { Chess, Position } from 'chessops/chess';
import { parseFen, INITIAL_FEN, makeFen } from 'chessops/fen';
import { chessgroundDests } from 'chessops/compat';
import { parseUci, makeUci } from 'chessops/util';
import { parsePgn } from 'chessops/pgn';
import { parseSan } from 'chessops/san';

type ChessgroundApi = ReturnType<typeof Chessground>;

const DEFAULT_PGN = `[Event "?"]
[Site "?"]
[Date "????.??.??"]
[Round "?"]
[White "?"]
[Black "?"]
[Result "*"]

1. c4 c5 2. Nf3 e6 3. Nc3 Nc6 4. g3 Nf6 5. Bg2 Qb6 6. d3 Be7 7. e4 d6 8. O-O Bd7 9. a3 Ng4 10. Ne1 Nf6 11. Rb1 a5 12. f4 O-O 13. b3 Ne8 14. g4 Qd8 15. Nc2 Nc7 16. Kh1 Bf6 17. Ne2 e5 18. f5 Bg5 19. a4 h6 20. Bxg5 hxg5 21. Ne3 Nd4 22. Qd2 f6 23. Bf3 Kf7 24. h4 Rh8 25. h5 Bc6 *`;

type GameState = {
  fen: string;
  pos: Position;
  lastMoveUci: string | null;
  policy: any[];
  saliency: any;
  evalObj: any;
  blunderFlash: boolean;
};

export default function PgnViewer() {
  const boardRef = useRef<HTMLDivElement>(null);
  const cgRef = useRef<ChessgroundApi | null>(null);
  
  const [pgnInput, setPgnInput] = useState(DEFAULT_PGN);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showTop20, setShowTop20] = useState(false);

  // Linear game history for Prev/Next/Branching
  const gameStates = useRef<GameState[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  // Derive current state from index
  const currentState = gameStates.current[currentIndex];

  useEffect(() => {
    if (!boardRef.current) return;
    
    const pos = Chess.default();
    const initialState: GameState = {
      fen: INITIAL_FEN,
      pos: pos,
      lastMoveUci: null,
      policy: [],
      saliency: null,
      evalObj: null,
      blunderFlash: false
    };
    gameStates.current = [initialState];
    setCurrentIndex(0);

    // Initialize chessground
    const cg = Chessground(boardRef.current, {
      fen: INITIAL_FEN,
      movable: {
        free: false,
        color: 'both',
        dests: chessgroundDests(pos),
        events: { after: handleMove }
      }
    });
    cgRef.current = cg;
    
    // Initial analysis
    analyzeFen(INITIAL_FEN, null, 0);

    return () => {
      cg.destroy();
    };
  }, []); // Run once on mount

  // Redraw Overlays when data changes or index changes
  useEffect(() => {
    if (currentState) {
      drawOverlays(
        currentState.saliency, 
        showTop20 ? currentState.policy : currentState.policy.slice(0, 5), 
        currentState.blunderFlash
      );
    }
  }, [currentIndex, currentState?.saliency, currentState?.policy, currentState?.blunderFlash, showTop20]);

  // Sync chessground with current state when index changes (e.g. Prev/Next)
  useEffect(() => {
    if (cgRef.current && currentState) {
      let lastMove: [string, string] | undefined = undefined;
      if (currentState.lastMoveUci) {
        lastMove = [currentState.lastMoveUci.substring(0,2), currentState.lastMoveUci.substring(2,4)];
      }
      cgRef.current.set({
        fen: currentState.fen,
        turnColor: currentState.pos.turn === 'white' ? 'white' : 'black',
        movable: { dests: chessgroundDests(currentState.pos) },
        lastMove: lastMove
      });
    }
  }, [currentIndex]);

  const handleMove = (orig: string, dest: string) => {
    if (!cgRef.current || !currentState) return;
    
    let uci = orig + dest;
    const piece = currentState.pos.board.get(parseUci(uci)!.from);
    if (piece && piece.role === 'pawn') {
      const destRank = dest.charAt(1);
      if (destRank === '1' || destRank === '8') {
        uci += 'q'; // Auto promote to queen
      }
    }
    
    const move = parseUci(uci);
    if (!move || !currentState.pos.isLegal(move)) {
      // Illegal move, snap back
      cgRef.current.set({ fen: currentState.fen });
      return;
    }
    
    // Play move
    const newPos = currentState.pos.clone();
    newPos.play(move);
    const newFen = makeFen(newPos.toSetup());
    
    const newState: GameState = {
      fen: newFen,
      pos: newPos,
      lastMoveUci: uci,
      policy: [],
      saliency: null,
      evalObj: null,
      blunderFlash: false
    };

    // Branching: truncate future history
    gameStates.current = gameStates.current.slice(0, currentIndex + 1);
    gameStates.current.push(newState);
    const newIndex = gameStates.current.length - 1;
    setCurrentIndex(newIndex);
    
    // Analyze new position
    analyzeFen(newFen, uci, newIndex);
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleNext = () => {
    if (currentIndex < gameStates.current.length - 1) {
      setCurrentIndex(currentIndex + 1);
      // Trigger analysis if it wasn't analyzed yet
      const nextState = gameStates.current[currentIndex + 1];
      if (!nextState.saliency && !nextState.policy.length) {
        analyzeFen(nextState.fen, nextState.lastMoveUci, currentIndex + 1);
      }
    }
  };

  const analyzeFen = async (fen: string, uciPlayed: string | null, stateIndex: number) => {
    setIsAnalyzing(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fen, multipv: 5 })
      });
      const data = await res.json();
      
      const policy = data.policy || [];
      const saliency = data.saliency || null;
      const evalObj = data.evaluation;
      
      let shouldFlash = false;
      if (uciPlayed && stateIndex > 0) {
        const prevPolicy = gameStates.current[stateIndex - 1].policy;
        if (prevPolicy && prevPolicy.length > 0) {
          const bestP = prevPolicy[0].p;
          const playedMove = prevPolicy.find((m: any) => m.uci === uciPlayed);
          const playedP = playedMove ? playedMove.p : 0;
          if (bestP - playedP > 0.25) {
            shouldFlash = true;
          }
        }
      }
      
      // Update the specific state
      const targetState = gameStates.current[stateIndex];
      if (targetState && targetState.fen === fen) {
        targetState.policy = policy;
        targetState.saliency = saliency;
        targetState.evalObj = evalObj;
        targetState.blunderFlash = shouldFlash;
        
        // Force re-render if it's the current state
        if (stateIndex === currentIndex) {
          setCurrentIndex(stateIndex); // Trigger effect by setting state to same value? No, React bails out.
          // We can just call drawOverlays directly to update SVG
          drawOverlays(saliency, showTop20 ? policy : policy.slice(0, 5), shouldFlash);
          
          // And we also want to trigger a re-render for evalObj. We can use a small hack or just 
          // let the component re-render by cloning the array or using a forceUpdate.
          gameStates.current = [...gameStates.current]; // trigger re-render if we were to store it in state, but gameStates is a ref.
          // We can force a re-render by re-setting currentIndex.
          setCurrentIndex(prev => prev); // This might not re-render.
          // Better: set a dummy state to force re-render.
          setForceRender(prev => prev + 1);
        }
      }
    } catch (err) {
      console.error("Analysis failed:", err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const [forceRender, setForceRender] = useState(0);

  const handleLoadPgn = () => {
    try {
      const games = parsePgn(pgnInput);
      if (games.length === 0) return;
      
      const game = games[0];
      const states: GameState[] = [];
      
      let startFen = INITIAL_FEN;
      if (game.headers && game.headers.size > 0) {
        // Some libraries use Map, some use an array/object. In chessops it's a Map-like or Iterable.
        for (const [key, val] of game.headers.entries()) {
          if (key.toUpperCase() === 'FEN') {
             startFen = val;
          }
        }
      }
      
      let startPos: Position;
      try {
          const parsedPos = parseFen(startFen).unwrap();
          startPos = Chess.fromSetup(parsedPos).unwrap();
      } catch (e) {
          startPos = Chess.default();
          startFen = INITIAL_FEN;
      }
      
      states.push({
        fen: makeFen(startPos.toSetup()),
        pos: startPos.clone(),
        lastMoveUci: null,
        policy: [],
        saliency: null,
        evalObj: null,
        blunderFlash: false
      });
      
      let currentNode = game.moves;
      let currentPos = startPos;
      
      while (currentNode.children && currentNode.children.length > 0) {
        const child = currentNode.children[0];
        const sanStr = child.data.san;
        
        const move = parseSan(currentPos, sanStr);
        if (!move) break;
        
        currentPos = currentPos.clone();
        currentPos.play(move);
        const fen = makeFen(currentPos.toSetup());
        const uci = makeUci(move);
        
        states.push({
          fen: fen,
          pos: currentPos,
          lastMoveUci: uci,
          policy: [],
          saliency: null,
          evalObj: null,
          blunderFlash: false
        });
        
        currentNode = child;
      }
      
      gameStates.current = states;
      setCurrentIndex(0);
      analyzeFen(states[0].fen, null, 0);
      
    } catch (err) {
      console.error("Invalid PGN:", err);
    }
  };

  const drawOverlays = (saliency: any, policy: any[], flash: boolean) => {
    if (!boardRef.current) return;
    const cgBoard = boardRef.current.querySelector('cg-board');
    if (!cgBoard) return;
    
    const isBlack = cgRef.current?.state.orientation === 'black';
    
    let svg = cgBoard.querySelector('.neural-overlay');
    if (!svg) {
      svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.classList.add('neural-overlay');
      (svg as SVGElement).style.position = 'absolute';
      (svg as SVGElement).style.top = '0';
      (svg as SVGElement).style.left = '0';
      (svg as SVGElement).style.width = '100%';
      (svg as SVGElement).style.height = '100%';
      (svg as SVGElement).style.pointerEvents = 'none';
      (svg as SVGElement).style.zIndex = '50';
      cgBoard.appendChild(svg);
    }
    
    svg.innerHTML = '';
    
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    marker.setAttribute('id', 'arrowhead');
    marker.setAttribute('markerWidth', '4');
    marker.setAttribute('markerHeight', '4');
    marker.setAttribute('refX', '2');
    marker.setAttribute('refY', '2');
    marker.setAttribute('orient', 'auto');
    
    const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    polygon.setAttribute('points', '0 0, 4 2, 0 4');
    polygon.setAttribute('fill', '#00ffcc');
    marker.appendChild(polygon);
    defs.appendChild(marker);
    svg.appendChild(defs);

    const getCoords = (sq: string) => {
      const file = sq.charCodeAt(0) - 97;
      const rank = sq.charCodeAt(1) - 49;
      const x = isBlack ? 7 - file : file;
      const y = isBlack ? rank : 7 - rank;
      return { x: (x + 0.5) * 12.5, y: (y + 0.5) * 12.5 };
    };

    if (saliency) {
      const color = flash ? '255, 0, 50' : '0, 150, 255';
      for (const [sq, val] of Object.entries(saliency)) {
        if ((val as number) > 0.05) {
          const coords = getCoords(sq);
          const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
          circle.setAttribute('cx', coords.x + '%');
          circle.setAttribute('cy', coords.y + '%');
          circle.setAttribute('r', '6.25%');
          
          const gradId = 'glow-' + sq;
          const grad = document.createElementNS('http://www.w3.org/2000/svg', 'radialGradient');
          grad.setAttribute('id', gradId);
          grad.innerHTML = `
              <stop offset="0%" stop-color="rgba(${color}, ${(val as number) * 0.8})" />
              <stop offset="100%" stop-color="rgba(${color}, 0)" />
          `;
          defs.appendChild(grad);
          
          circle.setAttribute('fill', `url(#${gradId})`);
          svg.appendChild(circle);
        }
      }
    }

    if (policy && policy.length > 0) {
      for (const move of policy) {
        const fromSq = move.from;
        const toSq = move.to;
        const p = move.p;
        if (!fromSq || !toSq || p < 0.01) continue;
        
        const fromCoords = getCoords(fromSq);
        const toCoords = getCoords(toSq);
        
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', fromCoords.x + '%');
        line.setAttribute('y1', fromCoords.y + '%');
        line.setAttribute('x2', toCoords.x + '%');
        line.setAttribute('y2', toCoords.y + '%');
        line.setAttribute('stroke', `rgba(0, 255, 204, ${Math.max(0.2, p)})`);
        line.setAttribute('stroke-width', Math.max(1, p * 4) + '%');
        line.setAttribute('marker-end', 'url(#arrowhead)');
        svg.appendChild(line);
      }
    }
  };

  return (
    <div className="pgn-viewer-container">
      <div className="board-section glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div ref={boardRef} style={{ width: '500px', height: '500px' }} className="cg-board-wrap" />
        
        <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
          <button className="load-btn" onClick={handlePrev} disabled={currentIndex === 0}>
            Take-back / Prev
          </button>
          <button className="load-btn" onClick={handleNext} disabled={currentIndex === gameStates.current.length - 1}>
            Next
          </button>
        </div>
      </div>

      <div className="input-section glass-panel">
        <h2>Neural Vision</h2>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input 
              type="checkbox" 
              checked={showTop20} 
              onChange={e => setShowTop20(e.target.checked)} 
            />
            Show Top 20 Arrows
          </label>
          
          {isAnalyzing && <span style={{ color: '#00ffcc', fontSize: '14px' }}>Analyzing...</span>}
        </div>
        
        {currentState?.evalObj && (
          <div style={{ marginBottom: '15px', padding: '10px', background: 'rgba(255,255,255,0.05)', borderRadius: '6px' }}>
            <strong>Evaluation: </strong>
            <span style={{ color: currentState.evalObj.value > 0 ? '#00ffcc' : '#ff3366', fontWeight: 'bold' }}>
              {currentState.evalObj.type === 'mate' ? `M${currentState.evalObj.value}` : (currentState.evalObj.value / 100).toFixed(2)}
            </span>
          </div>
        )}

        <textarea 
          value={pgnInput}
          onChange={(e) => setPgnInput(e.target.value)}
          placeholder="Paste PGN here..."
          style={{ height: '200px' }}
        />
        
        <button className="load-btn" onClick={handleLoadPgn}>
          Load Game
        </button>

        {currentState?.fen && (
          <div style={{ marginTop: '15px', fontSize: '12px', color: '#ccc', wordBreak: 'break-all' }}>
            <strong>Current FEN:</strong> {currentState.fen}
          </div>
        )}
      </div>
    </div>
  );
}
