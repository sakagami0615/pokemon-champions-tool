from datetime import datetime
from domain.entities.pokemon import PokemonList
from domain.repositories.pokemon_list_repository import IPokemonListRepository
from infrastructure.external.pokemon_list_scraper import PokemonListScraper


class ScrapePokemonListUseCase:
    def __init__(self, scraper: PokemonListScraper, repository: IPokemonListRepository):
        self._scraper = scraper
        self._repository = repository

    def execute(self) -> None:
        pokemons, mega_pokemons = self._scraper.fetch_pokemon_list()
        data = PokemonList(
            collected_at=datetime.now().isoformat(),
            pokemons=pokemons,
            mega_pokemons=mega_pokemons,
        )
        self._repository.save_pokemon_list(data)
