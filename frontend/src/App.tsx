import { useState } from 'react'
import { useDarkMode } from './hooks/useDarkMode'
import PredictionPage from './pages/PredictionPage'
import PartyPage from './pages/PartyPage'
import Header from './components/Header'

type Page = 'prediction' | 'party'

export default function App() {
  const { dark, toggle } = useDarkMode()
  const [page, setPage] = useState<Page>('prediction')

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <Header dark={dark} onToggleDark={toggle} page={page} onChangePage={setPage} />
      <main className="p-4">
        {page === 'prediction' ? <PredictionPage /> : <PartyPage />}
      </main>
    </div>
  )
}
