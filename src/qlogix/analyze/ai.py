import json
from datetime import UTC, datetime

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.openai import OpenAIProvider

from qlogix.analyze.base import Analyze
from qlogix.config import get_analyze_config


class AIContent(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    analysis: str


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

    def run(self, events: list[dict]) -> AIContent:
        logs = json.dumps(events, ensure_ascii=False)
        result = self.agent.run_sync(user_prompt=(f"Analyze the following logs:\n\n{logs}"))

        return AIContent(analysis=result.output)
