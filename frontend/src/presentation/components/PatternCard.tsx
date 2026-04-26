import PokemonCard from './PokemonCard'
import type { PredictionPattern, UsageEntry } from '../../domain/entities'

interface Props {
  pattern: PredictionPattern
  index: number
  usageMap: Record<string, UsageEntry>
}

export default function PatternCard({ pattern, index, usageMap }: Props) {
  const isTop = index === 0
  return (
    <div className={`rounded-xl p-4 border-2 ${isTop ? 'border-indigo-500' : 'border-gray-200 dark:border-gray-700'}`}>
      <div className={`font-bold text-sm mb-3 ${isTop ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500'}`}>
        {isTop ? '🏆 ' : ''}パターン{index + 1}{isTop ? '（最有力）' : ''}
      </div>
      <div className="flex gap-2">
        {pattern.pokemon.map((name, i) => (
          <PokemonCard key={i} name={name} usage={usageMap[name] ?? null} />
        ))}
      </div>
    </div>
  )
}
