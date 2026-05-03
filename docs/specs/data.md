# データ設計

## 使用率データ（usage_rates/YYYY-MM-DD.json）

```json
{
  "collected_at": "2026-04-26T12:00:00",
  "season": 1,
  "regulation": "レギュレーションA",
  "source_updated_at": "2026-04-25",
  "pokemons": [
    {
      "name": "リザードン",
      "moves": [{"name": "かえんほうしゃ", "rate": 78}],
      "items": [{"name": "いのちのたま", "rate": 61}],
      "abilities": [{"name": "もうか", "rate": 82}],
      "natures": [{"name": "ひかえめ", "rate": 67}],
      "teammates": [],
      "evs": [
        {"spread": {"H": 0, "A": 0, "B": 0, "C": 252, "D": 4, "S": 252}, "rate": 52}
      ],
      "ivs": {"H": 31, "A": 0, "B": 31, "C": 31, "D": 31, "S": 31}
    }
  ]
}
```

`ivs` は GameWith に記載がある場合は実値、ない場合は `null`（表示時に競技標準値で補完）。

## 内定ポケモン一覧（pokemon_list.json）

```json
{
  "collected_at": "2026-04-26T12:00:00",
  "pokemons": [
    {
      "pokedex_id": 6,
      "name": "リザードン",
      "types": ["ほのお", "ひこう"],
      "base_stats": {
        "hp": 78, "attack": 84, "defense": 78,
        "sp_attack": 109, "sp_defense": 85, "speed": 100
      },
      "height_m": 1.7,
      "weight_kg": 90.5,
      "low_kick_power": 100,
      "abilities": ["もうか", "サンパワー"],
      "no_effect_types": ["じめん"],
      "quarter_damage_types": [],
      "half_damage_types": ["くさ", "かくとう", "むし", "ほのお", "フェアリー"],
      "double_damage_types": ["いわ", "でんき", "みず"],
      "sprite_path": "sprites/006.png"
    }
  ],
  "mega_pokemons": [
    {
      "pokedex_id": 6,
      "name": "メガリザードンX",
      "types": ["ほのお", "ドラゴン"],
      "base_stats": {
        "hp": 78, "attack": 130, "defense": 111,
        "sp_attack": 130, "sp_defense": 85, "speed": 100
      },
      "height_m": 1.7,
      "weight_kg": 110.5,
      "low_kick_power": 100,
      "abilities": ["かたいツメ"],
      "no_effect_types": ["じめん"],
      "quarter_damage_types": [],
      "half_damage_types": ["くさ", "かくとう", "むし", "ほのお", "フェアリー"],
      "double_damage_types": ["いわ", "ドラゴン"],
      "sprite_path": "sprites/006-mega-1.png"
    }
  ]
}
```

通常ポケモンは `pokemons`、メガシンカポケモンは `mega_pokemons` に格納する。タイプ相性は4区分に分類する（`no_effect_types`: x0無効、`quarter_damage_types`: x0.25、`half_damage_types`: x0.5、`double_damage_types`: x2弱点）。

## パーティデータ（parties.json）

```json
{
  "parties": [
    {
      "id": "party-1",
      "name": "メインパーティ",
      "pokemons": ["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "ゲンガー", "カビゴン"]
    }
  ]
}
```
