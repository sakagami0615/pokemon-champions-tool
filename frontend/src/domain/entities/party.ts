export interface Party {
  id: string
  name: string
  pokemons: string[]
}

export interface PartiesData {
  parties: Party[]
  last_used_id: string | null
}
