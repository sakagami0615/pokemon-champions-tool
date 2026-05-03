from domain.entities.pokemon import PokemonInfo, BaseStats, RatedItem, EvSpread, UsageEntry, UsageData
from domain.entities.party import Party, PredictionPattern, PredictionResult


def test_pokemon_info():
    p = PokemonInfo(
        pokedex_id=6,
        name="リザードン",
        types=["ほのお", "ひこう"],
        base_stats=BaseStats(hp=78, attack=84, defense=78, sp_attack=109, sp_defense=85, speed=100),
        height_m=1.7,
        weight_kg=90.5,
        low_kick_power=100,
        abilities=["もうか", "サンパワー"],
        no_effect_types=["じめん"],
        quarter_damage_types=[],
        half_damage_types=["くさ", "かくとう", "むし", "ほのお", "フェアリー"],
        double_damage_types=["いわ", "でんき", "みず"],
        sprite_path="sprites/006.png",
    )
    assert p.name == "リザードン"
    assert p.no_effect_types == ["じめん"]
    assert p.double_damage_types == ["いわ", "でんき", "みず"]


def test_usage_entry():
    entry = UsageEntry(
        name="リザードン",
        moves=[RatedItem(name="かえんほうしゃ", rate=78), RatedItem(name="だいもんじ", rate=54)],
        items=[RatedItem(name="いのちのたま", rate=61)],
        abilities=[RatedItem(name="もうか", rate=82)],
        natures=[RatedItem(name="ひかえめ", rate=67)],
        teammates=[RatedItem(name="カメックス", rate=45)],
        evs=[EvSpread(spread={"H": 0, "A": 0, "B": 0, "C": 252, "D": 4, "S": 252}, rate=52)],
        ivs={"H": 31, "A": 0, "B": 31, "C": 31, "D": 31, "S": 31},
    )
    assert entry.moves[0].rate == 78
    assert entry.ivs["A"] == 0


def test_prediction_pattern():
    pattern = PredictionPattern(pokemons=["リザードン", "カメックス", "フシギバナ"])
    assert len(pattern.pokemons) == 3


def test_party():
    party = Party(id="p1", name="メインパーティ", pokemons=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "ゲンガー", "カビゴン"])
    assert len(party.pokemons) == 6
