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
            "pokemon": ["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "ゲンガー", "カビゴン"]
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
    mock_scraper = MagicMock()
    mock_scraper.fetch_pokemon_list.return_value = []
    mock_scraper.fetch_usage_ranking.return_value = []

    with patch("presentation.routers.data.GameWithScraper", return_value=mock_scraper):
        with patch("presentation.routers.data._usage_repo"):
            from presentation.routers.data import _do_fetch
            _do_fetch()

    mock_scraper.fetch_pokemon_list.assert_called_once()
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
    mock_scraper = MagicMock()
    mock_scraper.fetch_pokemon_list.side_effect = Exception("Network error")
    mock_scraper.fetch_usage_ranking.return_value = []

    with patch("presentation.routers.data.GameWithScraper", return_value=mock_scraper):
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
    assert isinstance(data["available_dates"], list)


@pytest.mark.asyncio
async def test_get_dates_returns_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/data/dates")
    assert resp.status_code == 200
    assert "dates" in resp.json()
    assert isinstance(resp.json()["dates"], list)


@pytest.mark.asyncio
async def test_select_date_sets_and_returns_date():
    with patch("presentation.routers.data._usage_repo") as mock_repo:
        mock_repo.get_usage_data_by_date.return_value = MagicMock()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/data/select-date", json={"date": "2026-04-27"})
    assert resp.status_code == 200
    assert resp.json()["selected_date"] == "2026-04-27"


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

    mock_scraper = MagicMock()
    mock_scraper.fetch_pokemon_list.return_value = []
    mock_scraper.fetch_usage_ranking.return_value = []

    with patch("presentation.routers.data.GameWithScraper", return_value=mock_scraper):
        with patch("presentation.routers.data._usage_repo"):
            from presentation.routers.data import _do_fetch
            _do_fetch()

    assert state.scraping_in_progress is False  # 完了後は False に戻る
