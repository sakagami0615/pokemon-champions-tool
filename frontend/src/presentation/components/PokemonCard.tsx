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
