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

export async function getProfile() {
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
