import PatternCard from './PatternCard'
import type { PredictionResult } from '../../domain/entities/prediction'
import type { UsageEntry, PokemonListEntry } from '../../domain/entities/pokemon'

interface Props {
  result: PredictionResult
  usageEntries?: UsageEntry[]
  pokemonList: PokemonListEntry[]
}

export default function PredictionResultView({ result, usageEntries = [], pokemonList }: Props) {
  const usageMap: Record<string, UsageEntry> = Object.fromEntries(
    usageEntries.map(e => [e.name, e])
  )

  return (
    <div className="space-y-4">
      <h2 className="font-bold text-lg">選出予想</h2>
      {result.patterns.map((pattern, i) => (
        <PatternCard key={i} pattern={pattern} index={i} usageMap={usageMap} pokemonList={pokemonList} />
      ))}
    </div>
  )
}
