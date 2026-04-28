import type { DateDetail } from '../../infrastructure/api/dataApi'
import DataCard from './DataCard'

interface Props {
  details: DateDetail[]
  selectedDate: string | null
  onSelect: (date: string) => void
}

export default function DataCardList({ details, selectedDate, onSelect }: Props) {
  if (details.length === 0) {
    return <p className="text-sm text-gray-500">取得済みデータがありません</p>
  }

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-y-auto max-h-96 space-y-2 p-2">
      {details.map((detail) => (
        <DataCard
          key={detail.date}
          detail={detail}
          selected={selectedDate === detail.date}
          onSelect={onSelect}
        />
      ))}
    </div>
  )
}
