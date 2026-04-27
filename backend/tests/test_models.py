from domain.entities.pokemon import PokemonInfo, MegaEvolution, BaseStats, RatedItem, EvSpread, UsageEntry, UsageData
from domain.entities.party import Party, PredictionPattern, PredictionResult


def test_pokemon_info_with_mega():
    mega = MegaEvolution(
        name="メガリザードンX",
        types=["ほのお", "ドラゴン"],
        base_stats=BaseStats(hp=78, attack=130, defense=111, sp_attack=130, sp_defense=85, speed=100),
        abilities=["かたいツメ"],
        weaknesses=["じめん", "いわ", "ドラゴン"],
        resistances=["ほのお", "くさ"],
        sprite_path="sprites/006-mega-x.png",
    )
    p = PokemonInfo(
        pokedex_id=6,
        name="リザードン",
        types=["ほのお", "ひこう"],
        base_stats=BaseStats(hp=78, attack=84, defense=78, sp_attack=109, sp_defense=85, speed=100),
        height_m=1.7,
        weight_kg=90.5,
        low_kick_power=100,
        abilities=["もうか", "サンパワー"],
        weaknesses=["いわ", "みず", "でんき"],
        resistances=["くさ", "かくとう"],
        sprite_path="sprites/006.png",
        mega_evolution=mega,
    )
    assert p.name == "リザードン"
    assert p.mega_evolution.name == "メガリザードンX"


def test_pokemon_info_without_mega():
    p = PokemonInfo(
        pokedex_id=1,
        name="フシギダネ",
        types=["くさ", "どく"],
        base_stats=BaseStats(hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45),
        height_m=0.7,
        weight_kg=6.9,
        low_kick_power=20,
        abilities=["しんりょく"],
        weaknesses=["ほのお", "ひこう"],
        resistances=["くさ", "みず"],
        sprite_path="sprites/001.png",
        mega_evolution=None,
    )
    assert p.mega_evolution is None


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
    pattern = PredictionPattern(pokemon=["リザードン", "カメックス", "フシギバナ"])
    assert len(pattern.pokemon) == 3


def test_party():
    party = Party(id="p1", name="メインパーティ", pokemon=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "ゲンガー", "カビゴン"])
    assert len(party.pokemon) == 6
