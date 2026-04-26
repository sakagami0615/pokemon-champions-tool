import uuid
from fastapi import APIRouter, HTTPException
from services.data_manager import DataManager
from models.party import Party, PartiesData
from pydantic import BaseModel

router = APIRouter(prefix="/api/party", tags=["party"])
_manager = DataManager()


class PartyCreateRequest(BaseModel):
    name: str
    pokemon: list[str]


@router.get("")
def list_parties():
    return _manager.load_parties()


@router.post("")
def create_party(req: PartyCreateRequest):
    data = _manager.load_parties()
    party = Party(id=str(uuid.uuid4()), name=req.name, pokemon=req.pokemon)
    data.parties.append(party)
    _manager.save_parties(data)
    return party


@router.put("/{party_id}")
def update_party(party_id: str, req: PartyCreateRequest):
    data = _manager.load_parties()
    for i, p in enumerate(data.parties):
        if p.id == party_id:
            data.parties[i] = Party(id=party_id, name=req.name, pokemon=req.pokemon)
            _manager.save_parties(data)
            return data.parties[i]
    raise HTTPException(status_code=404, detail="Party not found")


@router.delete("/{party_id}")
def delete_party(party_id: str):
    data = _manager.load_parties()
    data.parties = [p for p in data.parties if p.id != party_id]
    _manager.save_parties(data)
    return {"ok": True}


@router.post("/last-used/{party_id}")
def set_last_used(party_id: str):
    data = _manager.load_parties()
    data.last_used_id = party_id
    _manager.save_parties(data)
    return {"ok": True}
