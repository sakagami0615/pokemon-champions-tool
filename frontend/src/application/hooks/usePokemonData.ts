import { useState, useEffect, useCallback, useMemo } from 'react'
import { getPokemonList } from '../../infrastructure/api/dataApi'
import type { PokemonListEntry, BaseStats } from '../../domain/entities/pokemon'

export interface UsePokemonDataReturn {
  pokemonNames: string[]
  pokemonList: PokemonListEntry[]
  getBaseStats: (name: string) => BaseStats | null
}

export function usePokemonData(): UsePokemonDataReturn {
  const [pokemonList, setPokemonList] = useState<PokemonListEntry[]>([])

  useEffect(() => {
    getPokemonList()
      .then((res) => setPokemonList([...res.pokemons, ...res.mega_pokemons]))
      .catch(() => {})
  }, [])

  const pokemonNames = useMemo(() => pokemonList.map((p) => p.name), [pokemonList])

  const getBaseStats = useCallback(
    (name: string): BaseStats | null =>
      pokemonList.find((p) => p.name === name)?.base_stats ?? null,
    [pokemonList],
  )

  return { pokemonNames, pokemonList, getBaseStats }
}
