import { useEffect, useRef } from 'react';
import { Chessground } from 'chessground';
import 'chessground/assets/chessground.base.css';
import 'chessground/assets/chessground.brown.css';
import 'chessground/assets/chessground.cburnett.css';
import { Chess, Position } from 'chessops/chess';
import { parseFen, INITIAL_FEN } from 'chessops/fen';
import { chessgroundDests } from 'chessops/compat';
import { makeUci, parseUci } from 'chessops/util';
import { makeSan } from 'chessops/san';

interface TrainingBoardProps {
  fen: string;
  orientation?: 'white' | 'black';
  policy?: any[];
  saliency?: any;
  hotSquares?: string[];
  blunderFlash?: boolean;
  onMove?: (uci: string, san: string) => void;
  interactive?: boolean;
}

export default function TrainingBoard({
  fen,
  orientation = 'white',
  policy = [],
  saliency = null,
  hotSquares = [],
  blunderFlash = false,
  onMove,
  interactive = true,
}: TrainingBoardProps) {
  const boardRef = useRef<HTMLDivElement>(null);
  const cgRef = useRef<ReturnType<typeof Chessground> | null>(null);

  // Initialize board
  useEffect(() => {
    if (!boardRef.current) return;
    
    let pos: Position;
    try {
      pos = Chess.fromSetup(parseFen(fen).unwrap()).unwrap();
    } catch {
      pos = Chess.default();
    }

    const cg = Chessground(boardRef.current, {
      fen: pos ? fen : INITIAL_FEN,
      orientation,
      movable: {
        free: false,
        color: interactive ? orientation : undefined,
        dests: interactive ? chessgroundDests(pos) : new Map(),
      },
    });

    cg.set({
      movable: {
        events: {
          after: (orig, dest) => {
            if (!onMove) return;
            const uci = orig + dest;
            
            let currentPos: Position;
            try {
              currentPos = Chess.fromSetup(parseFen(cg.getFen()).unwrap()).unwrap();
            } catch {
              currentPos = Chess.default();
            }
            
            const move = parseUci(uci);
            if (move) {
              // Wait, chessground gives us fen after move? No, chessground changes DOM, not internal chessops.
              // We need to parse UCI from the *previous* pos to get SAN.
              let oldPos: Position;
              try {
                oldPos = Chess.fromSetup(parseFen(fen).unwrap()).unwrap();
              } catch {
                oldPos = Chess.default();
              }
              const validMove = parseUci(uci);
              if (validMove) {
                const san = makeSan(oldPos, validMove);
                onMove(uci, san);
              }
            }
          }
        }
      }
    });

    cgRef.current = cg;

    return () => {
      cg.destroy();
      cgRef.current = null;
    };
  }, []);

  // Update FEN, orientation, and interactability
  useEffect(() => {
    if (!cgRef.current) return;
    
    let pos: Position;
    try {
      pos = Chess.fromSetup(parseFen(fen).unwrap()).unwrap();
    } catch {
      pos = Chess.default();
    }
    
    cgRef.current.set({
      fen,
      orientation,
      movable: {
        color: interactive ? pos.turn : undefined,
        dests: interactive ? chessgroundDests(pos) : new Map(),
      }
    });
  }, [fen, orientation, interactive]);

  // Update overlays
  useEffect(() => {
    if (!boardRef.current) return;
    const cgBoard = boardRef.current.querySelector('cg-board');
    if (!cgBoard) return;

    const isBlack = cgRef.current?.state.orientation === 'black';

    let svg = cgBoard.querySelector('.neural-overlay') as SVGSVGElement | null;
    if (!svg) {
      svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.classList.add('neural-overlay');
      svg.style.position = 'absolute';
      svg.style.top = '0';
      svg.style.left = '0';
      svg.style.width = '100%';
      svg.style.height = '100%';
      svg.style.pointerEvents = 'none';
      svg.style.zIndex = '50';
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
    const markerPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    markerPath.setAttribute('d', 'M0,0 L0,4 L4,2 Z');
    markerPath.setAttribute('fill', 'rgba(0, 150, 255, 0.7)');
    marker.appendChild(markerPath);
    defs.appendChild(marker);

    const markerHot = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    markerHot.setAttribute('id', 'arrowhead-hot');
    markerHot.setAttribute('markerWidth', '4');
    markerHot.setAttribute('markerHeight', '4');
    markerHot.setAttribute('refX', '2');
    markerHot.setAttribute('refY', '2');
    markerHot.setAttribute('orient', 'auto');
    const markerHotPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    markerHotPath.setAttribute('d', 'M0,0 L0,4 L4,2 Z');
    markerHotPath.setAttribute('fill', 'rgba(255, 50, 50, 0.8)');
    markerHot.appendChild(markerHotPath);
    defs.appendChild(markerHot);
    svg.appendChild(defs);

    const squareToCoords = (sq: string) => {
      const file = sq.charCodeAt(0) - 97; // a=0, h=7
      const rank = parseInt(sq[1], 10) - 1; // 1=0, 8=7
      const px = isBlack ? 7 - file : file;
      const py = isBlack ? rank : 7 - rank;
      return { x: px * 12.5 + 6.25, y: py * 12.5 + 6.25 };
    };

    if (blunderFlash) {
      const flashRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      flashRect.setAttribute('x', '0');
      flashRect.setAttribute('y', '0');
      flashRect.setAttribute('width', '100%');
      flashRect.setAttribute('height', '100%');
      flashRect.setAttribute('fill', 'rgba(255,0,0,0.3)');
      flashRect.style.animation = 'blunder-pulse 1s ease-out';
      svg.appendChild(flashRect);
    }

    if (saliency && Object.keys(saliency).length > 0) {
      for (const [sq, val] of Object.entries(saliency)) {
        if (typeof val !== 'number' || val < 0.05) continue;
        const { x, y } = squareToCoords(sq);
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', `${x}%`);
        circle.setAttribute('cy', `${y}%`);
        
        const isHot = hotSquares.includes(sq);
        const radius = isHot ? (val * 8 + 2) : (val * 5);
        circle.setAttribute('r', `${radius}%`);
        
        if (isHot) {
          circle.setAttribute('fill', `rgba(255, 60, 0, ${Math.min(val + 0.2, 0.8)})`);
          circle.setAttribute('stroke', 'rgba(255, 255, 0, 0.5)');
          circle.setAttribute('stroke-width', '0.5%');
        } else {
          circle.setAttribute('fill', `rgba(255, 200, 0, ${val * 0.6})`);
        }
        
        circle.style.mixBlendMode = 'screen';
        svg.appendChild(circle);
      }
    }

    if (policy && policy.length > 0) {
      let maxP = policy[0].p;
      for (const move of policy) {
        if (move.p < 0.05) continue; // Noise
        const origSq = move.uci.slice(0, 2);
        const destSq = move.uci.slice(2, 4);
        const { x: x1, y: y1 } = squareToCoords(origSq);
        const { x: x2, y: y2 } = squareToCoords(destSq);

        const isBest = move.p === maxP;

        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', `${x1}%`);
        line.setAttribute('y1', `${y1}%`);
        line.setAttribute('x2', `${x2}%`);
        line.setAttribute('y2', `${y2}%`);
        
        line.setAttribute('stroke', isBest ? 'rgba(255, 50, 50, 0.8)' : 'rgba(0, 150, 255, 0.7)');
        line.setAttribute('stroke-width', `${Math.max(move.p * 3, 0.5)}%`);
        line.setAttribute('marker-end', isBest ? 'url(#arrowhead-hot)' : 'url(#arrowhead)');
        
        if (isBest) {
          line.style.filter = 'drop-shadow(0 0 2px rgba(255,0,0,0.5))';
        }
        
        svg.appendChild(line);
      }
    }

  }, [fen, policy, saliency, hotSquares, blunderFlash]);

  return (
    <div style={{ width: '100%', maxWidth: '600px', margin: '0 auto' }}>
      <div
        ref={boardRef}
        style={{ width: '100%', paddingBottom: '100%', position: 'relative' }}
      />
    </div>
  );
}
