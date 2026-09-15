import json
import threading
from collections import Counter
from time import perf_counter

from qlogix.analyze.base import Analyze, AnalyzeBaseContent
from qlogix.config import get_analyze_config
from qlogix.logutil import get_logger
from qlogix.source.base import SourceBaseContent

logger = get_logger(__name__)


class AiContent(AnalyzeBaseContent):
    pass


class AiAnalyze(Analyze[AiContent]):
    def __init__(self):
        from openai import OpenAI

        cfg = get_analyze_config()
        self.client = OpenAI(
            api_key=cfg.api_key or "",
            base_url=cfg.base_url,
            timeout=cfg.timeout,
            max_retries=cfg.max_retries,
        )
        self.model_name = cfg.model
        self.api_type = cfg.api_type
        self.system_prompt = cfg.system_prompt

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
        started_at = perf_counter()
        heartbeat_stop = threading.Event()

        def log_progress() -> None:
            while not heartbeat_stop.wait(30):
                logger.info(
                    "ai analysis still running model=%s elapsed_seconds=%.1f",
                    self.model_name,
                    perf_counter() - started_at,
                )

        heartbeat = threading.Thread(target=log_progress, daemon=True)
        heartbeat.start()
        logger.info(
            "ai analysis started model=%s events=%d sources=%d",
            self.model_name,
            len(events),
            len(source_counts),
        )
        try:
            if self.api_type == "responses":
                response = self.client.responses.create(
                    model=self.model_name,
                    instructions=self.system_prompt,
                    input=prompt,
                )
                content = response.output_text
            else:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                )
                content = response.choices[0].message.content or ""

            logger.info(
                "ai analysis completed model=%s elapsed_seconds=%.1f",
                self.model_name,
                perf_counter() - started_at,
            )

            return AiContent(result=content)

        except Exception as e:  # noqa: BLE001
            elapsed_seconds = perf_counter() - started_at
            logger.error(
                "ai analysis failed model=%s elapsed_seconds=%.1f error=%r",
                self.model_name,
                elapsed_seconds,
                e,
            )
            return AiContent(result=f"AI analysis failed: {e}")
        finally:
            heartbeat_stop.set()
