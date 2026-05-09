import { useState, useEffect, useRef } from 'react'
import PartyInput from '../components/PartyInput'
import PredictionResultView from '../components/PredictionResult'
import { usePredict } from '../../application/hooks/usePredict'
import { useParty } from '../../application/hooks/useParty'
import { usePokemonData } from '../../application/hooks/usePokemonData'
import { useRecognition } from '../../application/hooks/useRecognition'
import { useDataManagement } from '../../application/hooks/useDataManagement'
import type { Party } from '../../domain/entities/party'

export default function PredictionPage() {
  const [opponentParty, setOpponentParty] = useState<string[]>(Array(6).fill(''))
  const [myPartySlots, setMyPartySlots] = useState<string[]>(Array(6).fill(''))
  const [cameraMyParty, setCameraMyParty] = useState<string[]>(Array(6).fill(''))
  const [cameraSelected, setCameraSelected] = useState(false)
  const { result, loading, error, handlePredict } = usePredict()
  const { parties, selectedPartyId, myParty, selectParty, clearSelectedParty } = useParty()
  const { pokemonList } = usePokemonData()
  const { recognizeImage } = useRecognition()
  const { status } = useDataManagement()
  const initializedRef = useRef(false)
  const opponentFileRef = useRef<HTMLInputElement>(null)

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

  const handleOpponentFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      const recognized = await recognizeImage(file)
      const mappedOpponent = recognized.opponentParty.map(stemToName)
      const mappedMy = recognized.myParty.map(stemToName)
      setOpponentParty(mappedOpponent)
      setCameraMyParty(mappedMy)
      setMyPartySlots(mappedMy)
      setCameraSelected(true)
      clearSelectedParty()
    } catch (err) {
      alert(`画像認識に失敗しました: ${err}`)
    } finally {
      if (opponentFileRef.current) opponentFileRef.current.value = ''
    }
  }

  const handleSelectCamera = () => {
    setMyPartySlots(cameraMyParty)
    setCameraSelected(true)
    clearSelectedParty()
  }

  const handleSelectParty = (p: Party) => {
    selectParty(p)
    setMyPartySlots([...p.pokemons, ...Array(6).fill('')].slice(0, 6))
    setCameraSelected(false)
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {status !== null && !hasData && (
        <p className="text-sm text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 rounded-lg px-4 py-3">
          データが取得されていません。データ管理ページからデータを取得してください。
        </p>
      )}

      <div className="space-y-2">
        <div className="flex justify-end">
          <button
            onClick={() => opponentFileRef.current?.click()}
            className="text-xs px-3 py-1 rounded bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            画像から入力
          </button>
          <input ref={opponentFileRef} type="file" accept="image/*" className="hidden" onChange={handleOpponentFileChange} />
        </div>
        <div className="border rounded-xl p-4 dark:border-gray-700">
          <PartyInput party={opponentParty} onChange={setOpponentParty} pokemonList={pokemonList} label="相手のパーティ" />
        </div>
      </div>

      <div className="border rounded-xl p-4 dark:border-gray-700 space-y-3">
        <h2 className="font-bold text-sm text-gray-600 dark:text-gray-400">自分のパーティ</h2>
        {(parties.length > 0 || cameraMyParty.some(Boolean)) && (
          <div className="flex gap-2 flex-wrap">
            {cameraMyParty.some(Boolean) && (
              <button
                onClick={handleSelectCamera}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
                  cameraSelected
                    ? 'bg-indigo-600 text-white border-indigo-600'
                    : 'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                画像入力
              </button>
            )}
            {parties.map((p) => (
              <button
                key={p.id}
                onClick={() => handleSelectParty(p)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
                  !cameraSelected && selectedPartyId === p.id
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
