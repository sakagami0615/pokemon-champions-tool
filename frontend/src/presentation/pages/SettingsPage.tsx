import { useState } from 'react'
import { useDataManagement } from '../../application/hooks/useDataManagement'
import { useLLMConfig } from '../../application/hooks/useLLMConfig'
import DataCardList from '../components/DataCardList'
import PokemonPanelGrid from '../components/PokemonPanelGrid'
import ModelSettings from '../components/ModelSettings'
import ScrapeProgressBar from '../components/ScrapeProgressBar'

type DataTab = 'dates' | 'pokemons'

export default function SettingsPage() {
  const {
    status,
    pokemonList,
    isFetching,
    error: dataError,
    triggerFetch,
    handleSelectDate,
  } = useDataManagement()

  const {
    config,
    ollamaModels,
    isSaving,
    isFetchingModels,
    error: llmError,
    saveMessage,
    isSelectedModelValid,
    updateProvider,
    updateModel,
    updateApiKey,
    updateOllamaBaseUrl,
    fetchOllamaModels,
    save,
  } = useLLMConfig()

  const [dataTab, setDataTab] = useState<DataTab>('dates')

  const onSelectDate = async (date: string) => {
    await handleSelectDate(date)
    setDataTab('pokemons')
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <section>
        {config === null ? (
          <p className="text-sm text-gray-500">読み込み中...</p>
        ) : (
          <ModelSettings
            config={config}
            ollamaModels={ollamaModels}
            isSaving={isSaving}
            isFetchingModels={isFetchingModels}
            error={llmError}
            saveMessage={saveMessage}
            isSelectedModelValid={isSelectedModelValid}
            onSelectProvider={updateProvider}
            onSelectModel={updateModel}
            onUpdateApiKey={updateApiKey}
            onUpdateOllamaBaseUrl={updateOllamaBaseUrl}
            onFetchOllamaModels={fetchOllamaModels}
            onSave={save}
          />
        )}
      </section>

      <hr className="border-gray-200 dark:border-gray-700" />

      <section className="space-y-4">
        <h1 className="text-xl font-bold">データ管理</h1>

        <div className="space-y-2">
          <div className="space-y-2">
            <button
              onClick={triggerFetch}
              disabled={isFetching}
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold disabled:opacity-50"
            >
              {isFetching ? '開始中...' : 'データ取得'}
            </button>
            {status?.scraping_in_progress && (
              <ScrapeProgressBar
                progress={status.scraping_progress}
                step={status.scraping_step}
              />
            )}
          </div>
          {dataError && <p className="text-sm text-red-500">{dataError}</p>}
        </div>

        {status === null ? (
          <p className="text-sm text-gray-500">読み込み中...</p>
        ) : (
          <>
            <div className="flex border-b dark:border-gray-700 sm:hidden">
              <button
                onClick={() => setDataTab('dates')}
                className={`flex-1 py-2 text-sm font-medium border-b-2 transition-colors ${
                  dataTab === 'dates'
                    ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                }`}
              >
                日付選択
              </button>
              <button
                onClick={() => setDataTab('pokemons')}
                className={`flex-1 py-2 text-sm font-medium border-b-2 transition-colors ${
                  dataTab === 'pokemons'
                    ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                }`}
              >
                ポケモン一覧
              </button>
            </div>

            <div className="sm:flex sm:gap-4 sm:items-stretch">
              <div
                className={`sm:block sm:w-64 sm:shrink-0 ${dataTab === 'dates' ? 'block' : 'hidden'}`}
              >
                <DataCardList
                  details={status.dates_detail}
                  selectedDate={status.selected_date}
                  onSelect={onSelectDate}
                />
              </div>
              <div className="hidden sm:block w-px bg-gray-300 dark:bg-gray-600 self-stretch" />
              <div
                className={`sm:block sm:flex-1 sm:min-w-0 ${dataTab === 'pokemons' ? 'block' : 'hidden'}`}
              >
                <PokemonPanelGrid pokemonList={pokemonList} />
              </div>
            </div>
          </>
        )}
      </section>
    </div>
  )
}
