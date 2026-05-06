import { useState, useEffect, useRef, useCallback } from 'react'
import { fetchData, getDataStatus, selectDate, getPokemonList, DataStatus } from '../../infrastructure/api/dataApi'
import type { PokemonListEntry } from '../../domain/entities/pokemon'

interface UseDataManagementReturn {
  status: DataStatus | null
  pokemonList: PokemonListEntry[]
  isFetching: boolean
  fetchMessage: string | null
  error: string | null
  triggerFetch: () => Promise<void>
  handleSelectDate: (date: string) => Promise<void>
}

export function useDataManagement(): UseDataManagementReturn {
  const [status, setStatus] = useState<DataStatus | null>(null)
  const [pokemonList, setPokemonList] = useState<PokemonListEntry[]>([])
  const [isFetching, setIsFetching] = useState(false)
  const [fetchMessage, setFetchMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const wasScrapingRef = useRef(false)

  const loadStatus = useCallback(async () => {
    try {
      const s = await getDataStatus()
      setStatus(s)
    } catch {
    }
  }, [])

  const loadPokemonList = useCallback(async () => {
    try {
      const res = await getPokemonList()
      setPokemonList([...res.pokemons, ...res.mega_pokemons])
    } catch {
    }
  }, [])

  useEffect(() => {
    loadStatus()
    loadPokemonList()
  }, [loadStatus, loadPokemonList])

  useEffect(() => {
    if (status?.scraping_in_progress) {
      wasScrapingRef.current = true
      pollingRef.current = setInterval(loadStatus, 3000)
    } else {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
      if (wasScrapingRef.current) {
        wasScrapingRef.current = false
        loadPokemonList()
      }
    }
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    }
  }, [status?.scraping_in_progress, loadStatus, loadPokemonList])

  const triggerFetch = useCallback(async () => {
    setIsFetching(true)
    setError(null)
    setFetchMessage(null)
    try {
      await fetchData()
      setFetchMessage('データ取得を開始しました')
      await loadStatus()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'データ取得の開始に失敗しました')
    } finally {
      setIsFetching(false)
    }
  }, [loadStatus])

  const handleSelectDate = useCallback(async (date: string) => {
    setError(null)
    const previous = status?.selected_date ?? null
    setStatus((prev) => prev ? { ...prev, selected_date: date } : prev)
    try {
      await selectDate(date)
      await loadPokemonList()
    } catch (e) {
      setStatus((prev) => prev ? { ...prev, selected_date: previous } : prev)
      setError(e instanceof Error ? e.message : '日付の選択に失敗しました')
    }
  }, [status?.selected_date, loadPokemonList])

  return { status, pokemonList, isFetching, fetchMessage, error, triggerFetch, handleSelectDate }
}
