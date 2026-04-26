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
