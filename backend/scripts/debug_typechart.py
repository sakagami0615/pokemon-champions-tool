#!/usr/bin/env python3
"""
タイプ相性の重複原因を調査するスクリプト。
フシギバナの詳細ページを取得してタイプ相性HTMLを確認する。

Usage: docker compose run --rm backend python scripts/debug_typechart.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import requests
from bs4 import BeautifulSoup
from infrastructure.external.constants import HEADERS

DETAIL_URL = "https://gamewith.jp/pokemon-champions/553138"  # フシギバナ

resp = requests.get(DETAIL_URL, headers=HEADERS, timeout=30)
soup = BeautifulSoup(resp.text, "html.parser")

# ol._pokechamp_pkm_typechart の出現回数
ols = soup.select("ol._pokechamp_pkm_typechart")
print(f"ol._pokechamp_pkm_typechart の出現回数: {len(ols)}")
print()

# 各 ol の li 一覧
for ol_idx, ol in enumerate(ols):
    print(f"=== ol[{ol_idx}] ===")
    for li in ol.select("li[data-attr]"):
        attr = li.get("data-attr")
        imgs = li.select("img[alt]")
        alts = [img["alt"] for img in imgs]
        print(f"  data-attr={attr!r}: {alts}")
    print()

# li 内の img 構造を詳細確認 (最初の li のみ)
print("=== 最初の li の prettify ===")
first_li = soup.select_one("ol._pokechamp_pkm_typechart li[data-attr]")
if first_li:
    print(first_li.prettify()[:1500])
