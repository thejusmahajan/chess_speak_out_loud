import './Training.css';

interface ProfileReportProps {
  profile: any;
  onFindingClick: (finding: any) => void;
  onGenerateDrills: () => void;
}

export default function ProfileReport({ profile, onFindingClick, onGenerateDrills }: ProfileReportProps) {
  if (!profile) return <div className="glass-panel">No profile available.</div>;

  const agg = profile.aggregates || {};
  const motifs = Object.entries(agg.by_motif || {}).sort((a: any, b: any) => b[1].blind - a[1].blind);
  const openings = Object.entries(agg.by_opening || {}).sort((a: any, b: any) => b[1].blind_rate - a[1].blind_rate);
  const concepts = Object.entries(agg.by_concept || {}).sort((a: any, b: any) => b[1].missed - a[1].missed);

  return (
    <div className="profile-report">
      <div className="profile-header glass-panel">
        <h2 className="gradient-text">Weakness Profile</h2>
        <div className="stats-row">
          <div className="stat-box">
            <span className="stat-label">Games Analyzed</span>
            <span className="stat-value">{profile.games_analyzed}</span>
          </div>
          <div className="stat-box">
            <span className="stat-label">Intuitive Blindness Rate</span>
            <span className="stat-value">{((agg.intuitive_blindness_rate || 0) * 100).toFixed(1)}%</span>
          </div>
          <div className="stat-box">
            <span className="stat-label">Attention Blindness Rate</span>
            <span className="stat-value">{((agg.attention_blindness_rate || 0) * 100).toFixed(1)}%</span>
          </div>
        </div>
        <button className="glass-btn primary" onClick={onGenerateDrills}>Generate Drills</button>
      </div>

      <div className="profile-grid">
        <div className="glass-panel">
          <h3>Top Motifs Missed</h3>
          <table className="glass-table">
            <thead>
              <tr><th>Motif</th><th>Blind</th><th>Missed</th></tr>
            </thead>
            <tbody>
              {motifs.slice(0, 5).map(([m, stats]: any) => (
                <tr key={m}>
                  <td>{m}</td>
                  <td>{stats.blind || 0}</td>
                  <td>{stats.missed || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="glass-panel">
          <h3>Top Openings</h3>
          <table className="glass-table">
            <thead>
              <tr><th>ECO</th><th>Moves</th><th>Blind Rate</th></tr>
            </thead>
            <tbody>
              {openings.slice(0, 5).map(([eco, stats]: any) => (
                <tr key={eco}>
                  <td>{eco}</td>
                  <td>{stats.moves || 0}</td>
                  <td>{((stats.blind_rate || 0) * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="glass-panel">
          <h3>Top Concepts</h3>
          <table className="glass-table">
            <thead>
              <tr><th>Concept</th><th>Missed</th></tr>
            </thead>
            <tbody>
              {concepts.slice(0, 5).map(([concept, stats]: any) => (
                <tr key={concept}>
                  <td>{concept}</td>
                  <td>{stats.missed || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="glass-panel findings-list">
        <h3>Notable Findings</h3>
        <div className="findings-grid">
          {profile.findings?.map((f: any) => (
            <div key={f.id} className="finding-card glass-card" onClick={() => onFindingClick(f)}>
              <div className="finding-header">
                <span className="move-number">Move {f.move_number}</span>
                <span className={`severity ${f.severity}`}>{f.severity}</span>
              </div>
              <div className="finding-details">
                <p><strong>Played:</strong> {f.played.san} <span className="dim">({(f.played.p * 100).toFixed(1)}%)</span></p>
                <p><strong>Best:</strong> {f.best.san} <span className="dim">({(f.best.p * 100).toFixed(1)}%)</span></p>
                {f.confirmation?.swing_cp != null && (
                  <p className="swing-cp">Swing: {(f.confirmation.swing_cp / 100).toFixed(2)}</p>
                )}
                {f.motifs?.length > 0 && (
                  <div className="tags">
                    {f.motifs.map((m: string) => <span key={m} className="tag">{m}</span>)}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
