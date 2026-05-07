interface Props {
  progress: number
  step: string
}

export default function ScrapeProgressBar({ progress, step }: Props) {
  return (
    <div className="space-y-1">
      {step && (
        <p className="text-sm text-gray-600 dark:text-gray-400">{step}</p>
      )}
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
        <div
          className="bg-indigo-600 h-2.5 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
      <p className="text-sm text-gray-500">{progress}%</p>
    </div>
  )
}
