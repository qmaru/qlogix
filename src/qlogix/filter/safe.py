import re

from qlogix.filter.base import Filter, FilterStage
from qlogix.source.base import SourceBaseContent


class SafeFilter(Filter):
    stage = FilterStage.PREPROCESS

    RULES = [
        # email=xxx
        (r"(?i)(email|user|username)=([\w\.-]+@[\w\.-]+\.\w+)", r"\1=<EMAIL>"),
        # ip=xxx
        (
            r"(?i)(ip|client_ip|remote_ip)=((?:25[0-5]|2[0-4]\d|1?\d?\d)"
            r"(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3})",
            r"\1=<IP>",
        ),
        # phone=13843347832
        (
            r"(?i)(phone|mobile|tel)=((?:86[- ]?)?1[3-9]\d{9})",
            r"\1=<PHONE>",
        ),
        # token=xxx
        (r"(?i)(token|apikey|x-api-key|api_key|secret|password)=([^\s]+)", r"\1=<SECRET>"),
        # uuid/request_id/trace_id
        (
            r"(?i)(uuid|trace_id|request_id)="
            r"([0-9a-f-]{36})",
            r"\1=<UUID>",
        ),
    ]

    def process(self, events: list[SourceBaseContent]) -> list[SourceBaseContent]:
        for event in events:
            msg = str(event.message)

            for pattern, replacement in self.RULES:
                msg = re.sub(pattern, replacement, msg, flags=re.I)

            event.message = msg

        return events
