import { useState, useEffect } from 'react'
import PartyInput from '../components/PartyInput'
import PredictionResultView from '../components/PredictionResult'
import { predict, getParties, setLastUsedParty, getPokemonNames } from '../../infrastructure/api/client'
import type { PredictionResult, Party, PartiesData } from '../../domain/entities'

export default function PredictionPage() {
  const [opponentParty, setOpponentParty] = useState<string[]>(Array(6).fill(''))
  const [myParty, setMyParty] = useState<string[]>(Array(6).fill(''))
  const [parties, setParties] = useState<Party[]>([])
  const [selectedPartyId, setSelectedPartyId] = useState<string | null>(null)
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pokemonNames, setPokemonNames] = useState<string[]>([])

  useEffect(() => {
    getPokemonNames().then(setPokemonNames)
    getParties().then((data: PartiesData) => {
      setParties(data.parties)
      if (data.last_used_id) {
        const last = data.parties.find(p => p.id === data.last_used_id)
        if (last) {
          setMyParty([...last.pokemon, ...Array(6).fill('')].slice(0, 6))
          setSelectedPartyId(last.id)
        }
      }
    })
  }, [])

  const handlePartySelect = async (party: Party) => {
    setMyParty([...party.pokemon, ...Array(6).fill('')].slice(0, 6))
    setSelectedPartyId(party.id)
    await setLastUsedParty(party.id)
  }

  const handlePredict = async () => {
    const opponent = opponentParty.filter(Boolean)
    const my = myParty.filter(Boolean)
    if (opponent.length < 6) { setError('相手パーティを6体入力してください'); return }
    if (my.length < 6) { setError('自分のパーティを6体入力してください'); return }
    setError(null)
    setLoading(true)
    try {
      const res = await predict(opponent, my)
      setResult(res)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <PartyInput party={opponentParty} onChange={setOpponentParty} pokemonNames={pokemonNames} />

      <div>
        <h2 className="font-bold text-sm text-gray-600 dark:text-gray-400 mb-2">自分のパーティ</h2>
        <div className="flex gap-2 flex-wrap">
          {parties.map(p => (
            <button
              key={p.id}
              onClick={() => handlePartySelect(p)}
              className={`px-3 py-1 rounded text-sm border ${selectedPartyId === p.id ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'}`}
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <button
        onClick={handlePredict}
        disabled={loading}
        className="w-full py-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold disabled:opacity-50"
      >
        {loading ? '予想中...' : '選出予想する'}
      </button>

      {result && <PredictionResultView result={result} />}
    </div>
  )
}
