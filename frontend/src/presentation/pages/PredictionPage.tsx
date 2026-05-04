import { useState } from 'react'
import PartyInput from '../components/PartyInput'
import PredictionResultView from '../components/PredictionResult'
import { usePredict } from '../../application/hooks/usePredict'
import { useParty } from '../../application/hooks/useParty'
import { usePokemonData } from '../../application/hooks/usePokemonData'
import { useRecognition } from '../../application/hooks/useRecognition'
import { useDataManagement } from '../../application/hooks/useDataManagement'

export default function PredictionPage() {
  const [opponentParty, setOpponentParty] = useState<string[]>(Array(6).fill(''))
  const { result, loading, error, handlePredict } = usePredict()
  const { parties, selectedPartyId, myParty, selectParty } = useParty()
  const { pokemonList } = usePokemonData()
  const { recognizeImage } = useRecognition()
  const { status } = useDataManagement()

  const hasData = status !== null && status.available_dates.length > 0

  const isReady =
    hasData &&
    opponentParty.filter(Boolean).length >= 3 &&
    selectedPartyId !== null

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {status !== null && !hasData && (
        <p className="text-sm text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 rounded-lg px-4 py-3">
          データが取得されていません。データ管理ページからデータを取得してください。
        </p>
      )}

      <PartyInput party={opponentParty} onChange={setOpponentParty} pokemonList={pokemonList} onImageUpload={recognizeImage} />

      <div>
        <h2 className="font-bold text-sm text-gray-600 dark:text-gray-400 mb-2">自分のパーティ</h2>
        <div className="flex gap-2 flex-wrap">
          {parties.map((p) => (
            <button
              key={p.id}
              onClick={() => selectParty(p)}
              className={`px-3 py-1 rounded text-sm border ${
                selectedPartyId === p.id
                  ? 'bg-indigo-600 text-white border-indigo-600'
                  : 'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              {p.name}
            </button>
          ))}
        </div>
        {selectedPartyId && (
          <div className="flex gap-2 flex-wrap mt-2">
            {myParty.filter(Boolean).map((pokemon, i) => (
              <span
                key={i}
                className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-sm text-gray-700 dark:text-gray-300"
              >
                {pokemon}
              </span>
            ))}
          </div>
        )}
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <button
        onClick={() => handlePredict(opponentParty, myParty)}
        disabled={loading || !isReady}
        className="w-full py-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold disabled:opacity-50"
      >
        {loading ? '予想中...' : '選出予想する'}
      </button>

      {result && <PredictionResultView result={result} pokemonList={pokemonList} />}
    </div>
  )
}
