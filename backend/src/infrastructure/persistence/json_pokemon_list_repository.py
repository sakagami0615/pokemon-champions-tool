from pathlib import Path
from typing import Optional
from domain.entities.pokemon import PokemonList
from domain.repositories.pokemon_list_repository import IPokemonListRepository


class JsonPokemonListRepository(IPokemonListRepository):
    def __init__(self, data_dir: Path | str = Path(__file__).parent.parent.parent.parent / "data"):
        self._path = Path(data_dir) / "pokemon_list.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def get_pokemon_list(self) -> Optional[PokemonList]:
        if not self._path.exists():
            return None
        return PokemonList.model_validate_json(self._path.read_text(encoding="utf-8"))

    def save_pokemon_list(self, data: PokemonList) -> None:
        self._path.write_text(data.model_dump_json(indent=2), encoding="utf-8")
