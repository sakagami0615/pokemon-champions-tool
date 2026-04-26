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

    with patch("routers.recognition.recognizer") as mock_rec:
        mock_rec.recognize_from_bytes.return_value = mock_result
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/recognize",
                files={"file": ("test.jpg", b"fake-image-data", "image/jpeg")},
            )
    assert resp.status_code == 200
    assert len(resp.json()["names"]) == 6


@pytest.mark.asyncio
async def test_recognize_returns_400_on_invalid_image():
    """無効な画像バイト列を送った場合、APIが400を返すこと"""
    from services.image_recognition import InvalidImageError
    with patch("routers.recognition.recognizer") as mock_rec:
        mock_rec.recognize_from_bytes.side_effect = InvalidImageError("bad image")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/recognize",
                files={"file": ("bad.png", b"not an image", "image/png")},
            )
    assert resp.status_code == 400


def test_do_fetch_calls_scraper_methods():
    """_do_fetch が fetch_pokemon_list と fetch_usage_ranking を呼び出すこと"""
    mock_scraper = MagicMock()
    mock_scraper.fetch_pokemon_list.return_value = []
    mock_scraper.fetch_usage_ranking.return_value = []

    with patch("routers.data.GameWithScraper", return_value=mock_scraper):
        with patch("routers.data._manager"):
            from routers.data import _do_fetch
            _do_fetch()

    mock_scraper.fetch_pokemon_list.assert_called_once()
    mock_scraper.fetch_usage_ranking.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_data_endpoint_returns_started():
    """POST /api/data/fetch が {"status": "started"} を返すこと"""
    with patch("routers.data._do_fetch"):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/data/fetch")
    assert resp.status_code == 200
    assert resp.json()["status"] == "started"


def test_do_fetch_handles_scraper_init_exception():
    """GameWithScraper の初期化が失敗しても _do_fetch がクラッシュしないこと"""
    with patch("routers.data.GameWithScraper", side_effect=Exception("init error")):
        from routers.data import _do_fetch
        _do_fetch()  # 例外が伝播しないこと


def test_do_fetch_handles_scraper_exception():
    """fetch_pokemon_listが例外を投げても fetch_usage_ranking が呼ばれ、クラッシュしないこと"""
    mock_scraper = MagicMock()
    mock_scraper.fetch_pokemon_list.side_effect = Exception("Network error")
    mock_scraper.fetch_usage_ranking.return_value = []  # usage側は正常に動く

    with patch("routers.data.GameWithScraper", return_value=mock_scraper):
        from routers.data import _do_fetch
        _do_fetch()

    mock_scraper.fetch_usage_ranking.assert_called_once()
