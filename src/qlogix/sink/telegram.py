import httpx

from qlogix.analyze.base import AnalyzeBaseContent
from qlogix.config import TelegramSinkConfig, get_sink_config
from qlogix.sink.base import Sink


class TelegramSink(Sink):
    def __init__(self):
        config = next((x for x in get_sink_config() if x.type == "telegram"), TelegramSinkConfig())

        self.token = config.token
        self.chat_id = config.chat_id

    def __send_message(self, message: str):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
        }
        httpx.post(url, json=payload)

    def write(self, content: AnalyzeBaseContent):
        message = content.result
        self.__send_message(message)
