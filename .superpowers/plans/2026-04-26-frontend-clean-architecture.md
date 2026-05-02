# フロントエンド Clean Architecture フォルダ再編 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** フロントエンドの `src/` ディレクトリを種類別構成から Clean Architecture のレイヤー別構成（domain/infrastructure/presentation）に再編する

**Architecture:** ファイルを domain（エンティティ型定義）、infrastructure（APIクライアント）、presentation（React コンポーネント・ページ・フック）の3レイヤーに移動する。ロジックの変更は一切行わず、ファイルの移動と import パスの更新のみを実施する。

**Tech Stack:** React 18, TypeScript 5.6, Vite, Tailwind CSS, Docker

---

## ファイル変更マッピング

| 移動前 | 移動後 |
|---|---|
| `src/types/index.ts` | `src/domain/entities/index.ts` |
| `src/api/client.ts` | `src/infrastructure/api/client.ts` |
| `src/hooks/useDarkMode.ts` | `src/presentation/hooks/useDarkMode.ts` |
| `src/components/DarkModeToggle.tsx` | `src/presentation/components/DarkModeToggle.tsx` |
| `src/components/Header.tsx` | `src/presentation/components/Header.tsx` |
| `src/components/PartyInput.tsx` | `src/presentation/components/PartyInput.tsx` |
| `src/components/PatternCard.tsx` | `src/presentation/components/PatternCard.tsx` |
| `src/components/PokemonCard.tsx` | `src/presentation/components/PokemonCard.tsx` |
| `src/components/PokemonSlot.tsx` | `src/presentation/components/PokemonSlot.tsx` |
| `src/components/PredictionResult.tsx` | `src/presentation/components/PredictionResult.tsx` |
| `src/pages/PartyPage.tsx` | `src/presentation/pages/PartyPage.tsx` |
| `src/pages/PredictionPage.tsx` | `src/presentation/pages/PredictionPage.tsx` |

---

## Task 1: domain/entities レイヤー作成

**Files:**
- Create: `frontend/src/domain/entities/index.ts`
- Delete: `frontend/src/types/index.ts`（Task 7 で削除）

- [ ] **Step 1: `domain/entities/index.ts` を作成**

```typescript
export interface RatedItem {
  name: string
  rate: number
}

export interface EvSpread {
  spread: Record<string, number>
  rate: number
}

export interface UsageEntry {
  name: string
  moves: RatedItem[]
  items: RatedItem[]
  abilities: RatedItem[]
  natures: RatedItem[]
  teammates: RatedItem[]
  evs: EvSpread[]
  ivs: Record<string, number> | null
}

export interface PredictionPattern {
  pokemon: string[]
}

export interface PredictionResult {
  patterns: PredictionPattern[]
}

export interface Party {
  id: string
  name: string
  pokemon: string[]
}

export interface PartiesData {
  parties: Party[]
  last_used_id: string | null
}
```

ファイルパス: `frontend/src/domain/entities/index.ts`

---

## Task 2: infrastructure/api レイヤー作成

**Files:**
- Create: `frontend/src/infrastructure/api/client.ts`
- Delete: `frontend/src/api/client.ts`（Task 7 で削除）

- [ ] **Step 1: `infrastructure/api/client.ts` を作成**

```typescript
const BASE = '/api'

export async function recognize(file: File): Promise<{ names: string[]; confidences: number[] }> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/recognize`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function predict(opponentParty: string[], myParty: string[]) {
  const res = await fetch(`${BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ opponent_party: opponentParty, my_party: myParty }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getParties() {
  const res = await fetch(`${BASE}/party`)
  return res.json()
}

export async function createParty(name: string, pokemon: string[]) {
  const res = await fetch(`${BASE}/party`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, pokemon }),
  })
  return res.json()
}

export async function updateParty(id: string, name: string, pokemon: string[]) {
  const res = await fetch(`${BASE}/party/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, pokemon }),
  })
  return res.json()
}

export async function deleteParty(id: string) {
  await fetch(`${BASE}/party/${id}`, { method: 'DELETE' })
}

export async function setLastUsedParty(id: string) {
  await fetch(`${BASE}/party/last-used/${id}`, { method: 'POST' })
}

export async function fetchData() {
  const res = await fetch(`${BASE}/data/fetch`, { method: 'POST' })
  return res.json()
}

export async function getDataStatus() {
  const res = await fetch(`${BASE}/data/status`)
  return res.json()
}

