import { useState, useEffect } from 'react'
import { getPokemonNames } from '../../infrastructure/api/dataApi'

export interface UsePokemonDataReturn {
  pokemonNames: string[]
}

export function usePokemonData(): UsePokemonDataReturn {
  const [pokemonNames, setPokemonNames] = useState<string[]>([])

  useEffect(() => {
    getPokemonNames().then(setPokemonNames)
  }, [])

  return { pokemonNames }
}
