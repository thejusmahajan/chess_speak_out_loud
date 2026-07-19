import { useState, useEffect } from 'react';
import DiagnosePanel from './DiagnosePanel';
import ProfileReport from './ProfileReport';
import DrillMode from './DrillMode';
import TrainingBoard from './TrainingBoard';
import { getProfile, generateDrills } from '../../api/training';
import './Training.css';

export default function TrainingTab() {
  const [view, setView] = useState<'diagnose' | 'profile' | 'drills'>('diagnose');
  const [profile, setProfile] = useState<any>(null);
  const [drillSetId, setDrillSetId] = useState<string | null>(null);
  const [selectedFinding, setSelectedFinding] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [drillError, setDrillError] = useState<string | null>(null);

  const fetchProfile = async () => {
    try {
      const p = await getProfile();
      if (p) {
        setProfile(p);
        setView('profile');
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleGenerateDrills = async () => {
    try {
      setLoading(true);
      setDrillError(null);
      const res = await generateDrills(5);
      setDrillSetId(res.set_id);
      setView('drills');
      setLoading(false);
    } catch (err: any) {
      console.error('Failed to generate drills', err);
      setDrillError(err.message || 'Failed to generate drills');
      setLoading(false);
    }
  };

  return (
    <div className="training-tab">
      <div className="training-nav glass-panel">
        <button 
          className={`glass-btn ${view === 'diagnose' ? 'active' : ''}`}
          onClick={() => setView('diagnose')}
        >
          Diagnose PGN
        </button>
        <button 
          className={`glass-btn ${view === 'profile' ? 'active' : ''}`}
          onClick={() => setView('profile')}
          disabled={!profile}
        >
          Weakness Profile
        </button>
        <button 
          className={`glass-btn ${view === 'drills' ? 'active' : ''}`}
          onClick={() => drillSetId ? setView('drills') : handleGenerateDrills()}
          disabled={!profile || loading}
        >
          {loading ? 'Generating...' : 'Training Drills'}
        </button>
        {drillError && <div className="error-msg" style={{ marginLeft: 'auto', color: 'var(--color-danger)' }}>{drillError}</div>}
      </div>

      <div className="training-content">
        {view === 'diagnose' && (
          <DiagnosePanel onProfileReady={fetchProfile} />
        )}

        {view === 'profile' && profile && (
          <div className="profile-view-layout">
            <ProfileReport 
              profile={profile} 
              onFindingClick={setSelectedFinding}
              onGenerateDrills={handleGenerateDrills}
            />
            {selectedFinding && (
              <div className="finding-board-container glass-panel">
                <h3>Missed Opportunity</h3>
                <TrainingBoard 
                  fen={selectedFinding.fen_before}
                  orientation={selectedFinding.user_color}
                  interactive={false}
                  policy={[selectedFinding.best, selectedFinding.played].filter(Boolean)}
                  saliency={null} // Can add full saliency if available in profile finding
                  hotSquares={selectedFinding.attention?.hot_squares || []}
                  blunderFlash={true}
                />
              </div>
            )}
          </div>
        )}

        {view === 'drills' && drillSetId && (
          <DrillMode setId={drillSetId} onExit={() => setView('profile')} />
        )}
      </div>
    </div>
  );
}
