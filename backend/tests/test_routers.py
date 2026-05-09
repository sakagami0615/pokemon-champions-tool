import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
from main import app


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_parties_empty():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/party")
    assert resp.status_code == 200
    assert resp.json()["parties"] == []


@pytest.mark.asyncio
async def test_create_party():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/party", json={
            "name": "テストパーティ",
            "pokemons": ["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "ゲンガー", "カビゴン"]
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "テストパーティ"
    assert "id" in data


@pytest.mark.asyncio
async def test_recognize_returns_both_parties():
    my_result = MagicMock()
    my_result.names = ["リザードン", "ゲッコウガ", "ルチャブル", "ゾロアーク", "ブラッキー", "ギルガルド"]
    my_result.confidences = [0.9] * 6
    opp_result = MagicMock()
    opp_result.names = ["ガブリアス", "カイリュー", "ミミッキュ", "サーナイト", "ドリュウズ", "ハッサム"]
    opp_result.confidences = [0.85] * 6
    selection_result = MagicMock()
    selection_result.my_party = my_result
    selection_result.opponent_party = opp_result

    with patch("presentation.routers.recognition.recognizer") as mock_rec:
        mock_rec.recognize_selection.return_value = selection_result
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/recognize",
                files={"file": ("test.jpg", b"fake-image-data", "image/jpeg")},
            )
    assert resp.status_code == 200
    data = resp.json()
    assert "my_party" in data
    assert "opponent_party" in data
    assert len(data["my_party"]["names"]) == 6
    assert len(data["opponent_party"]["names"]) == 6
    assert len(data["my_party"]["confidences"]) == 6
    assert len(data["opponent_party"]["confidences"]) == 6


@pytest.mark.asyncio
async def test_recognize_returns_400_on_invalid_image():
    from domain.repositories.image_recognizer import InvalidImageError
    with patch("presentation.routers.recognition.recognizer") as mock_rec:
        mock_rec.recognize_selection.side_effect = InvalidImageError("bad image")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/recognize",
                files={"file": ("bad.png", b"not an image", "image/png")},
            )
    assert resp.status_code == 400


def test_do_fetch_calls_scraper_methods():
    with patch("presentation.routers.data.ScrapePokemonListUseCase") as mock_use_case_cls:
        mock_use_case = MagicMock()
        mock_use_case_cls.return_value = mock_use_case
        with patch("presentation.routers.data.GameWithScraper") as mock_gw_cls:
            mock_scraper = MagicMock()
            mock_scraper.fetch_usage_ranking.return_value = []
            mock_gw_cls.return_value = mock_scraper
            with patch("presentation.routers.data._usage_repo"):
                from presentation.routers.data import _do_fetch
                _do_fetch()

    mock_use_case.execute.assert_called_once()
    mock_scraper.fetch_usage_ranking.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_data_endpoint_returns_started():
    with patch("presentation.routers.data._do_fetch"):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/data/fetch")
    assert resp.status_code == 200
    assert resp.json()["status"] == "started"


def test_do_fetch_handles_scraper_init_exception():
    with patch("presentation.routers.data.ScrapePokemonListUseCase") as mock_uc_cls:
        mock_uc_cls.return_value = MagicMock()
        with patch("presentation.routers.data.GameWithScraper", side_effect=Exception("init error")):
            from presentation.routers.data import _do_fetch
            _do_fetch()


def test_do_fetch_handles_scraper_exception():
    with patch("presentation.routers.data.ScrapePokemonListUseCase") as mock_use_case_cls:
        mock_use_case = MagicMock()
        mock_use_case.execute.side_effect = Exception("Scrape error")
        mock_use_case_cls.return_value = mock_use_case
        with patch("presentation.routers.data.GameWithScraper") as mock_gw_cls:
            mock_scraper = MagicMock()
            mock_scraper.fetch_usage_ranking.return_value = []
            mock_gw_cls.return_value = mock_scraper
            with patch("presentation.routers.data._usage_repo"):
                from presentation.routers.data import _do_fetch
                _do_fetch()

    mock_scraper.fetch_usage_ranking.assert_called_once()


@pytest.mark.asyncio
async def test_data_status_includes_scraping_fields():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/data/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "scraping_in_progress" in data
    assert "selected_date" in data
    assert "available_dates" in data
    assert "dates_detail" in data
    assert isinstance(data["available_dates"], list)
    assert isinstance(data["dates_detail"], list)


