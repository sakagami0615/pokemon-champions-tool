import { useState, useEffect, useRef, useCallback } from 'react'
import { fetchData, getDataStatus, selectDate, DataStatus } from '../../infrastructure/api/dataApi'

interface UseDataManagementReturn {
  status: DataStatus | null
  isFetching: boolean
  fetchMessage: string | null
  error: string | null
  triggerFetch: () => Promise<void>
  handleSelectDate: (date: string) => Promise<void>
}

export function useDataManagement(): UseDataManagementReturn {
  const [status, setStatus] = useState<DataStatus | null>(null)
  const [isFetching, setIsFetching] = useState(false)
  const [fetchMessage, setFetchMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const loadStatus = useCallback(async () => {
    try {
      const s = await getDataStatus()
      setStatus(s)
    } catch {
      // ポーリング失敗は無視して次回に再試行
    }
  }, [])

  useEffect(() => {
    loadStatus()
  }, [loadStatus])

  useEffect(() => {
    if (status?.scraping_in_progress) {
      pollingRef.current = setInterval(loadStatus, 3000)
    } else {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    }
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    }
  }, [status?.scraping_in_progress, loadStatus])

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
    } catch (e) {
      setStatus((prev) => prev ? { ...prev, selected_date: previous } : prev)
      setError(e instanceof Error ? e.message : '日付の選択に失敗しました')
    }
  }, [status?.selected_date])

  return { status, isFetching, fetchMessage, error, triggerFetch, handleSelectDate }
}
