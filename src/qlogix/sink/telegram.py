import httpx

from qlogix.analyze.base import AnalyzeBaseContent
from qlogix.config import TelegramSinkConfig, get_sink_config
from qlogix.sink.base import Sink


class TelegramSink(Sink):
    def __init__(self):
        config = next((x for x in get_sink_config() if x.type == "telegram"), TelegramSinkConfig())

        self.token = config.token
        self.chat_id = config.chat_id

    def __escape_markdown(self, text: str) -> str:
        # Escape special characters for Telegram MarkdownV2
        escape_chars = r"_*[]()~`>#+-=|{}.!"
        return "".join(f"\\{c}" if c in escape_chars else c for c in text)

    def __send_message(self, message: str):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": self.__escape_markdown(message),
            "parse_mode": "MarkdownV2",
        }
        httpx.post(url, json=payload)

    def write(self, content: AnalyzeBaseContent):
        payload = content.model_dump_json(ensure_ascii=False)
        self.__send_message(payload)
