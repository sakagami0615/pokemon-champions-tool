import { useDataManagement } from '../../application/hooks/useDataManagement'
import DataCardList from '../components/DataCardList'

export default function DataPage() {
  const { status, isFetching, fetchMessage, error, triggerFetch, handleSelectDate } = useDataManagement()

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-xl font-bold">データ管理</h1>

      <div className="space-y-2">
        <div className="flex items-center gap-4">
          <button
            onClick={triggerFetch}
            disabled={isFetching}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold disabled:opacity-50"
          >
            {isFetching ? '開始中...' : 'データ取得'}
          </button>
          {status?.scraping_in_progress && (
            <p className="text-sm text-yellow-500 animate-pulse">スクレイピング実行中...</p>
          )}
        </div>
        {fetchMessage && <p className="text-sm text-green-600">{fetchMessage}</p>}
        {error && <p className="text-sm text-red-500">{error}</p>}
      </div>

      {status === null ? (
        <p className="text-sm text-gray-500">読み込み中...</p>
      ) : (
        <DataCardList
          details={status.dates_detail}
          selectedDate={status.selected_date}
          onSelect={handleSelectDate}
        />
      )}
    </div>
  )
}
