import { useState } from 'react'
import PartyInput from '../components/PartyInput'
import PredictionResultView from '../components/PredictionResult'
import { usePredict } from '../../application/hooks/usePredict'
import { useParty } from '../../application/hooks/useParty'
import { usePokemonData } from '../../application/hooks/usePokemonData'
import { useRecognition } from '../../application/hooks/useRecognition'
import { useDataManagement } from '../../application/hooks/useDataManagement'
import type { RecognizedParties } from '../../application/hooks/useRecognition'

export default function PredictionPage() {
  const [opponentParty, setOpponentParty] = useState<string[]>(Array(6).fill(''))
  const [cameraMyParty, setCameraMyParty] = useState<string[]>(Array(6).fill(''))
  const { result, loading, error, handlePredict } = usePredict()
  const { parties, selectedPartyId, myParty, selectParty } = useParty()
  const { pokemonList } = usePokemonData()
  const { recognizeImage } = useRecognition()
  const { status } = useDataManagement()

  const hasData = status !== null && status.available_dates.length > 0
  const effectiveMyParty = selectedPartyId !== null ? myParty : cameraMyParty

  const isReady =
    hasData &&
    opponentParty.filter(Boolean).length >= 3 &&
    effectiveMyParty.filter(Boolean).length >= 1

  const handleImageUpload = async (file: File): Promise<RecognizedParties> => {
    const recognized = await recognizeImage(file)
    setCameraMyParty(recognized.myParty)
    return recognized
  }

  const displayParty = effectiveMyParty.filter(Boolean)

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {status !== null && !hasData && (
        <p className="text-sm text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 rounded-lg px-4 py-3">
          データが取得されていません。データ管理ページからデータを取得してください。
        </p>
      )}

      <PartyInput party={opponentParty} onChange={setOpponentParty} pokemonList={pokemonList} onImageUpload={handleImageUpload} />

      <div className="border rounded-xl p-4 dark:border-gray-700 space-y-3">
        <h2 className="font-bold text-sm text-gray-600 dark:text-gray-400">自分のパーティ</h2>
        {parties.length === 0 ? (
          <p className="text-sm text-gray-400">パーティが登録されていません</p>
        ) : (
          <div className="flex gap-2 flex-wrap">
            {parties.map((p) => (
              <button
                key={p.id}
                onClick={() => selectParty(p)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
                  selectedPartyId === p.id
                    ? 'bg-indigo-600 text-white border-indigo-600'
                    : 'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                {p.name}
              </button>
            ))}
          </div>
        )}
        {displayParty.length > 0 && (
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 justify-items-center pt-4 border-t dark:border-gray-700">
            {displayParty.map((pokemon, i) => {
              const spriteSrc = pokemonList.find((e) => e.name === pokemon)?.sprite_path
              return (
                <div key={`${i}-${pokemon}`} className="text-center">
                  {spriteSrc && (
                    <img
                      src={`/${spriteSrc}`}
                      alt={pokemon}
                      className="w-10 h-10 object-contain mx-auto"
                    />
                  )}
                  <div className="text-xs mt-0.5">{pokemon}</div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <button
        onClick={() => handlePredict(opponentParty, effectiveMyParty)}
        disabled={loading || !isReady}
        className="w-full py-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold disabled:opacity-50"
      >
        {loading ? '予想中...' : '選出予想する'}
      </button>

      {result && <PredictionResultView result={result} pokemonList={pokemonList} />}
    </div>
  )
}
