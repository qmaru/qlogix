import json

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.openai import OpenAIProvider

from qlogix.analyze.base import Analyze, AnalyzeBaseContent
from qlogix.config import get_analyze_config
from qlogix.logutil import get_logger, log_external_call
from qlogix.source.base import SourceBaseContent

logger = get_logger(__name__)


class AiContent(AnalyzeBaseContent):
    pass


class AiAnalyze(Analyze[AiContent]):
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

    def run(self, events: list[SourceBaseContent]) -> AiContent:
        logs = json.dumps([event.model_dump() for event in events], ensure_ascii=False)
        result = log_external_call(
            logger,
            "ai.run_sync",
            lambda: self.agent.run_sync(user_prompt=(f"Analyze the following logs:\n\n{logs}")),
            analyzer=self.__class__.__name__,
            event_count=len(events),
        )

        return AiContent(result=result.output)
