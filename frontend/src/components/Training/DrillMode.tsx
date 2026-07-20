import { useState, useEffect, useMemo } from 'react';
import { getDrillSet, attemptDrill } from '../../api/training';
import TrainingBoard from './TrainingBoard';
import { Chess } from 'chessops/chess';
import { parseFen, makeFen } from 'chessops/fen';
import { parseUci } from 'chessops/util';
import type { Key } from 'chessground/types';
import './Training.css';

interface DrillModeProps {
  setId?: string;
  dueItems?: any[];
  onExit: () => void;
}

function applyUci(fen: string, uci: string): string {
  try {
    const pos = Chess.fromSetup(parseFen(fen).unwrap()).unwrap();
    const move = parseUci(uci);
    if (move) pos.play(move);
    return makeFen(pos.toSetup());
  } catch {
    return fen;
  }
}

function formatRelativeTime(isoString: string) {
  const diff = new Date(isoString).getTime() - new Date().getTime();
  if (diff < 0) return 'now';
  const hours = diff / (1000 * 60 * 60);
  if (hours < 1) return 'in < 1 hour';
  if (hours < 24) return `in ${Math.round(hours)} hours`;
  return `in ${Math.round(hours / 24)} days`;
}

export default function DrillMode({ setId, dueItems, onExit }: DrillModeProps) {
  const [drillSet, setDrillSet] = useState<any>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [attemptResult, setAttemptResult] = useState<any>(null);
  const [ply, setPly] = useState(0);
  const [lineProgress, setLineProgress] = useState<string[]>([]);

  const [activeFen, setActiveFen] = useState<string>('');
  const [activeLastMove, setActiveLastMove] = useState<[Key, Key] | undefined>();
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    async function load() {
      setCurrentIndex(0);
      setAttemptResult(null);
      setPly(0);
      setLineProgress([]);
      if (dueItems) {
        setDrillSet({ drills: dueItems.map(item => ({...item.drill, _srsItem: item})) });
        setLoading(false);
        return;
      }
      if (setId) {
        try {
          setLoading(true);
          const ds = await getDrillSet(setId);
          setDrillSet(ds);
          setLoading(false);
        } catch (err: any) {
          setError(err.message || 'Failed to load drills');
          setLoading(false);
        }
      }
    }
    load();
  }, [setId, dueItems]);

  const drill = drillSet?.drills?.[currentIndex];

  const finalFen = useMemo(() => {
    if (!drill) return '';
    if (drill.setup_move_uci) {
      try {
        const pos = Chess.fromSetup(parseFen(drill.fen).unwrap()).unwrap();
        const move = parseUci(drill.setup_move_uci);
        if (move) pos.play(move);
        return makeFen(pos.toSetup());
      } catch {
        return drill.fen;
      }
    }
    return drill.fen;
  }, [drill]);

  useEffect(() => {
    if (!drill) return;

    setPly(0);
    setLineProgress([]);
    if (drill.setup_move_uci) {
      setActiveFen(drill.fen);
      setActiveLastMove(undefined);
      setIsAnimating(true);
      
      const timer = setTimeout(() => {
        setActiveFen(finalFen);
        setActiveLastMove([drill.setup_move_uci.slice(0,2) as Key, drill.setup_move_uci.slice(2,4) as Key]);
        setIsAnimating(false);
      }, 600);
      return () => clearTimeout(timer);
    } else {
      setActiveFen(drill.fen);
      setActiveLastMove(undefined);
      setIsAnimating(false);
    }
  }, [drill, finalFen]);

  if (loading) return <div className="glass-panel">Loading Drills...</div>;
  if (error) return <div className="glass-panel error-msg">{error}</div>;
  if (!drillSet || !drillSet.drills || drillSet.drills.length === 0) return <div className="glass-panel">No drills found.</div>;

  const isFinished = currentIndex >= drillSet.drills.length;

  if (isFinished) {
    return (
      <div className="glass-panel drill-complete">
        <h2 className="gradient-text">Training Complete!</h2>
        <p>You have completed {drillSet.drills.length} drills.</p>
        <button className="glass-btn primary" onClick={onExit}>Back to Profile</button>
      </div>
    );
  }

  const handleMove = async (uci: string, san: string) => {
    if (attemptResult || isAnimating) return;
    try {
      const currentSetId = drill._srsItem?.set_id || setId;
      if (!currentSetId) return;
      const res = await attemptDrill(currentSetId, drill.id, uci, ply);

      if (res.correct && !res.complete) {
        // Mid-line: play the user's move, then auto-play the opponent's reply.
        const fenAfterUser = applyUci(activeFen, uci);
        setActiveFen(fenAfterUser);
        setActiveLastMove([uci.slice(0, 2) as Key, uci.slice(2, 4) as Key]);
        setLineProgress(p => [...p, san]);
        setPly(p => p + 2);
        if (res.reply_uci) {
          setIsAnimating(true);
          setTimeout(() => {
            setActiveFen(applyUci(fenAfterUser, res.reply_uci));
            setActiveLastMove([res.reply_uci.slice(0, 2) as Key, res.reply_uci.slice(2, 4) as Key]);
            setIsAnimating(false);
          }, 450);
        }
        return;
      }

      if (res.correct && res.complete) {
        // Show the final position with the winning move played.
        const fenAfterUser = applyUci(activeFen, uci);
        setActiveFen(res.reply_uci ? applyUci(fenAfterUser, res.reply_uci) : fenAfterUser);
        setActiveLastMove([uci.slice(0, 2) as Key, uci.slice(2, 4) as Key]);
        setLineProgress(p => [...p, san]);
      }
      setAttemptResult(res);
    } catch (err: any) {
      console.error('Attempt failed', err);
    }
  };

  const nextDrill = () => {
    setAttemptResult(null);
    setPly(0);
    setLineProgress([]);
    setCurrentIndex(i => i + 1);
  };

  const getOrientation = (fen: string) => {
    if (!fen) return 'white';
    const turn = fen.split(' ')[1];
    return turn === 'w' ? 'white' : 'black';
  };
  
  return (
    <div className="drill-mode">
      <div className="drill-header glass-panel">
        <h2 className="gradient-text">Drill {currentIndex + 1} of {drillSet.drills.length}</h2>
        <p>Source: {drill.source} | Difficulty: {drill.difficulty}</p>
        {drill.tags && drill.tags.length > 0 && (
          <div className="tags">
            {drill.tags.map((t: string) => <span key={t} className="tag">{t}</span>)}
          </div>
        )}
      </div>

      <div className="drill-content">
        <div className="board-container">
          <TrainingBoard 
            fen={activeFen}
            lastMove={activeLastMove}
            orientation={getOrientation(finalFen)}
            interactive={!attemptResult && !isAnimating}
            onMove={handleMove}
            policy={attemptResult?.reveal?.policy || []}
            saliency={attemptResult?.reveal?.saliency}
            blunderFlash={attemptResult && !attemptResult.correct}
          />
        </div>

        <div className="drill-sidebar glass-panel">
          {!attemptResult ? (
            <div className="instruction">
              <h3>Your Turn</h3>
              <p>{lineProgress.length === 0
                ? 'Find the best move in this position.'
                : 'Correct — keep going, find the next move.'}</p>
              {lineProgress.length > 0 && (
                <p className="line-progress"><strong>So far:</strong> {lineProgress.join(' ')}</p>
              )}
              <button className="glass-btn" onClick={onExit}>Exit Drills</button>
            </div>
          ) : (
            <div className={`result-card ${attemptResult.correct ? 'correct' : 'incorrect'}`}>
              <h3>{attemptResult.correct ? 'Correct!' : 'Incorrect!'}</h3>
              
              {attemptResult.next_due && (
                <div className="srs-info" style={{marginTop: '10px', marginBottom: '10px'}}>
                  <span style={{marginRight: '10px'}}><strong>Next review:</strong> {formatRelativeTime(attemptResult.next_due)}</span>
                  {attemptResult.lapses > 0 && (
                    <span className="badge" style={{backgroundColor: 'var(--color-danger)', padding: '2px 6px', borderRadius: '4px'}}>Lapses: {attemptResult.lapses}</span>
                  )}
                </div>
              )}

              {attemptResult.reveal && (
                <div className="reveal-data">
                  {attemptResult.reveal.swing_cp != null && attemptResult.reveal.swing_cp !== 0 && (
                    <p><strong>Eval swing:</strong> {Math.abs(attemptResult.reveal.swing_cp) >= 9000
                      ? 'decisive (mate)'
                      : (attemptResult.reveal.swing_cp / 100).toFixed(2)}</p>
                  )}
                  {attemptResult.reveal.pv_san && attemptResult.reveal.pv_san.length > 0 && (
                    <p><strong>Line:</strong> {attemptResult.reveal.pv_san.join(' ')}</p>
                  )}
                </div>
              )}
              <button className="glass-btn primary" onClick={nextDrill}>Next Drill</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
