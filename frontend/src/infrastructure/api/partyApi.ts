import type { Party, PartiesData } from '../../domain/entities/party'

const BASE = '/api'

export async function getParties(): Promise<PartiesData> {
  const res = await fetch(`${BASE}/party`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function createParty(name: string, pokemon: string[]): Promise<Party> {
  const res = await fetch(`${BASE}/party`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, pokemon }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function updateParty(id: string, name: string, pokemon: string[]): Promise<Party> {
  const res = await fetch(`${BASE}/party/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, pokemon }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function deleteParty(id: string): Promise<void> {
  await fetch(`${BASE}/party/${id}`, { method: 'DELETE' })
}

export async function setLastUsedParty(id: string): Promise<void> {
  await fetch(`${BASE}/party/last-used/${id}`, { method: 'POST' })
}