@pytest.mark.asyncio
async def test_get_dates_returns_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/data/dates")
    assert resp.status_code == 200
    assert "dates" in resp.json()
    assert isinstance(resp.json()["dates"], list)


@pytest.mark.asyncio
async def test_select_date_sets_and_returns_date():
    import application.state.scraping_state as state
    try:
        with patch("presentation.routers.data._usage_repo") as mock_repo:
            mock_repo.get_usage_data_by_date.return_value = MagicMock()
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post("/api/data/select-date", json={"date": "2026-04-27"})
        assert resp.status_code == 200
        assert resp.json()["selected_date"] == "2026-04-27"
    finally:
        state.selected_date = None


@pytest.mark.asyncio
async def test_select_date_returns_404_for_missing_date():
    with patch("presentation.routers.data._usage_repo") as mock_repo:
        mock_repo.get_usage_data_by_date.return_value = None
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/data/select-date", json={"date": "2099-01-01"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_select_date_validates_format():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/data/select-date", json={"date": "not-a-date"})
    assert resp.status_code == 422


def test_do_fetch_sets_scraping_flag():
    import application.state.scraping_state as state

    with patch("presentation.routers.data.ScrapePokemonListUseCase") as mock_use_case_cls:
        mock_use_case_cls.return_value = MagicMock()
        with patch("presentation.routers.data.GameWithScraper") as mock_gw_cls:
            mock_scraper = MagicMock()
            mock_scraper.fetch_usage_ranking.return_value = []
            mock_gw_cls.return_value = mock_scraper
            with patch("presentation.routers.data._usage_repo"):
                from presentation.routers.data import _do_fetch
                _do_fetch()

    assert state.scraping_in_progress is False


@pytest.mark.asyncio
async def test_predict_uses_selected_date(monkeypatch):
    import application.state.scraping_state as state
    monkeypatch.setattr(state, "selected_date", "2026-04-27")

    with patch("presentation.routers.prediction._usage_repo") as mock_repo:
        mock_repo.get_usage_data_by_date.return_value = MagicMock()
        with patch("presentation.routers.prediction._llm_config_repo") as mock_cfg:
            mock_cfg.get_config.return_value = MagicMock(
                selected_provider="anthropic",
                providers={"anthropic": MagicMock(model="claude-sonnet-4-6")},
            )
            with patch("presentation.routers.prediction.LiteLLMClient"):
                with patch("presentation.routers.prediction.PredictUseCase") as mock_uc:
                    mock_uc.return_value.predict.return_value = {"patterns": []}
                    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                        await client.post("/api/predict", json={
                            "opponent_party": ["リザードン"] * 6,
                            "my_party": ["カメックス"] * 6,
                        })

    mock_repo.get_usage_data_by_date.assert_called_once_with("2026-04-27")
    mock_repo.get_usage_data.assert_not_called()


