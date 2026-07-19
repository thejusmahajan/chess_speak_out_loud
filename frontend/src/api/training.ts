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

export async function attemptDrill(setId: string, drillId: string, moveUci: string) {
  const res = await fetch(`${BASE_URL}/drills/attempt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ set_id: setId, drill_id: drillId, move_uci: moveUci }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
