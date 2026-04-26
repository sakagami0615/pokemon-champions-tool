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
        <span className="font-bold text-lg">🎮 ポケチャン支援ツール</span>
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
