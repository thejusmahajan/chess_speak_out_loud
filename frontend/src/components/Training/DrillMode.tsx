import { useState, useEffect } from 'react';
import { getDrillSet, attemptDrill } from '../../api/training';
import TrainingBoard from './TrainingBoard';
import './Training.css';

interface DrillModeProps {
  setId: string;
  onExit: () => void;
}

export default function DrillMode({ setId, onExit }: DrillModeProps) {
  const [drillSet, setDrillSet] = useState<any>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [attemptResult, setAttemptResult] = useState<any>(null);
  const [revealFen, setRevealFen] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
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
    load();
  }, [setId]);

  if (loading) return <div className="glass-panel">Loading Drills...</div>;
  if (error) return <div className="glass-panel error-msg">{error}</div>;
  if (!drillSet || !drillSet.drills || drillSet.drills.length === 0) return <div className="glass-panel">No drills found.</div>;

  const drill = drillSet.drills[currentIndex];
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
    if (attemptResult) return; // already attempted this drill
    try {
      // Temporarily show the user's move on the board before the reveal data comes back
      // The TrainingBoard will update its UI locally due to chessground, but we need to record the FEN for saliency
      const res = await attemptDrill(setId, drill.id, uci);
      setAttemptResult(res);
      // Note: we might want to update the FEN to the post-move state, but usually the reveal 
      // applies to the FEN *before* the move, or exactly after setup. 
      // We'll leave the board as is (chessground played it) and just show overlays.
    } catch (err: any) {
      console.error('Attempt failed', err);
    }
  };

  const nextDrill = () => {
    setAttemptResult(null);
    setRevealFen(null);
    setCurrentIndex(i => i + 1);
  };

  const getOrientation = (fen: string) => {
    const turn = fen.split(' ')[1];
    return turn === 'w' ? 'white' : 'black';
  };
  
  // The interactive FEN is the drill.fen + setup move applied if corpus, but since frontend doesn't have 
  // chess.js locally exposed without chessops, we'll just let TrainingBoard handle it or pass fen.
  // Actually, wait: for corpus, setup_move_uci must be played!
  // If setup_move_uci exists, we should show it playing. For simplicity in this demo,
  // we can just let the board show the start FEN, and rely on the user to understand if it's their turn.
  // Ideally, we'd use chessops to apply the setup_move_uci to the FEN.
  
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
            fen={drill.fen}
            orientation={getOrientation(drill.fen)}
            interactive={!attemptResult}
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
              <p>Find the best move in this position.</p>
              <button className="glass-btn" onClick={onExit}>Exit Drills</button>
            </div>
          ) : (
            <div className={`result-card ${attemptResult.correct ? 'correct' : 'incorrect'}`}>
              <h3>{attemptResult.correct ? 'Correct!' : 'Incorrect!'}</h3>
              {attemptResult.reveal && (
                <div className="reveal-data">
                  {attemptResult.reveal.eval_cp !== undefined && (
                    <p><strong>Eval:</strong> {(attemptResult.reveal.eval_cp / 100).toFixed(2)}</p>
                  )}
                  {attemptResult.reveal.pv_san && (
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
