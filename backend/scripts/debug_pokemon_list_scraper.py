#!/usr/bin/env python3
"""
pokemon_list_scraper の動作診断スクリプト。

Usage: docker compose run --rm backend python scripts/debug_pokemon_list_scraper.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import requests
from bs4 import BeautifulSoup
from infrastructure.external.constants import POKEMON_LIST_URL, HEADERS

resp = requests.get(POKEMON_LIST_URL, headers=HEADERS, timeout=30)
html = resp.text
soup = BeautifulSoup(html, "html.parser")

print(f"Status: {resp.status_code} / HTML size: {len(html):,} chars")
print()

# --- JSON スクリプトタグの内容を確認 ---
json_scripts = soup.select("script[type='application/ld+json'], script[type='application/json']")
print(f"[JSON スクリプトタグ: {len(json_scripts)} 件]")
for i, tag in enumerate(json_scripts):
    content = tag.string or ""
    try:
        parsed = json.loads(content)
        preview = json.dumps(parsed, ensure_ascii=False)[:300]
    except Exception:
        preview = content[:300]
    print(f"  [{i}] {preview}")
    print()

# --- window.* に埋め込まれた初期データを探す ---
print("[インライン script タグのキーワード検索]")
keywords = [
    "pokemon", "Pokemon", "ポケモン",
    "w-pokemon-list", "_name", "_no",
    "window.__", "initialState", "INITIAL_DATA",
]
for script_tag in soup.select("script:not([src])"):
    content = script_tag.string or ""
    matches = [kw for kw in keywords if kw in content]
    if matches:
        print(f"  マッチ: {matches}")
        print(f"  内容 (先頭300文字): {content[:300]}")
        print()

# --- 実際に存在する主要クラスをサンプリング ---
print("[HTML 内に存在するクラス名 (抜粋)]")
all_classes: set[str] = set()
for tag in soup.find_all(class_=True):
    for cls in tag.get("class", []):
        all_classes.add(cls)
pokemon_related = sorted(c for c in all_classes if "pokemon" in c.lower() or "pkm" in c.lower())
print(f"  pokemon/pkm 関連: {pokemon_related}")
print()

# --- XHR/fetch で呼ばれる API エンドポイントのヒントを探す ---
print("[script[src] 一覧 (外部JS)]")
for tag in soup.select("script[src]"):
    src = tag.get("src", "")
    if src:
        print(f"  {src}")
