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
