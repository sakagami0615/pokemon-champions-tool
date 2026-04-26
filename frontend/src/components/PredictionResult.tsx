// frontend/src/components/PredictionResult.tsx  (stub - will be replaced in Task 11)
import type { PredictionResult, UsageEntry } from '../types'

interface Props {
  result: PredictionResult
  usageEntries?: UsageEntry[]
}

export default function PredictionResultView({ result }: Props) {
  return (
    <div className="space-y-4">
      <h2 className="font-bold text-lg">選出予想</h2>
      {result.patterns.map((pattern, i) => (
        <div key={i} className="border rounded-xl p-4 dark:border-gray-700">
          <div className="font-bold text-sm mb-2">パターン{i + 1}</div>
          <div className="flex gap-2">
            {pattern.pokemon.map((name, j) => (
              <span key={j} className="px-2 py-1 bg-indigo-100 dark:bg-indigo-900/30 rounded text-sm">{name}</span>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
