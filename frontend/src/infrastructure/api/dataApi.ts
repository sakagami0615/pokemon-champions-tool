const BASE = '/api'

export async function fetchData(): Promise<{ status: string }> {
  const res = await fetch(`${BASE}/data/fetch`, { method: 'POST' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getDataStatus(): Promise<{
  pokemon_list_available: boolean
  usage_data_available: boolean
  usage_data_date: string | null
}> {
  const res = await fetch(`${BASE}/data/status`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getPokemonNames(): Promise<string[]> {
  const res = await fetch(`${BASE}/data/pokemon/names`)
  if (!res.ok) throw new Error(await res.text())
  const data = await res.json()
  return data.names as string[]
}
