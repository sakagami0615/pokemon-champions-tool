import { useState, useEffect, useRef } from 'react'
import type { PokemonListEntry } from '../../domain/entities/pokemon'

interface Props {
  value: string
  onChange: (name: string) => void
  pokemonList: PokemonListEntry[]
}

export default function PokemonSlot({ value, onChange, pokemonList }: Props) {
  const [editing, setEditing] = useState(false)
  const selectRef = useRef<HTMLSelectElement>(null)

  useEffect(() => {
    if (editing && selectRef.current) {
      selectRef.current.focus()
    }
  }, [editing])

  if (value && !editing) {
    const spriteSrc = pokemonList.find((p) => p.name === value)?.sprite_path
    return (
      <div
        className="flex flex-col items-center gap-1 p-2 rounded-lg border-2 border-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 cursor-pointer"
        onClick={() => setEditing(true)}
        title="クリックで変更"
      >
        {spriteSrc && (
          <img
            src={`/${spriteSrc}`}
            alt={value}
            className="w-12 h-12 object-contain"
          />
        )}
        <span className="text-xs font-bold">{value}</span>
      </div>
    )
  }

  return (
    <div className="rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 p-1">
      <select
        ref={selectRef}
        className="w-full text-sm bg-transparent dark:bg-gray-800 outline-none cursor-pointer"
        value={value}
        onChange={(e) => { onChange(e.target.value); setEditing(false) }}
        onBlur={() => setEditing(false)}
      >
        <option value="">---</option>
        {pokemonList.map((p) => (
          <option key={p.name} value={p.name}>{p.name}</option>
        ))}
      </select>
    </div>
  )
}
