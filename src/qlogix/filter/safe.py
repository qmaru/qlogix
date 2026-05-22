import re
from collections.abc import Callable
from typing import Match

from qlogix.filter.base import Filter, FilterType
from qlogix.source.base import SourceBaseContent

Replacement = str | Callable[[Match[str]], str]


class SafeFilter(Filter):
    stage = FilterType.MODIFY

    @staticmethod
    def _mask_phone(m: Match[str]) -> str:
        prefix = m.group(1)
        value = m.group(2)
        suffix = m.group(3)

        digits = re.sub(r"\D", "", value)

        if len(digits) < 7:
            return m.group(0)

        masked_digits = digits[:3] + "*" * max(len(digits) - 7, 0) + digits[-4:]

        if value.strip().startswith("+"):
            masked_digits = "+" + masked_digits

        return f"{prefix}{masked_digits}{suffix}"

    @staticmethod
    def _mask_email(m: Match[str]) -> str:
        prefix = m.group(1)
        value = m.group(2)
        suffix = m.group(3)

        name, domain = value.split("@", 1)

        masked = f"{name[:1]}***@{domain}"

        return f"{prefix}{masked}{suffix}"

    @staticmethod
    def _mask_ip(m: Match[str]) -> str:
        prefix = m.group(1)
        value = m.group(2)
        suffix = m.group(3)

        parts = value.split(".")

        masked = f"{parts[0]}.***.***.{parts[-1]}"

        return f"{prefix}{masked}{suffix}"

    @staticmethod
    def _mask_user_id(m: Match[str]) -> str:
        prefix = m.group(1)
        value = m.group(2)
        suffix = m.group(3)

        if len(value) <= 4:
            masked = "***"
        else:
            masked = value[:1] + "***" + value[-2:]

        return f"{prefix}{masked}{suffix}"

    RULES: list[tuple[re.Pattern[str], Replacement]] = [
        # email
        (
            re.compile(
                r'("?(?:email)"?\s*[:=]\s*"?)'
                r"([\w\.-]+@[\w\.-]+\.\w+)"
                r'("?)',
                re.I,
            ),
            _mask_email.__func__,
        ),
        # phone
        (
            re.compile(
                r'("?(?:phone|mobile|tel)"?\s*[:=]\s*"?)'
                r"((?:86[- ]?)?1[3-9]\d{9})"
                r'("?)',
                re.I,
            ),
            _mask_phone.__func__,
        ),
        # ip
        (
            re.compile(
                r'("?(?:ip|client_ip|remote_ip)"?\s*[:=]\s*"?)'
                r"((?:25[0-5]|2[0-4]\d|1?\d?\d)"
                r"(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3})"
                r'("?)',
                re.I,
            ),
            _mask_ip.__func__,
        ),
        # userId
        (
            re.compile(
                r'("?(?:userId|user_id)"?\s*[:=]\s*"?)'
                r"([A-Za-z0-9_-]+)"
                r'("?)',
                re.I,
            ),
            _mask_user_id.__func__,
        ),
        # key
        (
            re.compile(
                r'("?(?:token|api-key|apikey|api_key|secret|password|authorization|cookie|session|jwt)"?'
                r'\s*[:=]\s*"?)'
                r'([^\s",}]+)'
                r'("?)',
                re.I,
            ),
            r"\1<SECRET>\3",
        ),
    ]

    def process(self, events: list[SourceBaseContent]) -> list[SourceBaseContent]:
        for event in events:
            msg = str(event.message)

            for pattern, replacement in self.RULES:
                msg = pattern.sub(replacement, msg)

            event.message = msg

        return events
