const BASE_URL = 'http://127.0.0.1:8000/api/training';

export async function diagnose(pgn: string, playerName: string) {
  const res = await fetch(`${BASE_URL}/diagnose`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pgn, player_name: playerName }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getJobStatus(jobId: string) {
  const res = await fetch(`${BASE_URL}/jobs/${jobId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export interface SteerCandidate {
  uci: string;
  san?: string;
  eval_cp?: number;
  complexity?: number;
}

export interface SteerFinding {
  id: string;
  ply: number;
  move_number?: number;
  fen_before: string;
  user_color?: 'white' | 'black';
  opening?: { eco: string; name?: string };
  played?: SteerCandidate;
  best?: SteerCandidate;
  steer?: SteerCandidate;
  playable_candidates?: SteerCandidate[];
  eval_loss_cp?: number;
  had_tal_move?: boolean;
}

export interface SteerSummaryItem {
  moves: number;
  tal_moves: number;
  mean_complexity: number;
}

export interface ProfileData {
  player_name?: string;
  games_analyzed: number;
  moves_analyzed?: number;
  findings: any[];
  steer_findings?: SteerFinding[];
  steer_summary?: Record<string, SteerSummaryItem>;
  steer_budget_exhausted?: boolean;
  aggregates?: any;
  regressions?: any;
}

export async function getProfile(): Promise<ProfileData | null> {
  const res = await fetch(`${BASE_URL}/profile`);
  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error(await res.text());
  }
  return res.json();
}

export async function generateDrills(count: number = 20) {
  const res = await fetch(`${BASE_URL}/drills/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ count }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getDrillsList() {
  const res = await fetch(`${BASE_URL}/drills`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getDrillSet(setId: string) {
  const res = await fetch(`${BASE_URL}/drills/${setId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function attemptDrill(setId: string, drillId: string, moveUci: string, ply: number = 0) {
  const res = await fetch(`${BASE_URL}/drills/attempt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ set_id: setId, drill_id: drillId, move_uci: moveUci, ply }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getDueDrills() {
  const res = await fetch(`${BASE_URL}/srs/due`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function listRepertoires() {
  const res = await fetch(`${BASE_URL}/repertoires`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function buildRepertoire(color: 'white' | 'black', style: 'weakness' | 'sacrificial') {
  const res = await fetch(`${BASE_URL}/repertoire`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ color, style, build: true }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getTrends() {
  const res = await fetch(`${BASE_URL}/trends`);
  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error(await res.text());
  }
  return res.json();
}

export async function getRepertoireTree(eco: string, color: 'white' | 'black') {
  const res = await fetch(`${BASE_URL}/repertoire/tree`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ eco, color }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// The user's most-played openings per color (by ECO), for the Train-mode
// selector — so trees are built for high-volume lines, not just the low-volume
// weakness recommendations.
export async function getTopOpenings(limit = 12): Promise<{
  white: { eco: string; name: string; count: number }[];
  black: { eco: string; name: string; count: number }[];
}> {
  const res = await fetch(`${BASE_URL}/repertoire/top-openings?limit=${limit}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getWeaknessRanking(n = 6): Promise<{
  ranking: { dim: string; value: number; count: number; ref_value: number;
             grade: number; importance: number; kind: 'weakness' | 'strength' }[];
  phase: { dim: string; value: number; count: number; ref_value: number;
           grade: number; importance: number; kind: 'weakness' | 'strength' }[];
  clock: { dim: string; value: number; count: number; ref_value: number;
           grade: number; importance: number; kind: 'weakness' | 'strength' }[];
}> {
  const res = await fetch(`${BASE_URL}/weakness-ranking?n=${n}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export interface UsualSuspect {
  theme: string;
  games: number;
  occurrences: number;
  mean_severity: number;
  rank_score: number;
  severity_label: 'high' | 'medium' | 'low';
  finding_ids: string[];
}

export interface UsualSuspectsResponse {
  suspects: UsualSuspect[];
  by_phase: any[];
  by_concept: any[];
}

export interface ApprovedSuspectsResponse {
  themes: string[];
  updated?: string;
}

export async function getUsualSuspects(): Promise<UsualSuspectsResponse | null> {
  const res = await fetch(`${BASE_URL}/usual-suspects`);
  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error(await res.text());
  }
  return res.json();
}

export async function approveSuspects(themes: string[]): Promise<ApprovedSuspectsResponse> {
  const res = await fetch(`${BASE_URL}/usual-suspects/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ themes }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getApprovedSuspects(): Promise<ApprovedSuspectsResponse> {
  const res = await fetch(`${BASE_URL}/usual-suspects/approved`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function buildSuspectsDeck(count: number = 20): Promise<{ id: string; drills: any[]; [key: string]: any }> {
  const res = await fetch(`${BASE_URL}/usual-suspects/deck`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ count }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
