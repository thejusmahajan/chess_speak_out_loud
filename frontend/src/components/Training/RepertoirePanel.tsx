import { useState, useEffect, useMemo } from 'react';
import { listRepertoires, buildRepertoire } from '../../api/training';
import TrainingBoard from './TrainingBoard';
import { Chess } from 'chessops/chess';
import { makeFen } from 'chessops/fen';
import { parseSan } from 'chessops/san';
import { makeUci } from 'chessops/util';
import type { Key } from 'chessground/types';
import './Training.css';

type Style = 'weakness' | 'sacrificial';
type Color = 'white' | 'black';

const VARIANTS: { style: Style; color: Color; label: string }[] = [
  { style: 'weakness', color: 'white', label: 'Weakness · White' },
  { style: 'weakness', color: 'black', label: 'Weakness · Black' },
  { style: 'sacrificial', color: 'white', label: 'Sacrificial · White' },
  { style: 'sacrificial', color: 'black', label: 'Sacrificial · Black' },
];

function variantKey(style: string, color: string) {
  return `${style}_${color}`;
}

// Replay the SAN line (e.g. "1. e4 e5 2. d4") to its tabiya for a board preview.
function lineToPosition(linePgn: string): { fen: string; lastMove?: [Key, Key] } {
  const tokens = (linePgn || '').replace(/\d+\./g, '').trim().split(/\s+/).filter(Boolean);
  const pos = Chess.default();
  let lastUci: string | undefined;
  for (const san of tokens) {
    const move = parseSan(pos, san);
    if (!move) break;
    lastUci = makeUci(move);
    pos.play(move);
  }
  return {
    fen: makeFen(pos.toSetup()),
    lastMove: lastUci
      ? [lastUci.slice(0, 2) as Key, lastUci.slice(2, 4) as Key]
      : undefined,
  };
}

export default function RepertoirePanel() {
  const [reps, setReps] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [selectedRec, setSelectedRec] = useState(0);
  const [buildingKey, setBuildingKey] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      setLoading(true);
      const list = await listRepertoires();
      setReps(list);
      if (list.length > 0 && !selectedKey) {
        setSelectedKey(variantKey(list[0].style, list[0].color));
      }
      setLoading(false);
    } catch (e: any) {
      setError(e.message || 'Failed to load repertoires');
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const byKey = useMemo(() => {
    const m: Record<string, any> = {};
    for (const r of reps) m[variantKey(r.style, r.color)] = r;
    return m;
  }, [reps]);

  const selected = selectedKey ? byKey[selectedKey] : null;
  const recs = selected?.recommendations || [];
  const rec = recs[selectedRec];

  const preview = useMemo(
    () => (rec ? lineToPosition(rec.line_pgn) : null),
    [rec]
  );

  const handleBuild = async (style: Style, color: Color) => {
    const key = variantKey(style, color);
    try {
      setBuildingKey(key);
      setError(null);
      await buildRepertoire(color, style);
      await load();
      setSelectedKey(key);
      setSelectedRec(0);
    } catch (e: any) {
      setError(e.message || 'Build failed (is a profile diagnosed?)');
    } finally {
      setBuildingKey(null);
    }
  };

  const selectVariant = (key: string) => {
    setSelectedKey(key);
    setSelectedRec(0);
  };

  if (loading) return <div className="glass-panel">Loading repertoires...</div>;

  return (
    <div className="repertoire-panel">
      <div className="glass-panel">
        <h2 className="gradient-text">Opening Repertoire</h2>
        <p className="subtle">
          Sharp, engine-sound openings whose middlegames force the tactics you
          miss most. Four variants: a weakness-targeting and a sacrificial line
          set for each color.
        </p>
        <div className="variant-grid">
          {VARIANTS.map(v => {
            const key = variantKey(v.style, v.color);
            const built = byKey[key];
            const isBuilding = buildingKey === key;
            return (
              <div
                key={key}
                className={`variant-card ${selectedKey === key ? 'active' : ''} ${built ? '' : 'empty'}`}
                onClick={() => built && selectVariant(key)}
              >
                <div className="variant-label">{v.label}</div>
                {built ? (
                  <div className="variant-meta">
                    {built.recommendations?.length || 0} lines
                  </div>
                ) : (
                  <button
                    className="glass-btn"
                    disabled={isBuilding}
                    onClick={(e) => { e.stopPropagation(); handleBuild(v.style, v.color); }}
                  >
                    {isBuilding ? 'Building…' : 'Build'}
                  </button>
                )}
              </div>
            );
          })}
        </div>
        {error && <div className="error-msg" style={{ marginTop: '10px' }}>{error}</div>}
      </div>

      {selected && recs.length > 0 && (
        <div className="repertoire-detail">
          <div className="rec-list glass-panel">
            <h3>Recommended lines</h3>
            {recs.map((r: any, i: number) => (
              <div
                key={r.tag + i}
                className={`rec-item ${i === selectedRec ? 'active' : ''}`}
                onClick={() => setSelectedRec(i)}
              >
                <div className="rec-name">{r.name}</div>
                <div className="rec-sub">
                  <span className="tag">{r.eco}</span>
                  <span className="rec-line">{r.line_pgn}</span>
                </div>
                <div className="rec-stats">
                  <span title="LC0 eval of the tabiya (mover POV)">
                    eval {(r.eval_cp / 100).toFixed(2)}
                  </span>
                  {r.draw_pct != null && <span title="WDL draw share">draw {r.draw_pct}%</span>}
                  <span className="tag hot">{r.primary_motif}</span>
                </div>
              </div>
            ))}
          </div>

          {rec && (
            <div className="rec-board glass-panel">
              <h3>{rec.name}</h3>
              {preview && (
                <TrainingBoard
                  fen={preview.fen}
                  lastMove={preview.lastMove}
                  orientation={selected.color}
                  interactive={false}
                />
              )}
              <p className="rec-rationale">{rec.rationale}</p>
            </div>
          )}
        </div>
      )}

      {selected && recs.length === 0 && (
        <div className="glass-panel">
          No sound lines passed the soundness/sharpness gate for this variant.
        </div>
      )}
    </div>
  );
}
