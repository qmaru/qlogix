import json
from functools import partial

import httpx
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.retries import AsyncTenacityTransport, RetryConfig, wait_retry_after
from tenacity import stop_after_attempt, wait_exponential

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

        retryConfig = RetryConfig(
            stop=stop_after_attempt(3),
            wait=wait_retry_after(fallback_strategy=wait_exponential(multiplier=1, min=1, max=10)),
            reraise=True,
        )

        http_client = httpx.AsyncClient(
            timeout=300,
            transport=AsyncTenacityTransport(config=retryConfig),
        )

        if cfg.provider == "openai":
            if not cfg.api_key:
                provider = OpenAIProvider(base_url=cfg.base_url, http_client=http_client)
            else:
                provider = OpenAIProvider(
                    base_url=cfg.base_url, api_key=cfg.api_key, http_client=http_client
                )

            model = OpenAIChatModel(cfg.model, provider=provider)

        elif cfg.provider == "google":
            provider = GoogleProvider(api_key=cfg.api_key, http_client=http_client)
            model = GoogleModel(cfg.model, provider=provider)

        else:
            raise ValueError(f"Unsupported provider: {cfg.provider}")

        self.agent = Agent(model, system_prompt=cfg.system_prompt)

    def run(self, events: list[SourceBaseContent]) -> AiContent:
        logs = json.dumps([event.model_dump() for event in events], ensure_ascii=False)
        prompt = f"Analyze the following logs:\n\n{logs}"
        try:
            result = log_external_call(
                logger, "ai.run_sync", partial(self.agent.run_sync, user_prompt=prompt)
            )

            return AiContent(result=result.output)

        except Exception as e:
            raise RuntimeError(f"AI request failed: {e}") from None
