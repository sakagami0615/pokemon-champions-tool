import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from domain.entities.party import Party, PartiesData
from infrastructure.persistence.json_party_repository import JsonPartyRepository

router = APIRouter(prefix="/api/party", tags=["party"])
_repo = JsonPartyRepository()


class PartyCreateRequest(BaseModel):
    name: str
    pokemons: list[str]


@router.get("")
def list_parties() -> PartiesData:
    return _repo.get_all()


@router.post("")
def create_party(req: PartyCreateRequest) -> Party:
    data = _repo.get_all()
    party = Party(id=str(uuid.uuid4()), name=req.name, pokemons=req.pokemons)
    updated = PartiesData(parties=[*data.parties, party], last_used_id=data.last_used_id)
    _repo.save(updated)
    return party


@router.put("/{party_id}")
def update_party(party_id: str, req: PartyCreateRequest) -> Party:
    data = _repo.get_all()
    parties = data.parties
    for i, p in enumerate(parties):
        if p.id == party_id:
            updated_party = Party(id=party_id, name=req.name, pokemons=req.pokemons)
            new_parties = [*parties[:i], updated_party, *parties[i + 1:]]
            _repo.save(PartiesData(parties=new_parties, last_used_id=data.last_used_id))
            return updated_party
    raise HTTPException(status_code=404, detail="Party not found")


@router.delete("/{party_id}")
def delete_party(party_id: str):
    data = _repo.get_all()
    new_parties = [p for p in data.parties if p.id != party_id]
    _repo.save(PartiesData(parties=new_parties, last_used_id=data.last_used_id))
    return {"ok": True}


@router.post("/last-used/{party_id}")
def set_last_used(party_id: str):
    data = _repo.get_all()
    _repo.save(PartiesData(parties=data.parties, last_used_id=party_id))
    return {"ok": True}
