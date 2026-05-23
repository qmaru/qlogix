from functools import partial

import httpx

from qlogix.analyze.base import AnalyzeBaseContent
from qlogix.config import TelegramSinkConfig, get_sink_config
from qlogix.logutil import get_logger, log_external_call
from qlogix.sink.base import Sink

logger = get_logger(__name__)


class TelegramSink(Sink):
    def __init__(self, config: TelegramSinkConfig | None = None):
        if config is None:
            config = next((x for x in get_sink_config() if x.type == "telegram"), None)
            if config is None:
                raise ValueError("Telegram sink config not found")

        self.token = config.token
        self.chat_id = config.chat_id

    def __send_message(self, message: str):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "link_preview_options": {"is_disabled": True},
        }

        try:
            response = log_external_call(
                logger, "telegram.send_message", partial(httpx.post, url, json=payload, timeout=30)
            )
            response.raise_for_status()

        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to send telegram message: {e}") from None

    def write(self, content: AnalyzeBaseContent):
        message = content.result
        self.__send_message(message)
