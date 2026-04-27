import type { PredictionResult } from '../../domain/entities/prediction'

const BASE = '/api'

export async function predict(
  opponentParty: string[],
  myParty: string[],
): Promise<PredictionResult> {
  const res = await fetch(`${BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ opponent_party: opponentParty, my_party: myParty }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