export async function getPokemonNames(): Promise<string[]> {
  const res = await fetch(`${BASE}/data/pokemon/names`)
  const data = await res.json()
  return data.names as string[]
}
```

ファイルパス: `frontend/src/infrastructure/api/client.ts`

---

## Task 3: presentation/hooks 作成

**Files:**
- Create: `frontend/src/presentation/hooks/useDarkMode.ts`
- Delete: `frontend/src/hooks/useDarkMode.ts`（Task 7 で削除）

- [ ] **Step 1: `presentation/hooks/useDarkMode.ts` を作成**

```typescript
import { useEffect, useState } from 'react'

export function useDarkMode() {
  const [dark, setDark] = useState(() => localStorage.getItem('dark-mode') === 'true')

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('dark-mode', String(dark))
  }, [dark])

  return { dark, toggle: () => setDark(d => !d) }
}
```

ファイルパス: `frontend/src/presentation/hooks/useDarkMode.ts`

---

## Task 4: presentation/components 作成（import 更新あり）

**Files:**
- Create: `frontend/src/presentation/components/DarkModeToggle.tsx`（import 変更なし）
- Create: `frontend/src/presentation/components/Header.tsx`（import 変更なし）
- Create: `frontend/src/presentation/components/PokemonSlot.tsx`（import 変更なし）
- Create: `frontend/src/presentation/components/PokemonCard.tsx`（import パス変更あり）
- Create: `frontend/src/presentation/components/PatternCard.tsx`（import パス変更あり）
- Create: `frontend/src/presentation/components/PredictionResult.tsx`（import パス変更あり）
- Create: `frontend/src/presentation/components/PartyInput.tsx`（import パス変更あり）
- Delete: `frontend/src/components/` 配下の全ファイル（Task 7 で削除）

- [ ] **Step 1: `DarkModeToggle.tsx` を作成**（import 変更なし）

```typescript
interface Props { dark: boolean; onToggle: () => void }

export default function DarkModeToggle({ dark, onToggle }: Props) {
  return (
    <button
      onClick={onToggle}
      className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 text-sm"
      aria-label="ダークモード切り替え"
    >
      {dark ? '☀️ ライト' : '🌙 ダーク'}
    </button>
  )
}
```

ファイルパス: `frontend/src/presentation/components/DarkModeToggle.tsx`

- [ ] **Step 2: `Header.tsx` を作成**（import 変更なし。同フォルダの DarkModeToggle を参照）

```typescript
import DarkModeToggle from './DarkModeToggle'

interface Props {
  dark: boolean
  onToggleDark: () => void
  page: 'prediction' | 'party'
  onChangePage: (p: 'prediction' | 'party') => void
}

