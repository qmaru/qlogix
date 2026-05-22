import json

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.openai import OpenAIProvider

from qlogix.analyze.base import Analyze, AnalyzeBaseContent
from qlogix.config import get_analyze_config
from qlogix.source.base import SourceBaseContent


class AIContent(AnalyzeBaseContent):
    pass


class AIAnalyze(Analyze[AIContent]):
    def __init__(self):
        cfg = get_analyze_config()

        if cfg.provider == "openai":
            if not cfg.api_key:
                provider = OpenAIProvider(base_url=cfg.base_url)
            else:
                provider = OpenAIProvider(base_url=cfg.base_url, api_key=cfg.api_key)

            model = OpenAIChatModel(cfg.model, provider=provider)

        elif cfg.provider == "google":
            provider = GoogleProvider(api_key=cfg.api_key)
            model = GoogleModel(cfg.model, provider=provider)

        else:
            raise ValueError(f"Unsupported provider: {cfg.provider}")

        self.agent = Agent(model, system_prompt=cfg.system_prompt)

    def run(self, events: list[SourceBaseContent]) -> AIContent:
        logs = json.dumps([event.model_dump() for event in events], ensure_ascii=False)
        result = self.agent.run_sync(user_prompt=(f"Analyze the following logs:\n\n{logs}"))

        return AIContent(result=result.output)