@pytest.mark.asyncio
async def test_predict_uses_latest_when_no_date_selected(monkeypatch):
    import application.state.scraping_state as state
    monkeypatch.setattr(state, "selected_date", None)

    with patch("presentation.routers.prediction._usage_repo") as mock_repo:
        mock_repo.get_usage_data.return_value = MagicMock()
        with patch("presentation.routers.prediction._llm_config_repo") as mock_cfg:
            mock_cfg.get_config.return_value = MagicMock(
                selected_provider="anthropic",
                providers={"anthropic": MagicMock(model="claude-sonnet-4-6")},
            )
            with patch("presentation.routers.prediction.LiteLLMClient"):
                with patch("presentation.routers.prediction.PredictUseCase") as mock_uc:
                    mock_uc.return_value.predict.return_value = {"patterns": []}
                    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                        resp = await client.post("/api/predict", json={
                            "opponent_party": ["リザードン"] * 6,
                            "my_party": ["カメックス"] * 6,
                        })

    mock_repo.get_usage_data.assert_called_once()
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_predict_returns_400_when_model_not_set():
    import application.state.scraping_state as state
    state.selected_date = None

    with patch("presentation.routers.prediction._usage_repo") as mock_repo:
        mock_repo.get_usage_data.return_value = MagicMock()
        with patch("presentation.routers.prediction._llm_config_repo") as mock_cfg:
            mock_cfg.get_config.return_value = MagicMock(
                selected_provider="ollama",
                providers={"ollama": MagicMock(model=None)},
            )
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post("/api/predict", json={
                    "opponent_party": ["リザードン"] * 6,
                    "my_party": ["カメックス"] * 6,
                })

    assert resp.status_code == 400
    assert "モデルが設定されていません" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_predict_returns_400_when_api_key_not_set(monkeypatch):
    import application.state.scraping_state as state
    monkeypatch.setattr(state, "selected_date", None)

    with patch("presentation.routers.prediction._usage_repo") as mock_repo:
        mock_repo.get_usage_data.return_value = MagicMock()
        with patch("presentation.routers.prediction._llm_config_repo") as mock_cfg:
            mock_cfg.get_config.return_value = MagicMock(
                selected_provider="anthropic",
                providers={"anthropic": MagicMock(model="claude-sonnet-4-6", api_key=None)},
            )
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post("/api/predict", json={
                    "opponent_party": ["リザードン"] * 6,
                    "my_party": ["カメックス"] * 6,
                })

    assert resp.status_code == 400
    assert "APIキーが設定されていません" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_data_status_dates_detail_structure(tmp_path):
    from domain.entities.pokemon import UsageData, UsageEntry, PokemonList, PokemonInfo, BaseStats
    from infrastructure.persistence.json_usage_repository import JsonUsageRepository
    from infrastructure.persistence.json_pokemon_list_repository import JsonPokemonListRepository

    entry = UsageEntry(
        name="ピカチュウ",
        moves=[], items=[], abilities=[], natures=[], teammates=[], evs=[]
    )
    usage = UsageData(
        collected_at="2026-04-29T12:00:00",
        season=0, regulation="", source_updated_at="2026-04-29T12:00:00",
        pokemons=[entry]
    )
    plist = PokemonList(
        collected_at="2026-04-29T12:00:00",
        pokemons=[
            PokemonInfo(
                pokedex_id=25, name="ピカチュウ", types=["でんき"],
                base_stats=BaseStats(hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90),
                height_m=0.4, weight_kg=6.0, low_kick_power=20,
                abilities=["せいでんき"],
                no_effect_types=[], quarter_damage_types=[], half_damage_types=["でんき"], double_damage_types=["じめん"],
                quad_damage_types=[],
                sprite_path="sprites/025.png"
            )
        ],
        mega_pokemons=[]
    )
    tmp_usage_repo = JsonUsageRepository(data_dir=tmp_path)
    tmp_pokemon_list_repo = JsonPokemonListRepository(data_dir=tmp_path)
    tmp_usage_repo.save_usage_data(usage)
    tmp_pokemon_list_repo.save_pokemon_list(plist)

    with patch("presentation.routers.data._usage_repo", tmp_usage_repo), \
         patch("presentation.routers.data._pokemon_list_repo", tmp_pokemon_list_repo):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/data/status")

    assert resp.status_code == 200
    data = resp.json()
    assert "dates_detail" in data
    assert len(data["dates_detail"]) == 1
    detail = data["dates_detail"][0]
    assert detail["date"] == "2026-04-29"
    assert detail["pokemon_count"] == 1
    assert detail["top_pokemon"] == [{"name": "ピカチュウ"}]


@pytest.mark.asyncio
async def test_get_pokemon_list_empty():
    with patch("presentation.routers.data._pokemon_list_repo") as mock_repo:
        mock_repo.get_pokemon_list.return_value = None
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/data/pokemon-list")
    assert resp.status_code == 200
    data = resp.json()
    assert data["pokemons"] == []
    assert data["mega_pokemons"] == []


@pytest.mark.asyncio
async def test_get_pokemon_list_returns_data():
    from domain.entities.pokemon import PokemonList, PokemonInfo, BaseStats as BS
    mock_pokemon = PokemonInfo(
        pokedex_id=6,
        name="リザードン",
        types=["ほのお", "ひこう"],
        base_stats=BS(hp=78, attack=84, defense=78, sp_attack=109, sp_defense=85, speed=100),
        height_m=1.7,
        weight_kg=90.5,
        low_kick_power=100,
        abilities=["もうか"],
        no_effect_types=["じめん"],
        quarter_damage_types=[],
        half_damage_types=[],
        double_damage_types=["いわ"],
        quad_damage_types=[],
        sprite_path="sprites/006.png",
    )
    mock_list = PokemonList(
        collected_at="2026-05-01T00:00:00",
        pokemons=[mock_pokemon],
        mega_pokemons=[],
    )
    with patch("presentation.routers.data._pokemon_list_repo") as mock_repo:
        mock_repo.get_pokemon_list.return_value = mock_list
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/data/pokemon-list")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["pokemons"]) == 1
    assert data["pokemons"][0]["name"] == "リザードン"
    assert data["pokemons"][0]["base_stats"]["hp"] == 78
    assert data["mega_pokemons"] == []


