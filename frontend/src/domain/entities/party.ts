export interface Party {
  id: string
  name: string
  pokemon: string[]
}

export interface PartiesData {
  parties: Party[]
  last_used_id: string | null
}
