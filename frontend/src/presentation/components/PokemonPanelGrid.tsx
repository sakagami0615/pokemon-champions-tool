import type { PokemonListEntry } from '../../domain/entities/pokemon'

interface Props {
  pokemonList: PokemonListEntry[]
}

export default function PokemonPanelGrid({ pokemonList }: Props) {
  if (pokemonList.length === 0) {
    return <p className="text-sm text-gray-500">左のリストから日付を選択してください</p>
  }

  return (
    <div className="flex flex-wrap gap-2">
      {pokemonList.map((pokemon) => (
        <div
          key={pokemon.name}
          className="flex flex-col items-center gap-1 p-2 rounded-lg border dark:border-gray-700 bg-gray-50 dark:bg-gray-800 w-20"
        >
          <img
            src={`/sprites/${pokemon.name}.png`}
            alt={pokemon.name}
            className="w-12 h-12 object-contain"
            onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
          />
          <span className="text-xs text-center leading-tight">{pokemon.name}</span>
        </div>
      ))}
    </div>
  )
}
