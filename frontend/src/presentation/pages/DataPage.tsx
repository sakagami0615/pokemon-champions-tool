import { useDataManagement } from '../../application/hooks/useDataManagement'

export default function DataPage() {
  const { status, isFetching, fetchMessage, error, triggerFetch, handleSelectDate } = useDataManagement()

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-xl font-bold">データ管理</h1>

      <section className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-2">
        <h2 className="font-bold text-sm text-gray-600 dark:text-gray-400">データ取得状況</h2>
        {status === null ? (
          <p className="text-sm text-gray-500">読み込み中...</p>
        ) : (
          <>
            <p className="text-sm">
              ポケモン一覧：
              <span className={status.pokemon_list_available ? 'text-green-600' : 'text-red-500'}>
                {status.pokemon_list_available ? '取得済み' : '未取得'}
              </span>
            </p>
            <p className="text-sm">
              使用率データ：
              <span className={status.usage_data_available ? 'text-green-600' : 'text-red-500'}>
                {status.usage_data_available
                  ? `取得済み（${status.usage_data_date?.slice(0, 10) ?? ''}）`
                  : '未取得'}
              </span>
            </p>
            {status.scraping_in_progress && (
              <p className="text-sm text-yellow-500 animate-pulse">スクレイピング実行中...</p>
            )}
          </>
        )}
      </section>

      <section className="space-y-2">
        <button
          onClick={triggerFetch}
          disabled={isFetching}
          className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold disabled:opacity-50"
        >
          {isFetching ? '開始中...' : 'データ取得'}
        </button>
        {fetchMessage && <p className="text-sm text-green-600">{fetchMessage}</p>}
        {error && <p className="text-sm text-red-500">{error}</p>}
      </section>

      {status && status.available_dates.length > 0 && (
        <section className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-2">
          <h2 className="font-bold text-sm text-gray-600 dark:text-gray-400">使用するデータを選択</h2>
          <select
            value={status.selected_date ?? ''}
            onChange={(e) => handleSelectDate(e.target.value)}
            className="w-full border border-gray-300 dark:border-gray-600 rounded px-3 py-2 bg-white dark:bg-gray-800 text-sm"
          >
            <option value="" disabled>日付を選択してください</option>
            {status.available_dates.map((date) => (
              <option key={date} value={date}>{date}</option>
            ))}
          </select>
          {status.selected_date && (
            <p className="text-sm text-gray-500">
              選択中：{status.selected_date}
            </p>
          )}
        </section>
      )}
    </div>
  )
}
