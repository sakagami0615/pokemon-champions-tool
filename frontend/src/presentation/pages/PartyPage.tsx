import { useState } from 'react'
import PokemonSlot from '../components/PokemonSlot'
import { useParty } from '../../application/hooks/useParty'
import { usePokemonData } from '../../application/hooks/usePokemonData'
import type { Party } from '../../domain/entities/party'

export default function PartyPage() {
  const { parties, createNewParty, updateExistingParty, removeParty } = useParty()
  const { pokemonNames } = usePokemonData()
  const [editing, setEditing] = useState<Party | null>(null)
  const [name, setName] = useState('')
  const [pokemon, setPokemon] = useState<string[]>(Array(6).fill(''))

  const startNew = () => {
    setEditing(null)
    setName('')
    setPokemon(Array(6).fill(''))
  }

  const startEdit = (p: Party) => {
    setEditing(p)
    setName(p.name)
    setPokemon([...p.pokemon, ...Array(6).fill('')].slice(0, 6))
  }

  const save = async () => {
    if (!name) return
    const filled = pokemon.filter(Boolean)
    if (editing) {
      await updateExistingParty(editing.id, name, filled)
    } else {
      await createNewParty(name, filled)
    }
    startNew()
  }

  const remove = async (id: string) => {
    if (!confirm('削除しますか？')) return
    await removeParty(id)
  }

  const isSaveable = name.trim().length > 0 && pokemon.filter(Boolean).length >= 3

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="font-bold text-xl">パーティ登録</h1>

      <div className="border rounded-xl p-4 space-y-4 dark:border-gray-700">
        <h2 className="font-bold text-sm text-gray-600 dark:text-gray-400">
          {editing ? `編集中: ${editing.name}` : '新規パーティ'}
        </h2>
        <input
          className="w-full border rounded px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600"
          placeholder="パーティ名"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
          {pokemon.map((p, i) => (
            <PokemonSlot
              key={i}
              value={p}
              onChange={(v) => setPokemon(pokemon.map((p, j) => (j === i ? v : p)))}
              pokemonNames={pokemonNames}
            />
          ))}
        </div>
        <div className="flex gap-2">
          <button
            onClick={save}
            disabled={!isSaveable}
            className="px-4 py-2 rounded bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold disabled:opacity-50"
          >
            {editing ? '更新' : '登録'}
          </button>
          {editing && (
            <button
              onClick={startNew}
              className="px-4 py-2 rounded border dark:border-gray-600 text-sm"
            >
              キャンセル
            </button>
          )}
        </div>
      </div>

      <div className="space-y-3">
        {parties.map((p) => (
          <div key={p.id} className="border rounded-xl p-4 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="font-bold">{p.name}</span>
              <div className="flex gap-2">
                <button onClick={() => startEdit(p)} className="text-sm text-indigo-600 hover:underline">
                  編集
                </button>
                <button onClick={() => remove(p.id)} className="text-sm text-red-500 hover:underline">
                  削除
                </button>
              </div>
            </div>
            <div className="flex gap-2 flex-wrap">
              {p.pokemon.map((pname, i) => (
                <div key={i} className="text-center">
                  <img
                    src={`/sprites/${pname}.png`}
                    alt={pname}
                    className="w-10 h-10 object-contain mx-auto"
                    onError={(e) => {
                      ;(e.target as HTMLImageElement).style.display = 'none'
                    }}
                  />
                  <div className="text-xs">{pname}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
