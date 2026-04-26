export interface RatedItem {
  name: string
  rate: number
}

export interface EvSpread {
  spread: Record<string, number>
  rate: number
}

export interface UsageEntry {
  name: string
  moves: RatedItem[]
  items: RatedItem[]
  abilities: RatedItem[]
  natures: RatedItem[]
  teammates: RatedItem[]
  evs: EvSpread[]
  ivs: Record<string, number> | null
}

export interface PredictionPattern {
  pokemon: string[]
}

export interface PredictionResult {
  patterns: PredictionPattern[]
}

export interface Party {
  id: string
  name: string
  pokemon: string[]
}

export interface PartiesData {
  parties: Party[]
  last_used_id: string | null
}
