from qlogix.analyze.base import AnalyzeBaseContent
from qlogix.config import TelegramSinkConfig, get_sink_config
from qlogix.sink.base import Sink


class TelegramSink(Sink):
    def __init__(self):
        config = next((sink for sink in get_sink_config() if sink.type == "telegram"), None)
        if not isinstance(config, TelegramSinkConfig):
            raise ValueError("telegram sink config not found")

        self.token = config.resolved_token
        self.chat_id = config.resolved_chat_id

    def write(self, content: AnalyzeBaseContent):
        pass
