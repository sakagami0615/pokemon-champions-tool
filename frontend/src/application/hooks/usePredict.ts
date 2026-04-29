import { useState } from 'react'
import type { PredictionResult } from '../../domain/entities/prediction'
import { predict } from '../../infrastructure/api/predictionApi'

export interface UsePredictReturn {
  result: PredictionResult | null
  loading: boolean
  error: string | null
  handlePredict: (opponentParty: string[], myParty: string[]) => Promise<void>
}

export function usePredict(): UsePredictReturn {
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handlePredict = async (opponentParty: string[], myParty: string[]) => {
    const opponent = opponentParty.filter(Boolean)
    const my = myParty.filter(Boolean)
    setError(null)
    if (opponent.length < 3) return
    if (my.length === 0) return
    setLoading(true)
    try {
      const res = await predict(opponent, my)
      setResult(res)
    } catch (e) {
      setError(e instanceof Error ? e.message : '予期しないエラーが発生しました')
    } finally {
      setLoading(false)
    }
  }

  return { result, loading, error, handlePredict }
}
