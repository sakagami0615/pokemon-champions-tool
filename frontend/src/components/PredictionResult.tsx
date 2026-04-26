// frontend/src/components/PredictionResult.tsx
import PatternCard from './PatternCard'
import type { PredictionResult, UsageEntry } from '../types'

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