export default function Header({ dark, onToggleDark, page, onChangePage }: Props) {
  return (
    <header className="border-b border-gray-200 dark:border-gray-700 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <span className="font-bold text-lg">Pokemon Champions Tool</span>
        <nav className="flex gap-2">
          <button
            onClick={() => onChangePage('prediction')}
            className={`px-3 py-1 rounded text-sm ${page === 'prediction' ? 'bg-indigo-600 text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
          >
            選出予想
          </button>
          <button
            onClick={() => onChangePage('party')}
            className={`px-3 py-1 rounded text-sm ${page === 'party' ? 'bg-indigo-600 text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
          >
            パーティ登録
          </button>
        </nav>
      </div>
      <DarkModeToggle dark={dark} onToggle={onToggleDark} />
    </header>
  )
}
```

ファイルパス: `frontend/src/presentation/components/Header.tsx`

- [ ] **Step 3: `PokemonSlot.tsx` を作成**（import 変更なし）

```typescript
import { useState, useEffect, useRef } from 'react'

interface Props {
  value: string
  onChange: (name: string) => void
  pokemonNames: string[]
}

export default function PokemonSlot({ value, onChange, pokemonNames }: Props) {
  const [query, setQuery] = useState(value)
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => { setQuery(value) }, [value])

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const filtered = query
    ? pokemonNames.filter(n => n.includes(query)).slice(0, 8)
    : pokemonNames.slice(0, 8)

  const select = (name: string) => {
    onChange(name)
    setQuery(name)
    setOpen(false)
  }

  return (
    <div ref={ref} className="relative">
      {value ? (
        <div
          className="flex flex-col items-center gap-1 p-2 rounded-lg border-2 border-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 cursor-pointer"
          onClick={() => { onChange(''); setQuery('') }}
          title="クリックでリセット"
        >
          <img
            src={`/sprites/${value}.png`}
            alt={value}
            className="w-12 h-12 object-contain"
            onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
          />
          <span className="text-xs font-bold">{value}</span>
        </div>
      ) : (
        <div className="rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 p-2">
          <input
            className="w-full text-sm bg-transparent outline-none placeholder-gray-400"
            placeholder="ポケモン名..."
            value={query}
            onChange={e => { setQuery(e.target.value); setOpen(true) }}
            onFocus={() => setOpen(true)}
          />
          {open && filtered.length > 0 && (
            <ul className="absolute z-10 top-full left-0 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg max-h-48 overflow-y-auto">
              {filtered.map(name => (
                <li
                  key={name}
                  className="flex items-center gap-2 px-3 py-2 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 cursor-pointer text-sm"
                  onMouseDown={() => select(name)}
                >
                  <img
                    src={`/sprites/${name}.png`}
                    alt={name}
                    className="w-8 h-8 object-contain"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
                  />
                  {name}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
```

ファイルパス: `frontend/src/presentation/components/PokemonSlot.tsx`

- [ ] **Step 4: `PokemonCard.tsx` を作成**（`../types` → `../../domain/entities` に変更）

```typescript
import type { UsageEntry } from '../../domain/entities'

interface Props {
  name: string
  usage: UsageEntry | null
}

function labelColor(label: string) {
  const map: Record<string, string> = {
    'わざ': '#7c3aed', '持ち物': '#0369a1', '特性': '#065f46', '性格': '#92400e',
    '個体値': '#be185d', '能力ポイント': '#b45309',
  }
  return map[label] ?? '#374151'
}

function StatRow({ label, items }: { label: string; items: { name: string; rate: number }[] }) {
  return (
    <div className="mb-1">
      <span className="text-xs font-bold" style={{ color: labelColor(label) }}>{label}</span>
      {items.map((item, i) => (
        <div key={i} className="flex justify-between text-xs">
          <span>{item.name}</span>
          <span className={`font-bold ${i === 0 ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500'}`}>
            {item.rate}%
          </span>
        </div>
      ))}
    </div>
  )
}

export default function PokemonCard({ name, usage }: Props) {
  const ivText = usage?.ivs
    ? Object.entries(usage.ivs).map(([k, v]) => `${k}${v}`).join(' ')
    : 'H31 A31 B31 C31 D31 S31'

  return (
    <div className="flex-1 rounded-lg p-3 bg-gray-50 dark:bg-gray-800 min-w-0">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-shrink-0 text-center">
          <img
            src={`/sprites/${name}.png`}
            alt={name}
            className="w-14 h-14 object-contain mx-auto"
            onError={(e) => { (e.target as HTMLImageElement).src = '/sprites/unknown.png' }}
          />
          <div className="text-xs font-bold mt-1">{name}</div>
        </div>
        <div className="flex-1 min-w-0 text-xs">
          {usage ? (
            <>
              <StatRow label="わざ" items={usage.moves.slice(0, 3)} />
              <StatRow label="持ち物" items={usage.items.slice(0, 2)} />
              <StatRow label="特性" items={usage.abilities.slice(0, 2)} />
              <StatRow label="性格" items={usage.natures.slice(0, 2)} />
              <div className="mb-1">
                <span className="text-xs font-bold" style={{ color: '#be185d' }}>個体値</span>
                <div className="text-xs font-mono bg-pink-50 dark:bg-pink-900/20 rounded px-1 py-0.5">{ivText}</div>
              </div>
              <div className="mb-1">
                <span className="text-xs font-bold" style={{ color: '#b45309' }}>能力ポイント</span>
                {usage.evs.slice(0, 2).map((ev, i) => (
                  <div key={i} className="flex justify-between text-xs">
                    <span className="font-mono bg-yellow-50 dark:bg-yellow-900/20 rounded px-1 text-xs">
                      {Object.entries(ev.spread).filter(([, v]) => v > 0).map(([k, v]) => `${k}${v}`).join(' ')}
                    </span>
                    <span className={`font-bold ${i === 0 ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500'}`}>
                      {ev.rate}%
                    </span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <span className="text-gray-400">使用率データなし</span>
          )}
        </div>
      </div>
    </div>
  )
}
```

ファイルパス: `frontend/src/presentation/components/PokemonCard.tsx`

- [ ] **Step 5: `PatternCard.tsx` を作成**（`../types` → `../../domain/entities` に変更）

```typescript
import PokemonCard from './PokemonCard'
import type { PredictionPattern, UsageEntry } from '../../domain/entities'

interface Props {
  pattern: PredictionPattern
  index: number
  usageMap: Record<string, UsageEntry>
}

export default function PatternCard({ pattern, index, usageMap }: Props) {
  const isTop = index === 0
  return (
    <div className={`rounded-xl p-4 border-2 ${isTop ? 'border-indigo-500' : 'border-gray-200 dark:border-gray-700'}`}>
      <div className={`font-bold text-sm mb-3 ${isTop ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500'}`}>
        {isTop ? '🏆 ' : ''}パターン{index + 1}{isTop ? '（最有力）' : ''}
      </div>
      <div className="flex gap-2">
        {pattern.pokemon.map((name, i) => (
          <PokemonCard key={i} name={name} usage={usageMap[name] ?? null} />
        ))}
      </div>
    </div>
  )
}
```

ファイルパス: `frontend/src/presentation/components/PatternCard.tsx`

- [ ] **Step 6: `PredictionResult.tsx` を作成**（`../types` → `../../domain/entities` に変更）

```typescript
import PatternCard from './PatternCard'
import type { PredictionResult, UsageEntry } from '../../domain/entities'

interface Props {
  result: PredictionResult
  usageEntries?: UsageEntry[]
}

export default function PredictionResultView({ result, usageEntries = [] }: Props) {
  const usageMap: Record<string, UsageEntry> = Object.fromEntries(
    usageEntries.map(e => [e.name, e])
  )

  return (
    <div className="space-y-4">
      <h2 className="font-bold text-lg">選出予想</h2>
      {result.patterns.map((pattern, i) => (
        <PatternCard key={i} pattern={pattern} index={i} usageMap={usageMap} />
      ))}
    </div>
  )
}
```

ファイルパス: `frontend/src/presentation/components/PredictionResult.tsx`

- [ ] **Step 7: `PartyInput.tsx` を作成**（`../api/client` → `../../infrastructure/api/client` に変更）

```typescript
import { useRef } from 'react'
import PokemonSlot from './PokemonSlot'
import { recognize } from '../../infrastructure/api/client'

interface Props {
  party: string[]
  onChange: (party: string[]) => void
  pokemonNames: string[]
}

export default function PartyInput({ party, onChange, pokemonNames }: Props) {
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
      const result = await recognize(file)
      onChange(result.names.slice(0, 6))
    } catch (err) {
      alert(`画像認識に失敗しました: ${err}`)
    } finally {
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="font-bold text-sm text-gray-600 dark:text-gray-400">相手パーティ（6体）</h2>
        <button
          onClick={() => fileRef.current?.click()}
          className="text-xs px-3 py-1 rounded bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600"
        >
          📷 画像から入力
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
```

ファイルパス: `frontend/src/presentation/components/PartyInput.tsx`

---

## Task 5: presentation/pages 作成（import 更新あり）

**Files:**
- Create: `frontend/src/presentation/pages/PartyPage.tsx`
- Create: `frontend/src/presentation/pages/PredictionPage.tsx`
- Delete: `frontend/src/pages/` 配下の全ファイル（Task 7 で削除）

- [ ] **Step 1: `PartyPage.tsx` を作成**

変更点:
- `../components/PokemonSlot` → `../components/PokemonSlot`（同じ presentation 内なので変更なし）
- `../api/client` → `../../infrastructure/api/client`
- `../types` → `../../domain/entities`

```typescript
import { useState, useEffect } from 'react'
import PokemonSlot from '../components/PokemonSlot'
import { getParties, createParty, updateParty, deleteParty, getPokemonNames } from '../../infrastructure/api/client'
import type { Party } from '../../domain/entities'

export default function PartyPage() {
  const [parties, setParties] = useState<Party[]>([])
  const [editing, setEditing] = useState<Party | null>(null)
  const [name, setName] = useState('')
  const [pokemon, setPokemon] = useState<string[]>(Array(6).fill(''))
  const [pokemonNames, setPokemonNames] = useState<string[]>([])

  useEffect(() => {
    reload()
    getPokemonNames().then(setPokemonNames)
  }, [])

  const reload = () => getParties().then((d: { parties: Party[] }) => setParties(d.parties))

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
      await updateParty(editing.id, name, filled)
    } else {
      await createParty(name, filled)
    }
    startNew()
    reload()
  }

  const remove = async (id: string) => {
    if (!confirm('削除しますか？')) return
    await deleteParty(id)
    reload()
  }

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
          onChange={e => setName(e.target.value)}
        />
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
          {pokemon.map((p, i) => (
            <PokemonSlot
              key={i}
              value={p}
              onChange={v => { const next = [...pokemon]; next[i] = v; setPokemon(next) }}
              pokemonNames={pokemonNames}
            />
          ))}
        </div>
        <div className="flex gap-2">
          <button onClick={save} className="px-4 py-2 rounded bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold">
            {editing ? '更新' : '登録'}
          </button>
          {editing && (
            <button onClick={startNew} className="px-4 py-2 rounded border dark:border-gray-600 text-sm">
              キャンセル
            </button>
          )}
        </div>
      </div>

      <div className="space-y-3">
        {parties.map(p => (
          <div key={p.id} className="border rounded-xl p-4 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="font-bold">{p.name}</span>
              <div className="flex gap-2">
                <button onClick={() => startEdit(p)} className="text-sm text-indigo-600 hover:underline">編集</button>
                <button onClick={() => remove(p.id)} className="text-sm text-red-500 hover:underline">削除</button>
              </div>
            </div>
            <div className="flex gap-2 flex-wrap">
              {p.pokemon.map((pname, i) => (
                <div key={i} className="text-center">
                  <img
                    src={`/sprites/${pname}.png`}
                    alt={pname}
                    className="w-10 h-10 object-contain mx-auto"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
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
```

ファイルパス: `frontend/src/presentation/pages/PartyPage.tsx`

- [ ] **Step 2: `PredictionPage.tsx` を作成**

変更点:
- `../components/PartyInput` → `../components/PartyInput`（変更なし）
- `../components/PredictionResult` → `../components/PredictionResult`（変更なし）
- `../api/client` → `../../infrastructure/api/client`
- `../types` → `../../domain/entities`

```typescript
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
        {loading ? '予想中...' : '🔮 選出予想する'}
      </button>

      {result && <PredictionResultView result={result} />}
    </div>
  )
}
```

ファイルパス: `frontend/src/presentation/pages/PredictionPage.tsx`

---

## Task 6: App.tsx の import パスを更新

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: App.tsx を更新**

変更点:
- `./hooks/useDarkMode` → `./presentation/hooks/useDarkMode`
- `./pages/PredictionPage` → `./presentation/pages/PredictionPage`
- `./pages/PartyPage` → `./presentation/pages/PartyPage`
- `./components/Header` → `./presentation/components/Header`

```typescript
import { useState } from 'react'
import { useDarkMode } from './presentation/hooks/useDarkMode'
import PredictionPage from './presentation/pages/PredictionPage'
import PartyPage from './presentation/pages/PartyPage'
import Header from './presentation/components/Header'

type Page = 'prediction' | 'party'

export default function App() {
  const { dark, toggle } = useDarkMode()
  const [page, setPage] = useState<Page>('prediction')

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <Header dark={dark} onToggleDark={toggle} page={page} onChangePage={setPage} />
      <main className="p-4">
        {page === 'prediction' ? <PredictionPage /> : <PartyPage />}
      </main>
    </div>
  )
}
```

---

## Task 7: 旧フォルダの削除とビルド検証

**Files:**
- Delete: `frontend/src/types/` ディレクトリ
- Delete: `frontend/src/api/` ディレクトリ
- Delete: `frontend/src/hooks/` ディレクトリ
- Delete: `frontend/src/components/` ディレクトリ
- Delete: `frontend/src/pages/` ディレクトリ

- [ ] **Step 1: 旧ディレクトリを削除**

```bash
rm -rf frontend/src/types frontend/src/api frontend/src/hooks frontend/src/components frontend/src/pages
```

- [ ] **Step 2: 型チェックを実行して全エラーがないことを確認**

```bash
docker compose run --rm frontend sh -c "npx tsc -b --noEmit"
```

期待する出力: エラーなし（終了コード 0）

- [ ] **Step 3: ビルドを実行して成功することを確認**

```bash
docker compose run --rm frontend npm run build
```

期待する出力: `✓ built in` で終わるビルド成功メッセージ

---

## Task 8: コミット

- [ ] **Step 1: 変更をステージング**

```bash
git add frontend/src/domain/ frontend/src/infrastructure/ frontend/src/presentation/ frontend/src/App.tsx
git rm -r frontend/src/types frontend/src/api frontend/src/hooks frontend/src/components frontend/src/pages
```

- [ ] **Step 2: コミット**

```bash
git commit -m "refactor: フロントエンドをClean Architectureのフォルダ構成に再編"
```
