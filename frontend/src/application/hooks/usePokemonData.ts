import { useState, useEffect, useCallback } from 'react'
import { getPokemonNames, getPokemonList } from '../../infrastructure/api/dataApi'
import type { PokemonListEntry, BaseStats } from '../../domain/entities/pokemon'

export interface UsePokemonDataReturn {
  pokemonNames: string[]
  pokemonList: PokemonListEntry[]
  getBaseStats: (name: string) => BaseStats | null
}

export function usePokemonData(): UsePokemonDataReturn {
  const [pokemonNames, setPokemonNames] = useState<string[]>([])
  const [pokemonList, setPokemonList] = useState<PokemonListEntry[]>([])

  useEffect(() => {
    getPokemonNames().then(setPokemonNames).catch(() => {})
    getPokemonList()
      .then((res) => setPokemonList([...res.pokemons, ...res.mega_pokemons]))
      .catch(() => {})
  }, [])

  const getBaseStats = useCallback(
    (name: string): BaseStats | null =>
      pokemonList.find((p) => p.name === name)?.base_stats ?? null,
    [pokemonList],
  )

  return { pokemonNames, pokemonList, getBaseStats }
}
