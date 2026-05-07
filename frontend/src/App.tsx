import { useState } from 'react'
import { Toaster } from 'sonner'
import { useDarkMode } from './presentation/hooks/useDarkMode'
import PredictionPage from './presentation/pages/PredictionPage'
import PartyPage from './presentation/pages/PartyPage'
import SettingsPage from './presentation/pages/SettingsPage'
import Header from './presentation/components/Header'

type Page = 'prediction' | 'party' | 'settings'

export default function App() {
  const { dark, toggle } = useDarkMode()
  const [page, setPage] = useState<Page>('prediction')

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <Toaster position="top-right" richColors />
      <Header dark={dark} onToggleDark={toggle} page={page} onChangePage={setPage} />
      <main className="p-4">
        {page === 'prediction' && <PredictionPage />}
        {page === 'party' && <PartyPage />}
        {page === 'settings' && <SettingsPage />}
      </main>
    </div>
  )
}
