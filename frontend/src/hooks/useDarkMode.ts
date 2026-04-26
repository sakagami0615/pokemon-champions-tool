import { useEffect, useState } from 'react'

export function useDarkMode() {
  const [dark, setDark] = useState(() => localStorage.getItem('dark-mode') === 'true')

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('dark-mode', String(dark))
  }, [dark])

  return { dark, toggle: () => setDark(d => !d) }
}
