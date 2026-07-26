import { useState, useEffect } from 'react';
import TrainingBoard from './TrainingBoard';
import {
  startSacSession,
  submitSacGuess,
  getSacStats,
} from '../../api/training';
import type {
  SacPosition,
  SacGuessResult,
  SacStats,
} from '../../api/training';

export default function SacDrill() {
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [positions, setPositions] = useState<SacPosition[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentResult, setCurrentResult] = useState<SacGuessResult | null>(null);
  const [score, setScore] = useState(0);
  const [acceptableCount, setAcceptableCount] = useState(0);
  const [isFinished, setIsFinished] = useState(false);
  const [stats, setStats] = useState<SacStats | null>(null);

  const loadSession = async () => {
    try {
      setLoading(true);
      setError(null);
      setCurrentResult(null);
      setCurrentIndex(0);
      setScore(0);
      setAcceptableCount(0);
      setIsFinished(false);

      const [sessionPositions, statsData] = await Promise.all([
        startSacSession(10).catch(() => []),
        getSacStats().catch(() => null),
      ]);

      setPositions(sessionPositions);
      setStats(statsData);
    } catch (err: any) {
      console.error('Failed to start sacrifice drill session:', err);
      setError(err.message || 'Failed to start session');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSession();
  }, []);

  const handleGuess = async (uci: string) => {
    if (currentResult || submitting || isFinished || positions.length === 0) return;

    setSubmitting(true);
    setError(null);

    const currentPos = positions[currentIndex];
    try {
      const result = await submitSacGuess(currentPos.id, uci);
      setCurrentResult(result);
      if (result.correct) {
        setScore((s) => s + 1);
      } else if (result.acceptable) {
        setAcceptableCount((a) => a + 1);
      }
    } catch (err: any) {
      console.error('Failed to submit sacrifice guess:', err);
      setError(err.message || 'Failed to submit guess');
    } finally {
      setSubmitting(false);
    }
  };

  const handleNext = async () => {
    setCurrentResult(null);
    if (currentIndex + 1 < positions.length) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      setIsFinished(true);
      const updatedStats = await getSacStats().catch(() => null);
      if (updatedStats) setStats(updatedStats);
    }
  };

  if (loading) {
    return (
      <div className="sac-drill-panel glass-panel">
        <p>Loading sacrifice drill session...</p>
      </div>
    );
  }

  if (positions.length === 0) {
    return (
      <div className="sac-drill-panel glass-panel">
        <h2 className="gradient-text">Sacrifice & Tactical-Landmine Training</h2>
        <p className="empty-state-msg">
          No eligible sacrifice positions found in profile. Run a diagnosis first to discover your landmines!
        </p>
        <button className="glass-btn primary" onClick={loadSession}>
          Try Again
        </button>
      </div>
    );
  }

  if (isFinished) {
    const sessionAccuracy = positions.length > 0 ? (score / positions.length) * 100 : 0;
    return (
      <div className="sac-drill-panel glass-panel" style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'center' }}>
        <h2 className="gradient-text">Session Complete!</h2>
        <div style={{ fontSize: '2.5rem', fontWeight: 'bold', margin: '20px 0', color: '#60a5fa' }}>
          {score} / {positions.length}
        </div>
        <p style={{ fontSize: '1.2rem', marginBottom: '10px' }}>
          Sacrifice Finding Accuracy: <strong>{sessionAccuracy.toFixed(1)}%</strong>
        </p>
        {acceptableCount > 0 && (
          <p style={{ fontSize: '0.95rem', color: '#f59e0b', marginBottom: '20px' }}>
            ⚡ Found <strong>{acceptableCount}</strong> sound alternative sharp moves!
          </p>
        )}

        {stats && (
          <div className="glass-panel" style={{ padding: '15px', marginBottom: '25px', textAlign: 'left' }}>
            <h3 style={{ marginTop: 0, fontSize: '1rem', color: '#60a5fa' }}>Lifetime Sacrifice Stats</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div>
                <span style={{ fontSize: '0.85rem', opacity: 0.8 }}>Overall Accuracy</span>
                <div style={{ fontSize: '1.3rem', fontWeight: 600 }}>{(stats.accuracy * 100).toFixed(1)}%</div>
                <div style={{ fontSize: '0.75rem', opacity: 0.6 }}>({stats.correct} / {stats.total} guesses)</div>
              </div>
              <div>
                <span style={{ fontSize: '0.85rem', opacity: 0.8 }}>Recent Accuracy (last 50)</span>
                <div style={{ fontSize: '1.3rem', fontWeight: 600, color: '#f59e0b' }}>
                  {(stats.recent_accuracy * 100).toFixed(1)}%
                </div>
                <div style={{ fontSize: '0.75rem', opacity: 0.6 }}>({stats.acceptable} sound alts)</div>
              </div>
            </div>
          </div>
        )}

        <button className="glass-btn primary" onClick={loadSession} style={{ padding: '10px 24px', fontSize: '1rem' }}>
          Start New Session
        </button>
      </div>
    );
  }

  const currentPos = positions[currentIndex];
  const sideToMove = currentPos.fen.split(' ')[1] === 'b' ? 'black' : 'white';

  return (
    <div className="sac-drill-panel glass-panel">
      {/* Session Progress Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <div>
          <h2 className="gradient-text" style={{ margin: 0, fontSize: '1.4rem' }}>
            Sacrifice & Tactical-Landmine Training
          </h2>
          <span style={{ fontSize: '0.85rem', opacity: 0.8 }}>
            Position {currentIndex + 1} of {positions.length} • Found: {score}
          </span>
        </div>
      </div>

      {/* Prompt Banner */}
      <div
        className="glass-panel"
        style={{
          padding: '10px 16px',
          marginBottom: '15px',
          backgroundColor: 'rgba(96, 165, 250, 0.15)',
          borderLeft: '4px solid #60a5fa',
          fontWeight: 600,
          fontSize: '1.05rem',
        }}
      >
        💡 A strong sacrifice is available here — find it.
      </div>

      {error && <div style={{ color: '#ef4444', marginBottom: '10px' }}>{error}</div>}

      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
        <div style={{ width: '100%', maxWidth: '480px', aspectRatio: '1/1' }}>
          <TrainingBoard
            fen={currentPos.fen}
            orientation={sideToMove}
            interactive={!currentResult && !submitting}
            onMove={(uci) => handleGuess(uci)}
          />
        </div>

        {/* Soundness Reveal Panel */}
        {currentResult && (
          <div className="glass-panel" style={{ width: '100%', maxWidth: '520px', padding: '16px' }}>
            {/* Verdict Banner */}
            <div
              style={{
                padding: '10px 14px',
                borderRadius: '8px',
                marginBottom: '15px',
                fontWeight: 600,
                backgroundColor: currentResult.correct
                  ? 'rgba(16, 185, 129, 0.2)'
                  : currentResult.acceptable
                  ? 'rgba(245, 158, 11, 0.2)'
                  : 'rgba(239, 68, 68, 0.2)',
                color: currentResult.correct
                  ? '#6ee7b7'
                  : currentResult.acceptable
                  ? '#fcd34d'
                  : '#fca5a5',
                border: `1px solid ${
                  currentResult.correct ? '#10b981' : currentResult.acceptable ? '#f59e0b' : '#ef4444'
                }`,
              }}
            >
              {currentResult.correct ? (
                <span>🎯 HIT! You found the sacrifice! ({currentResult.sac_move.san})</span>
              ) : currentResult.acceptable ? (
                <span>⚡ SOUND ALTERNATIVE! A sharp try — LC0 preferred the sacrifice {currentResult.sac_move.san}.</span>
              ) : (
                <span>❌ MISS! You played it safe. The sound sacrifice was {currentResult.sac_move.san}.</span>
              )}
            </div>

            {/* Soundness Framing Comparison */}
            <div
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                padding: '12px 14px',
                borderRadius: '6px',
                fontSize: '0.92rem',
                lineHeight: '1.5',
                marginBottom: '15px',
                borderLeft: '3px solid #60a5fa',
              }}
            >
              You'd safely play <strong>{currentResult.safe_move.san}</strong> ({currentResult.safe_move.eval_cp}cp). The sac <strong>{currentResult.sac_move.san}</strong> ({currentResult.sac_move.eval_cp}cp) concedes only <strong>{currentResult.eval_loss_cp}cp</strong> of objective eval but goes into a far sharper position (complexity {currentResult.sac_move.complexity.toFixed(2)}) where the opponent is likely to go wrong.
            </div>

            <button
              className="glass-btn primary"
              onClick={handleNext}
              style={{ width: '100%', padding: '10px', fontSize: '1rem' }}
            >
              {currentIndex + 1 < positions.length ? 'Next Position' : 'Finish Session'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
