import { useState, useEffect, useRef, useCallback } from 'react'
import { toast } from 'sonner'
import { fetchData, getDataStatus, selectDate, getPokemonList, DataStatus } from '../../infrastructure/api/dataApi'
import type { PokemonListEntry } from '../../domain/entities/pokemon'

const LS_SCRAPING_PENDING = 'scraping_pending'
const LS_LAST_NOTIFIED_AT = 'last_notified_at'

interface UseDataManagementReturn {
  status: DataStatus | null
  pokemonList: PokemonListEntry[]
  isFetching: boolean
  error: string | null
  triggerFetch: () => Promise<void>
  handleSelectDate: (date: string) => Promise<void>
}

export function useDataManagement(): UseDataManagementReturn {
  const [status, setStatus] = useState<DataStatus | null>(null)
  const [pokemonList, setPokemonList] = useState<PokemonListEntry[]>([])
  const [isFetching, setIsFetching] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const wasScrapingRef = useRef(false)

  const maybeNotify = useCallback((s: DataStatus) => {
    if (
      localStorage.getItem(LS_SCRAPING_PENDING) === 'true' &&
      s.last_scraped_at !== null &&
      s.last_scraped_at !== localStorage.getItem(LS_LAST_NOTIFIED_AT)
    ) {
      toast.success('データ取得が完了しました')
      localStorage.setItem(LS_LAST_NOTIFIED_AT, s.last_scraped_at)
      localStorage.removeItem(LS_SCRAPING_PENDING)
    }
  }, [])

  const loadStatus = useCallback(async (): Promise<DataStatus | null> => {
    try {
      const s = await getDataStatus()
      setStatus(s)
      return s
    } catch {
      return null
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
    const init = async () => {
      const s = await loadStatus()
      if (s && !s.scraping_in_progress) {
        maybeNotify(s)
      }
    }
    init()
    loadPokemonList()
  }, [loadStatus, loadPokemonList, maybeNotify])

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
        if (status) {
          maybeNotify(status)
        }
        loadPokemonList()
      }
    }
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    }
  }, [status?.scraping_in_progress, status, loadStatus, loadPokemonList, maybeNotify])

  const triggerFetch = useCallback(async () => {
    setIsFetching(true)
    setError(null)
    try {
      await fetchData()
      localStorage.setItem(LS_SCRAPING_PENDING, 'true')
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

  return { status, pokemonList, isFetching, error, triggerFetch, handleSelectDate }
}
