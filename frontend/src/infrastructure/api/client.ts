const BASE = '/api'

export async function recognize(file: File): Promise<{ names: string[]; confidences: number[] }> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/recognize`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function predict(opponentParty: string[], myParty: string[]) {
  const res = await fetch(`${BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ opponent_party: opponentParty, my_party: myParty }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getParties() {
  const res = await fetch(`${BASE}/party`)
  return res.json()
}

export async function createParty(name: string, pokemon: string[]) {
  const res = await fetch(`${BASE}/party`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, pokemon }),
  })
  return res.json()
}

export async function updateParty(id: string, name: string, pokemon: string[]) {
  const res = await fetch(`${BASE}/party/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, pokemon }),
  })
  return res.json()
}

export async function deleteParty(id: string) {
  await fetch(`${BASE}/party/${id}`, { method: 'DELETE' })
}

export async function setLastUsedParty(id: string) {
  await fetch(`${BASE}/party/last-used/${id}`, { method: 'POST' })
}

export async function fetchData() {
  const res = await fetch(`${BASE}/data/fetch`, { method: 'POST' })
  return res.json()
}

export async function getDataStatus() {
  const res = await fetch(`${BASE}/data/status`)
  return res.json()
}

export async function getPokemonNames(): Promise<string[]> {
  const res = await fetch(`${BASE}/data/pokemon/names`)
  const data = await res.json()
  return data.names as string[]
}
