interface Props {
  value: string
  onChange: (name: string) => void
  pokemonNames: string[]
}

export default function PokemonSlot({ value, onChange, pokemonNames }: Props) {
  if (value) {
    return (
      <div
        className="flex flex-col items-center gap-1 p-2 rounded-lg border-2 border-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 cursor-pointer"
        onClick={() => onChange('')}
        title="クリックでリセット"
      >
        <img
          src={`/sprites/${value}.png`}
          alt={value}
          className="w-12 h-12 object-contain"
          onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
        />
        <span className="text-xs font-bold">{value}</span>
      </div>
    )
  }

  return (
    <div className="rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 p-1">
      <select
        className="w-full text-sm bg-transparent dark:bg-gray-800 outline-none cursor-pointer"
        value=""
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">---</option>
        {pokemonNames.map((name) => (
          <option key={name} value={name}>{name}</option>
        ))}
      </select>
    </div>
  )
}
