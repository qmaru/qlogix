from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.openai import OpenAIProvider

from qlogix.analyze.base import Analyze
from qlogix.config import get_analyze_config


class AIAnalyze(Analyze):
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

        self.agent = Agent(model, system_prompt=cfg.system_prompt)

    def run(self, events: list[dict]) -> str:
        logs = "\n".join(event["message"] for event in events)
        result = self.agent.run_sync(
            f"""
Analyze the following logs:

{logs}
"""
        )

        return result.output
