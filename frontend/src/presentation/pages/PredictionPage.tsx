import { useState, useEffect, useRef } from 'react'
import PartyInput from '../components/PartyInput'
import PredictionResultView from '../components/PredictionResult'
import { usePredict } from '../../application/hooks/usePredict'
import { useParty } from '../../application/hooks/useParty'
import { usePokemonData } from '../../application/hooks/usePokemonData'
import { useRecognition } from '../../application/hooks/useRecognition'
import { useDataManagement } from '../../application/hooks/useDataManagement'
import type { RecognizedParties } from '../../application/hooks/useRecognition'
import type { Party } from '../../domain/entities/party'

export default function PredictionPage() {
  const [opponentParty, setOpponentParty] = useState<string[]>(Array(6).fill(''))
  const [myPartySlots, setMyPartySlots] = useState<string[]>(Array(6).fill(''))
  const { result, loading, error, handlePredict } = usePredict()
  const { parties, selectedPartyId, myParty, selectParty } = useParty()
  const { pokemonList } = usePokemonData()
  const { recognizeImage } = useRecognition()
  const { status } = useDataManagement()
  const initializedRef = useRef(false)

  const hasData = status !== null && status.available_dates.length > 0

  const isReady =
    hasData &&
    opponentParty.filter(Boolean).length >= 3 &&
    myPartySlots.filter(Boolean).length >= 1

  useEffect(() => {
    if (!initializedRef.current && myParty.some(Boolean)) {
      setMyPartySlots([...myParty, ...Array(6).fill('')].slice(0, 6))
      initializedRef.current = true
    }
  }, [myParty])

  const stemToName = (stem: string): string => {
    if (!stem) return ''
    return pokemonList.find((p) => p.sprite_path === `sprites/${stem}.png`)?.name ?? stem
  }

  const handleImageUpload = async (file: File): Promise<RecognizedParties> => {
    const recognized = await recognizeImage(file)
    const mappedOpponent = recognized.opponentParty.map(stemToName)
    const mappedMy = recognized.myParty.map(stemToName)
    setMyPartySlots(mappedMy)
    return { opponentParty: mappedOpponent, myParty: mappedMy }
  }

  const handleSelectParty = (p: Party) => {
    selectParty(p)
    setMyPartySlots([...p.pokemons, ...Array(6).fill('')].slice(0, 6))
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {status !== null && !hasData && (
        <p className="text-sm text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 rounded-lg px-4 py-3">
          データが取得されていません。データ管理ページからデータを取得してください。
        </p>
      )}

      <PartyInput party={opponentParty} onChange={setOpponentParty} pokemonList={pokemonList} onImageUpload={handleImageUpload} />

      <div className="border rounded-xl p-4 dark:border-gray-700 space-y-3">
        {parties.length > 0 && (
          <div className="flex gap-2 flex-wrap">
            {parties.map((p) => (
              <button
                key={p.id}
                onClick={() => handleSelectParty(p)}
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
        <PartyInput
          party={myPartySlots}
          onChange={setMyPartySlots}
          pokemonList={pokemonList}
          label="自分のパーティ"
        />
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <button
        onClick={() => handlePredict(opponentParty, myPartySlots)}
        disabled={loading || !isReady}
        className="w-full py-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold disabled:opacity-50"
      >
        {loading ? '予想中...' : '選出予想する'}
      </button>

      {result && <PredictionResultView result={result} pokemonList={pokemonList} />}
    </div>
  )
}
