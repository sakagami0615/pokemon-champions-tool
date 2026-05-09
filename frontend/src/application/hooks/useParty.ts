import { useState, useEffect, useCallback } from 'react'
import type { Party } from '../../domain/entities/party'
import {
  getParties,
  createParty,
  updateParty,
  deleteParty,
  setLastUsedParty,
} from '../../infrastructure/api/partyApi'

export interface UsePartyReturn {
  parties: Party[]
  selectedPartyId: string | null
  myParty: string[]
  selectParty: (party: Party) => Promise<void>
  clearSelectedParty: () => void
  createNewParty: (name: string, pokemon: string[]) => Promise<void>
  updateExistingParty: (id: string, name: string, pokemon: string[]) => Promise<void>
  removeParty: (id: string) => Promise<void>
  setMyParty: (pokemon: string[]) => void
  reload: () => Promise<void>
}

export function useParty(): UsePartyReturn {
  const [parties, setParties] = useState<Party[]>([])
  const [selectedPartyId, setSelectedPartyId] = useState<string | null>(null)
  const [myParty, setMyParty] = useState<string[]>(Array(6).fill(''))

  const reload = useCallback(async () => {
    try {
      const data = await getParties()
      setParties(data.parties)
      if (data.last_used_id) {
        const last = data.parties.find((p) => p.id === data.last_used_id)
        if (last) {
          setMyParty([...last.pokemons, ...Array(6).fill('')].slice(0, 6))
          setSelectedPartyId(last.id)
        }
      }
    } catch {
      // network errors are silently ignored; UI stays with last known state
    }
  }, [])

  useEffect(() => {
    reload()
  }, [reload])

  const selectParty = async (party: Party) => {
    setMyParty([...party.pokemons, ...Array(6).fill('')].slice(0, 6))
    setSelectedPartyId(party.id)
    await setLastUsedParty(party.id)
  }

  const clearSelectedParty = () => {
    setSelectedPartyId(null)
  }

  const createNewParty = async (name: string, pokemon: string[]) => {
    await createParty(name, pokemon)
    reload()
  }

  const updateExistingParty = async (id: string, name: string, pokemon: string[]) => {
    await updateParty(id, name, pokemon)
    reload()
  }

  const removeParty = async (id: string) => {
    await deleteParty(id)
    reload()
  }

  return {
    parties,
    selectedPartyId,
    myParty,
    selectParty,
    clearSelectedParty,
    createNewParty,
    updateExistingParty,
    removeParty,
    setMyParty,
    reload,
  }
}
