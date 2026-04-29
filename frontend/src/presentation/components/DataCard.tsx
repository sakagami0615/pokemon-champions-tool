import type { DateDetail } from '../../infrastructure/api/dataApi'

interface Props {
  detail: DateDetail
  selected: boolean
  onSelect: (date: string) => void
}

export default function DataCard({ detail, selected, onSelect }: Props) {
  return (
    <label className="flex items-start gap-3 border rounded-lg p-4 cursor-pointer dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800">
      <input
        type="radio"
        name="selected-date"
        checked={selected}
        onChange={() => onSelect(detail.date)}
        className="mt-1 shrink-0"
      />
      <div className="flex flex-1 gap-4">
        <div className="flex-1">
          <p className="font-bold text-sm">{detail.date}</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">内定ポケモン: {detail.pokemon_count}体</p>
        </div>
        {detail.top_pokemon.length > 0 && (
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">使用ポケモン上位3位</p>
            <div className="flex gap-2">
              {detail.top_pokemon.map((p) => (
                <div key={p.name} className="text-center">
                  <img
                    src={`/sprites/${p.name}.png`}
                    alt={p.name}
                    className="w-10 h-10 object-contain mx-auto"
                    onError={(e) => {
                      ;(e.target as HTMLImageElement).style.display = 'none'
                    }}
                  />
                  <p className="text-xs">{p.name}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </label>
  )
}
