import type { DateDetail } from '../../infrastructure/api/dataApi'

interface Props {
  detail: DateDetail
  selected: boolean
  onSelect: (date: string) => void
}

export default function DataCard({ detail, selected, onSelect }: Props) {
  return (
    <label className="flex items-center gap-3 border rounded-lg px-4 py-3 cursor-pointer dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800">
      <input
        type="radio"
        name="selected-date"
        checked={selected}
        onChange={() => onSelect(detail.date)}
        className="shrink-0"
      />
      <div>
        <p className="font-bold text-sm">{detail.date}</p>
        <p className="text-xs text-gray-600 dark:text-gray-400">内定ポケモン: {detail.pokemon_count}体</p>
      </div>
    </label>
  )
}
