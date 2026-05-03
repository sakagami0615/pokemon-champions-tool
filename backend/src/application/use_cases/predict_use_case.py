import re
import anthropic
from domain.entities.pokemon import UsageData
from domain.entities.party import PredictionResult, PredictionPattern

SYSTEM_PROMPT = """あなたはポケモンチャンピオンズの対戦分析AIです。
与えられた情報をもとに、相手プレイヤーが選出しそうなポケモン3体のパターンを3つ予想してください。

回答は必ず以下の形式で出力してください：
パターン1: ポケモン名A, ポケモン名B, ポケモン名C
パターン2: ポケモン名D, ポケモン名E, ポケモン名F
パターン3: ポケモン名G, ポケモン名H, ポケモン名I

可能性が高い順に並べてください。確率の数値は不要です。"""


class PredictUseCase:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def predict(
        self,
        opponent_party: list[str],
        my_party: list[str],
        usage_data: UsageData,
    ) -> PredictionResult:
        prompt = self._build_prompt(opponent_party, my_party, usage_data)
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return self._parse_response(response.content[0].text)

    def _build_prompt(
        self,
        opponent_party: list[str],
        my_party: list[str],
        usage_data: UsageData,
    ) -> str:
        usage_summary = []
        for entry in usage_data.pokemons:
            if entry.name in opponent_party:
                top_moves = ", ".join(f"{m.name}({m.rate}%)" for m in entry.moves[:3])
                top_items = ", ".join(f"{i.name}({i.rate}%)" for i in entry.items[:2])
                usage_summary.append(f"- {entry.name}: わざ[{top_moves}] 持ち物[{top_items}]")

        usage_text = "\n".join(usage_summary) if usage_summary else "使用率データなし"

        return f"""【相手パーティ（6体）】
{", ".join(opponent_party)}

【自分のパーティ（6体）】
{", ".join(my_party)}

【相手パーティの使用率データ】
{usage_text}

シングルバトル3体選出です。相手が選出しそうな3体のパターンを3つ予想してください。"""

    def _parse_response(self, text: str) -> PredictionResult:
        patterns = []
        for line in text.strip().splitlines():
            m = re.match(r"パターン\d+[:：]\s*(.+)", line)
            if m:
                names = [n.strip() for n in m.group(1).split(",")][:3]
                while len(names) < 3:
                    names.append("")
                patterns.append(PredictionPattern(pokemons=names))
        while len(patterns) < 3:
            patterns.append(PredictionPattern(pokemons=["", "", ""]))
        return PredictionResult(patterns=patterns[:3])
