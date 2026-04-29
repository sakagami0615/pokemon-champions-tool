const BASE = '/api'

export interface TopPokemon {
  name: string
}

export interface DateDetail {
  date: string
  pokemon_count: number
  top_pokemon: TopPokemon[]
}

export interface DataStatus {
  scraping_in_progress: boolean
  selected_date: string | null
  available_dates: string[]
  dates_detail: DateDetail[]
}

export async function fetchData(): Promise<{ status: string }> {
  const res = await fetch(`${BASE}/data/fetch`, { method: 'POST' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getDataStatus(): Promise<DataStatus> {
  const res = await fetch(`${BASE}/data/status`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getAvailableDates(): Promise<string[]> {
  const res = await fetch(`${BASE}/data/dates`)
  if (!res.ok) throw new Error(await res.text())
  const data = await res.json()
  return data.dates as string[]
}

export async function selectDate(date: string): Promise<{ selected_date: string }> {
  const res = await fetch(`${BASE}/data/select-date`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ date }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getPokemonNames(): Promise<string[]> {
  const res = await fetch(`${BASE}/data/pokemon/names`)
  if (!res.ok) throw new Error(await res.text())
  const data = await res.json()
  return data.names as string[]
}
