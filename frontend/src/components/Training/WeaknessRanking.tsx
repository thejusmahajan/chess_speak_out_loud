import { useEffect, useState } from 'react';
import { getWeaknessRanking } from '../../api/training';

export interface RankingItem {
  dim: string;
  value: number;
  count: number;
  ref_value: number;
  grade: number;
  importance: number;
  kind: 'weakness' | 'strength';
}

export default function WeaknessRanking() {
  const [ranking, setRanking] = useState<RankingItem[] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    getWeaknessRanking(6)
      .then((data) => {
        if (isMounted) {
          setRanking(data.ranking || []);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err?.message || 'Failed to load weakness ranking.');
          setLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="glass-panel weakness-ranking-panel" data-testid="weakness-ranking-panel">
      <h3>What to Work On</h3>
      <p className="ranking-subtext">Openings ranked by self-relative blindness versus your baseline</p>

      {loading && (
        <div className="ranking-loading" data-testid="ranking-loading">
          <div className="spinner" />
          <span>Analyzing opening performance...</span>
        </div>
      )}

      {error && !loading && (
        <div className="ranking-error error-msg" data-testid="ranking-error">
          {error}
        </div>
      )}

      {!loading && !error && ranking && ranking.length === 0 && (
        <div className="ranking-empty" data-testid="ranking-empty">
          Not enough games analyzed yet to rank your openings
        </div>
      )}

      {!loading && !error && ranking && ranking.length > 0 && (
        <div className="ranking-list" data-testid="ranking-list">
          {ranking.map((item) => (
            <div
              key={item.dim}
              className={`ranking-item ${item.kind}`}
              data-testid={`ranking-item-${item.dim}`}
            >
              <div className="ranking-item-main">
                <span className="ranking-eco">{item.dim}</span>
                <span className={`ranking-badge ${item.kind}`}>
                  {item.kind === 'weakness' ? 'Weakness' : 'Strength'}
                </span>
              </div>
              <div className="ranking-item-stats">
                <span className="stat-pill">
                  <strong>{(item.value * 100).toFixed(1)}%</strong> blind
                </span>
                <span className="stat-pill">
                  <strong>{item.count}</strong> {item.count === 1 ? 'game' : 'games'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
