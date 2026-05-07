from dataclasses import dataclass


@dataclass(frozen=True)
class PromptConfig:
    system_prompt: str
    user_prompt_template: str