@pytest.mark.asyncio
async def test_get_llm_config_returns_default():
    from domain.entities.llm_config import LLMConfig, ProviderSettings
    default_config = LLMConfig(
        selected_provider="openai",
        providers={
            "anthropic": ProviderSettings(model="claude-sonnet-4-6", base_url=None, api_key=None),
            "openai": ProviderSettings(model="gpt-4o", base_url=None, api_key=None),
            "google": ProviderSettings(model="gemini-2.0-flash", base_url=None, api_key=None),
            "ollama": ProviderSettings(model=None, base_url="http://host.docker.internal:11434", api_key=None),
        },
    )
    with patch("presentation.routers.llm_config._llm_config_repo") as mock_repo:
        mock_repo.get_config.return_value = default_config
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/llm-config")
    assert resp.status_code == 200
    data = resp.json()
    assert data["selected_provider"] == "openai"
    assert "providers" in data
    assert "anthropic" in data["providers"]
    assert "openai" in data["providers"]
    assert "google" in data["providers"]
    assert "ollama" in data["providers"]


@pytest.mark.asyncio
async def test_get_llm_config_returns_actual_api_key():
    from domain.entities.llm_config import LLMConfig, ProviderSettings
    config_with_key = LLMConfig(
        selected_provider="anthropic",
        providers={
            "anthropic": ProviderSettings(model="claude-sonnet-4-6", base_url=None, api_key="sk-real-key"),
            "openai": ProviderSettings(model="gpt-4o", base_url=None, api_key=None),
            "google": ProviderSettings(model="gemini-2.0-flash", base_url=None, api_key=None),
            "ollama": ProviderSettings(model=None, base_url="http://host.docker.internal:11434", api_key=None),
        },
    )
    with patch("presentation.routers.llm_config._llm_config_repo") as mock_repo:
        mock_repo.get_config.return_value = config_with_key
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/llm-config")
    assert resp.status_code == 200
    assert resp.json()["providers"]["anthropic"]["api_key"] == "sk-real-key"
    assert resp.json()["providers"]["openai"]["api_key"] is None


@pytest.mark.asyncio
async def test_put_llm_config_saves_api_key():
    payload = {
        "selected_provider": "anthropic",
        "providers": {
            "anthropic": {"model": "claude-sonnet-4-6", "base_url": None, "api_key": "sk-new-key"},
            "openai": {"model": "gpt-4o", "base_url": None, "api_key": None},
            "google": {"model": "gemini-2.0-flash", "base_url": None, "api_key": None},
            "ollama": {"model": None, "base_url": "http://host.docker.internal:11434", "api_key": None},
        },
    }
    with patch("presentation.routers.llm_config._llm_config_repo") as mock_repo:
        mock_repo.save_config = MagicMock()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.put("/api/llm-config", json=payload)
    assert resp.status_code == 200
    saved = mock_repo.save_config.call_args[0][0]
    assert saved.providers["anthropic"].api_key == "sk-new-key"


@pytest.mark.asyncio
async def test_put_llm_config_saves_and_returns():
    payload = {
        "selected_provider": "openai",
        "providers": {
            "anthropic": {"model": "claude-sonnet-4-6", "base_url": None, "api_key": None},
            "openai": {"model": "gpt-4o", "base_url": None, "api_key": None},
            "google": {"model": "gemini-2.0-flash", "base_url": None, "api_key": None},
            "ollama": {"model": None, "base_url": "http://host.docker.internal:11434", "api_key": None},
        },
    }
    with patch("presentation.routers.llm_config._llm_config_repo") as mock_repo:
        mock_repo.save_config = MagicMock()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.put("/api/llm-config", json=payload)
    assert resp.status_code == 200
    assert resp.json()["selected_provider"] == "openai"
    mock_repo.save_config.assert_called_once()


@pytest.mark.asyncio
async def test_get_ollama_models_returns_model_names():
    with patch("presentation.routers.llm_config.requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "models": [{"name": "llama3.2"}, {"name": "mistral"}]
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/ollama-models?base_url=http://localhost:11434")
    assert resp.status_code == 200
    assert resp.json()["models"] == ["llama3.2", "mistral"]


@pytest.mark.asyncio
async def test_get_ollama_models_returns_503_on_connection_error():
    with patch(
        "presentation.routers.llm_config.requests.get",
        side_effect=Exception("connection refused"),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/ollama-models?base_url=http://localhost:11434")
    assert resp.status_code == 503
