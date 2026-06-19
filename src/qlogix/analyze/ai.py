import json
from collections import Counter
from functools import partial

from qlogix.analyze.base import Analyze, AnalyzeBaseContent
from qlogix.config import get_analyze_config
from qlogix.logutil import get_logger, log_external_call
from qlogix.source.base import SourceBaseContent

logger = get_logger(__name__)


class AiContent(AnalyzeBaseContent):
    pass


class AiAnalyze(Analyze[AiContent]):
    def __init__(self):
        import httpx
        from httpx import HTTPStatusError
        from pydantic_ai import Agent
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider
        from pydantic_ai.retries import AsyncTenacityTransport, RetryConfig, wait_retry_after
        from tenacity import retry_if_exception_type, stop_after_delay, wait_exponential

        cfg = get_analyze_config()

        retry_config = RetryConfig(
            retry=retry_if_exception_type(
                (
                    HTTPStatusError,
                    httpx.TimeoutException,
                    httpx.ConnectError,
                    httpx.ReadError,
                    httpx.RemoteProtocolError,
                    httpx.NetworkError,
                )
            ),
            wait=wait_retry_after(
                fallback_strategy=wait_exponential(multiplier=2, min=5, max=300),
                max_wait=1800,
            ),
            stop=stop_after_delay(3600),
            reraise=True,
        )

        limits = httpx.Limits(
            max_connections=20,
            max_keepalive_connections=10,
            keepalive_expiry=30,
        )

        timeout = httpx.Timeout(connect=10.0, read=120.0, write=30.0, pool=10.0)

        http_client = httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            transport=AsyncTenacityTransport(
                config=retry_config,
                validate_response=lambda r: r.raise_for_status(),
            ),
        )

        if not cfg.api_key:
            provider = OpenAIProvider(base_url=cfg.base_url, http_client=http_client)
        else:
            provider = OpenAIProvider(
                base_url=cfg.base_url, api_key=cfg.api_key, http_client=http_client
            )

        model = OpenAIChatModel(
            cfg.model, provider=provider, settings={"thinking": cfg.thinking_level}
        )

        self.agent = Agent(model, system_prompt=cfg.system_prompt)

    def run(self, events: list[SourceBaseContent]) -> AiContent:
        source_counts = Counter(event.source_name or "unknown" for event in events)
        metadata = {
            "total_events": len(events),
            "source_count": len(source_counts),
            "source_event_counts": dict(source_counts),
            "logs_are_filtered": True,
        }
        logs = json.dumps([event.model_dump() for event in events], ensure_ascii=False)
        prompt = (
            "Analyze the following logs.\n\n"
            f"Metadata:\n{json.dumps(metadata, ensure_ascii=False)}\n\n"
            f"Logs:\n{logs}"
        )
        try:
            result = log_external_call(
                logger, "ai.run_sync", partial(self.agent.run_sync, user_prompt=prompt)
            )

            return AiContent(result=result.output)

        except Exception as e:
            raise RuntimeError(f"AI request failed: {e}") from None
