import { useState } from 'react'
import PartyInput from '../components/PartyInput'
import PredictionResultView from '../components/PredictionResult'
import { usePredict } from '../../application/hooks/usePredict'
import { useParty } from '../../application/hooks/useParty'
import { usePokemonData } from '../../application/hooks/usePokemonData'
import { useRecognition } from '../../application/hooks/useRecognition'

export default function PredictionPage() {
  const [opponentParty, setOpponentParty] = useState<string[]>(Array(6).fill(''))
  const { result, loading, error, handlePredict } = usePredict()
  const { parties, selectedPartyId, myParty, selectParty } = useParty()
  const { pokemonNames } = usePokemonData()
  const { recognizeImage } = useRecognition()

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <PartyInput party={opponentParty} onChange={setOpponentParty} pokemonNames={pokemonNames} onImageUpload={recognizeImage} />

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
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <button
        onClick={() => handlePredict(opponentParty, myParty)}
        disabled={loading}
        className="w-full py-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold disabled:opacity-50"
      >
        {loading ? '予想中...' : '選出予想する'}
      </button>

      {result && <PredictionResultView result={result} />}
    </div>
  )
}
