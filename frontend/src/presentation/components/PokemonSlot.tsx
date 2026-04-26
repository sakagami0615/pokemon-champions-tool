import { useState, useEffect, useRef } from 'react'

interface Props {
  value: string
  onChange: (name: string) => void
  pokemonNames: string[]
}

export default function PokemonSlot({ value, onChange, pokemonNames }: Props) {
  const [query, setQuery] = useState(value)
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => { setQuery(value) }, [value])

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const filtered = query
    ? pokemonNames.filter(n => n.includes(query)).slice(0, 8)
    : pokemonNames.slice(0, 8)

  const select = (name: string) => {
    onChange(name)
    setQuery(name)
    setOpen(false)
  }

  return (
    <div ref={ref} className="relative">
      {value ? (
        <div
          className="flex flex-col items-center gap-1 p-2 rounded-lg border-2 border-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 cursor-pointer"
          onClick={() => { onChange(''); setQuery('') }}
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
      ) : (
        <div className="rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 p-2">
          <input
            className="w-full text-sm bg-transparent outline-none placeholder-gray-400"
            placeholder="ポケモン名..."
            value={query}
            onChange={e => { setQuery(e.target.value); setOpen(true) }}
            onFocus={() => setOpen(true)}
          />
          {open && filtered.length > 0 && (
            <ul className="absolute z-10 top-full left-0 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg max-h-48 overflow-y-auto">
              {filtered.map(name => (
                <li
                  key={name}
                  className="flex items-center gap-2 px-3 py-2 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 cursor-pointer text-sm"
                  onMouseDown={() => select(name)}
                >
                  <img
                    src={`/sprites/${name}.png`}
                    alt={name}
                    className="w-8 h-8 object-contain"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
                  />
                  {name}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
