import re
from domain.entities.pokemon import UsageData
from domain.entities.party import PredictionResult, PredictionPattern
from domain.entities.prompt_config import PromptConfig
from domain.repositories.llm_client import ILLMClient
from domain.repositories.prompt_config_repository import IPromptConfigRepository


class PredictUseCase:
    def __init__(self, llm_client: ILLMClient, prompt_config_repo: IPromptConfigRepository) -> None:
        self._client = llm_client
        self._prompt_config_repo = prompt_config_repo

    def predict(
        self,
        opponent_party: list[str],
        my_party: list[str],
        usage_data: UsageData,
    ) -> PredictionResult:
        config = self._prompt_config_repo.get_config()
        prompt = self._build_prompt(opponent_party, my_party, usage_data, config)
        text = self._client.generate(config.system_prompt, prompt)
        return self._parse_response(text)

    def _build_prompt(
        self,
        opponent_party: list[str],
        my_party: list[str],
        usage_data: UsageData,
        prompt_config: PromptConfig,
    ) -> str:
        usage_summary = []
        for entry in usage_data.pokemons:
            if entry.name in opponent_party:
                top_moves = ", ".join(f"{m.name}({m.rate}%)" for m in entry.moves[:3])
                top_items = ", ".join(f"{i.name}({i.rate}%)" for i in entry.items[:2])
                usage_summary.append(f"- {entry.name}: わざ[{top_moves}] 持ち物[{top_items}]")

        usage_text = "\n".join(usage_summary) if usage_summary else "使用率データなし"

        return prompt_config.user_prompt_template.format(
            opponent_party=", ".join(opponent_party),
            my_party=", ".join(my_party),
            usage_text=usage_text,
        )

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
