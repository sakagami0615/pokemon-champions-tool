import { useRef } from 'react'
import PokemonSlot from './PokemonSlot'

interface Props {
  party: string[]
  onChange: (party: string[]) => void
  pokemonNames: string[]
  onImageUpload: (file: File) => Promise<string[]>
}

export default function PartyInput({ party, onChange, pokemonNames, onImageUpload }: Props) {
  const fileRef = useRef<HTMLInputElement>(null)

  const update = (index: number, name: string) => {
    const next = [...party]
    next[index] = name
    onChange(next)
  }

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      const names = await onImageUpload(file)
      onChange(names)
    } catch (err) {
      alert(`画像認識に失敗しました: ${err}`)
    } finally {
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="font-bold text-sm text-gray-600 dark:text-gray-400">相手パーティ</h2>
        <button
          onClick={() => fileRef.current?.click()}
          className="text-xs px-3 py-1 rounded bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600"
        >
          画像から入力
        </button>
        <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={handleImageUpload} />
      </div>
      <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
        {party.map((name, i) => (
          <PokemonSlot key={i} value={name} onChange={v => update(i, v)} pokemonNames={pokemonNames} />
        ))}
      </div>
    </div>
  )
}
