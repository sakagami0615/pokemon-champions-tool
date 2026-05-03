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
async def test_recognize_returns_six_names():
    mock_result = MagicMock()
    mock_result.names = ["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "ゲンガー", "カビゴン"]
    mock_result.confidences = [0.9] * 6

    with patch("presentation.routers.recognition.recognizer") as mock_rec:
        mock_rec.recognize.return_value = mock_result
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/recognize",
                files={"file": ("test.jpg", b"fake-image-data", "image/jpeg")},
            )
    assert resp.status_code == 200
    assert len(resp.json()["names"]) == 6


@pytest.mark.asyncio
async def test_recognize_returns_400_on_invalid_image():
    from domain.repositories.image_recognizer import InvalidImageError
    with patch("presentation.routers.recognition.recognizer") as mock_rec:
        mock_rec.recognize.side_effect = InvalidImageError("bad image")
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
        mock_usage = MagicMock()
        mock_repo.get_usage_data_by_date.return_value = mock_usage
        mock_repo.get_usage_data.return_value = mock_usage

        with patch("presentation.routers.prediction.PredictUseCase") as mock_uc:
            mock_uc.return_value.predict.return_value = {"patterns": []}
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                    resp = await client.post("/api/predict", json={
                        "opponent_party": ["リザードン"] * 6,
                        "my_party": ["カメックス"] * 6,
                    })

        mock_repo.get_usage_data_by_date.assert_called_once_with("2026-04-27")
        mock_repo.get_usage_data.assert_not_called()


@pytest.mark.asyncio
async def test_predict_uses_latest_when_no_date_selected():
    import application.state.scraping_state as state
    state.selected_date = None

    with patch("presentation.routers.prediction._usage_repo") as mock_repo:
        mock_usage = MagicMock()
        mock_repo.get_usage_data.return_value = mock_usage

        with patch("presentation.routers.prediction.PredictUseCase") as mock_uc:
            mock_uc.return_value.predict.return_value = {"patterns": []}
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                    resp = await client.post("/api/predict", json={
                        "opponent_party": ["リザードン"] * 6,
                        "my_party": ["カメックス"] * 6,
                    })

        mock_repo.get_usage_data.assert_called_once()
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_data_status_dates_detail_structure():
    from domain.entities.pokemon import UsageData, UsageEntry, PokemonList, PokemonInfo, BaseStats
    import presentation.routers.data as rd

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
                sprite_path="sprites/025.png"
            )
        ],
        mega_pokemons=[]
    )
    rd._usage_repo.save_usage_data(usage)
    rd._pokemon_list_repo.save_pokemon_list(plist)

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
