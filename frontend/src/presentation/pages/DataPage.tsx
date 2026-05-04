import { useState } from 'react'
import { useDataManagement } from '../../application/hooks/useDataManagement'
import DataCardList from '../components/DataCardList'
import PokemonPanelGrid from '../components/PokemonPanelGrid'

type Tab = 'dates' | 'pokemons'

export default function DataPage() {
  const { status, pokemonList, isFetching, fetchMessage, error, triggerFetch, handleSelectDate } = useDataManagement()
  const [tab, setTab] = useState<Tab>('dates')

  const onSelectDate = async (date: string) => {
    await handleSelectDate(date)
    setTab('pokemons')
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
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
        <>
          <div className="flex border-b dark:border-gray-700 sm:hidden">
            <button
              onClick={() => setTab('dates')}
              className={`flex-1 py-2 text-sm font-medium border-b-2 transition-colors ${
                tab === 'dates'
                  ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              日付選択
            </button>
            <button
              onClick={() => setTab('pokemons')}
              className={`flex-1 py-2 text-sm font-medium border-b-2 transition-colors ${
                tab === 'pokemons'
                  ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              ポケモン一覧
            </button>
          </div>

          <div className="sm:flex sm:gap-4 sm:items-stretch">
            <div className={`sm:block sm:w-64 sm:shrink-0 ${tab === 'dates' ? 'block' : 'hidden'}`}>
              <DataCardList
                details={status.dates_detail}
                selectedDate={status.selected_date}
                onSelect={onSelectDate}
              />
            </div>
            <div className="hidden sm:block w-px bg-gray-300 dark:bg-gray-600 self-stretch" />
            <div className={`sm:block sm:flex-1 sm:min-w-0 ${tab === 'pokemons' ? 'block' : 'hidden'}`}>
              <PokemonPanelGrid pokemonList={pokemonList} />
            </div>
          </div>
        </>
      )}
    </div>
  )
}
