import React from 'react';
import './SteeringLinesPanel.css';

export interface SteeringLine {
  san: string;
  uci: string;
  eval: string;
  eval_cp: number;
  phi: number;
  motifs: string[];
  pv: string[];
  pv_str: string;
}

export interface SteeringData {
  current_phi?: number;
  objective_line?: SteeringLine;
  tactical_lines?: SteeringLine[];
}

interface SteeringLinesPanelProps {
  steering?: SteeringData | null;
  activeUci?: string | null;
  isAnalyzing?: boolean;
  onPreviewLine?: (pv: string[], moveUci: string) => void;
  onPlayMove?: (moveUci: string) => void;
}

// Empirical calibration curve from test split deciles
function calibratePhi(rawPhi: number): number {
  if (rawPhi <= 0.15) return rawPhi;
  if (rawPhi <= 0.50) return rawPhi * 0.95;
  if (rawPhi <= 0.80) return 0.50 + (rawPhi - 0.50) * 0.51; // maps 0.75 -> ~0.65
  return 0.65 + (rawPhi - 0.80) * 0.70;
}

export const SteeringLinesPanel: React.FC<SteeringLinesPanelProps> = ({
  steering,
  activeUci,
  isAnalyzing,
  onPreviewLine,
  onPlayMove,
}) => {
  if (!steering || (!steering.objective_line && (!steering.tactical_lines || steering.tactical_lines.length === 0))) {
    if (isAnalyzing) {
      return (
        <div className="steering-panel">
          <div className="steering-header">
            <div className="steering-header-row">
              <span className="steering-title">
                <span>⚡</span> Configuration Radar
              </span>
              <span className="tension-badge" style={{ color: '#00ffcc' }}>
                Analyzing...
              </span>
            </div>
          </div>
          <div style={{ padding: '16px', textAlign: 'center', color: '#00ffcc', fontSize: '0.88rem' }}>
            ⏱ Calculating Objective & Tal Steering Lines...
          </div>
        </div>
      );
    }
    return null;
  }

  const currentPhi = calibratePhi(steering.current_phi ?? 0);
  const phiPct = Math.round(currentPhi * 100);

  // Tension classification
  let tensionLabel = 'Calm / Positional';
  let tensionColor = '#00ffcc';
  if (currentPhi >= 0.35) {
    tensionLabel = 'Tactical Storm Alert';
    tensionColor = '#ff4444';
  } else if (currentPhi >= 0.15) {
    tensionLabel = 'Building Tension';
    tensionColor = '#ffaa00';
  }

  const getPhiBadgeClass = (phi: number) => {
    if (phi >= 0.3) return 'danger';
    if (phi >= 0.12) return 'medium';
    return 'low';
  };

  const formatEvalClass = (evalStr: string) => {
    if (evalStr.startsWith('+') || (evalStr.startsWith('M') && !evalStr.startsWith('M-'))) {
      return 'eval-pos';
    }
    if (evalStr.startsWith('-') || evalStr.startsWith('M-')) {
      return 'eval-neg';
    }
    return 'eval-even';
  };

  return (
    <div className="steering-panel">
      {/* Header & Board Tension Meter */}
      <div className="steering-header">
        <div className="steering-header-row">
          <span className="steering-title">
            <span>⚡</span> Configuration Radar
          </span>
          <span className="tension-badge" style={{ color: tensionColor }}>
            {tensionLabel} ({phiPct}%)
          </span>
        </div>
        <div className="tension-bar-bg">
          <div
            className="tension-bar-fill"
            style={{
              width: `${Math.min(100, Math.max(5, phiPct))}%`,
              background: `linear-gradient(90deg, #00ffcc 0%, ${tensionColor} 100%)`,
            }}
          />
        </div>
      </div>

      {/* Objective Engine Line */}
      {steering.objective_line && (
        <div className="lines-section">
          <div className="section-label objective">
            <span>🧊</span> Objective Best (Engine)
          </div>
          <div
            className={`line-card objective-card ${activeUci === steering.objective_line.uci ? 'active-preview' : ''}`}
            onClick={() => onPreviewLine && onPreviewLine(steering.objective_line!.pv, steering.objective_line!.uci)}
          >
            <div className="card-header-row">
              <div className="move-tag-group">
                <span className="rank-badge">Optimal</span>
                <span className="move-san-badge">{steering.objective_line.san}</span>
              </div>
              <div className="metrics-group">
                <span className={`eval-badge ${formatEvalClass(steering.objective_line.eval)}`}>
                  {steering.objective_line.eval}
                </span>
                <span className={`phi-badge ${getPhiBadgeClass(steering.objective_line.phi)}`}>
                  Risk: {Math.round(calibratePhi(steering.objective_line.phi) * 100)}%
                </span>
              </div>
            </div>

            <div className="pv-sequence">{steering.objective_line.pv_str || steering.objective_line.pv.join(' ')}</div>

            <div className="card-actions">
              <button
                type="button"
                className="action-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  onPreviewLine && onPreviewLine(steering.objective_line!.pv, steering.objective_line!.uci);
                }}
              >
                Preview Line
              </button>
              {onPlayMove && (
                <button
                  type="button"
                  className="action-btn play-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onPlayMove(steering.objective_line!.uci);
                  }}
                >
                  Play {steering.objective_line.san}
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tal Steering Lines (Tactical Potential) */}
      {steering.tactical_lines && steering.tactical_lines.length > 0 && (
        <div className="lines-section">
          <div className="section-label tactical">
            <span>🔥</span> Tal Steering Lines ({steering.tactical_lines.length} Options)
          </div>
          {steering.tactical_lines.map((line, index) => (
            <div
              key={line.uci + index}
              className={`line-card tactical-card ${activeUci === line.uci ? 'active-preview' : ''}`}
              onClick={() => onPreviewLine && onPreviewLine(line.pv, line.uci)}
            >
              <div className="card-header-row">
                <div className="move-tag-group">
                  <span className="rank-badge">#{index + 1} Steer</span>
                  <span className="move-san-badge">{line.san}</span>
                </div>
                <div className="metrics-group">
                  <span className={`eval-badge ${formatEvalClass(line.eval)}`}>{line.eval}</span>
                  <span className={`phi-badge ${getPhiBadgeClass(line.phi)}`}>
                    Risk: {Math.round(calibratePhi(line.phi) * 100)}%
                  </span>
                </div>
              </div>

              {line.motifs && line.motifs.length > 0 && (
                <div className="motifs-row">
                  {line.motifs.map((motif) => (
                    <span key={motif} className="motif-pill">
                      {motif}
                    </span>
                  ))}
                </div>
              )}

              <div className="pv-sequence">{line.pv_str || line.pv.join(' ')}</div>

              <div className="card-actions">
                <button
                  type="button"
                  className="action-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onPreviewLine && onPreviewLine(line.pv, line.uci);
                  }}
                >
                  Preview Line
                </button>
                {onPlayMove && (
                  <button
                    type="button"
                    className="action-btn play-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      onPlayMove(line.uci);
                    }}
                  >
                    Play {line.san}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
