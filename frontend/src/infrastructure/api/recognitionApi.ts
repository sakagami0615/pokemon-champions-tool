const BASE = '/api'

interface PartyResult {
  names: string[]
  confidences: number[]
}

export interface SelectionRecognitionResult {
  my_party: PartyResult
  opponent_party: PartyResult
}

export async function recognize(file: File): Promise<SelectionRecognitionResult> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/recognize`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
