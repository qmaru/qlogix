import re
from datetime import datetime

from qlogix.config import env
from qlogix.filter.base import Filter, FilterType
from qlogix.source.base import SourceBaseContent
from qlogix.utils import get_current_date


class TodayFilter(Filter):
    stage = FilterType.SELECT

    _datetime_patterns: list[tuple[str, str]] = [
        # ISO
        (r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", "%Y-%m-%dT%H:%M:%S"),
        # 2026-05-22 12:01:33
        (
            r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
            "%Y-%m-%d %H:%M:%S",
        ),
        # 2026/05/22 12:01:33
        (r"\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}", "%Y/%m/%d %H:%M:%S"),
        # date
        (r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d"),
    ]

    _nginx_pattern = (
        r"\d{2}/[A-Za-z]{3}/\d{4}:"
        r"\d{2}:\d{2}:\d{2}\s+[+-]\d{4}"
    )

    _timestamp_pattern = r"\b\d{10,13}\b"

    def _get_target_date(self):
        value = env.QLOGIX_FILTER_DATE

        if not value:
            return datetime.now().date()

        try:
            return datetime.strptime(value, "%Y-%m-%d").date()

        except ValueError:
            raise ValueError(f"{env.key('QLOGIX_FILTER_DATE')} must be YYYY-MM-DD")

    def process(self, events: list[SourceBaseContent]) -> list[SourceBaseContent]:
        current = get_current_date()

        result: list[SourceBaseContent] = []

        for event in events:
            dt = self._extract_datetime(str(event.message))

            if dt and dt.date() == current.date():
                result.append(event)

        return result

    def _extract_datetime(self, text: str) -> datetime | None:
        # unix timestamp
        m = re.search(self._timestamp_pattern, text)

        if m:
            try:
                ts = int(m.group())

                # ms → s
                if len(m.group()) == 13:
                    ts /= 1000

                return datetime.fromtimestamp(ts)

            except Exception:
                pass

        # nginx/apache
        m = re.search(self._nginx_pattern, text)

        if m:
            try:
                value = m.group()
                value = value.replace(":", " ", 1)

                return datetime.strptime(value, "%d/%b/%Y %H:%M:%S %z")

            except Exception:
                pass

        for pattern, fmt in self._datetime_patterns:
            m = re.search(pattern, text)

            if not m:
                continue

            try:
                return datetime.strptime(m.group(), fmt)

            except Exception:
                continue

        return None
