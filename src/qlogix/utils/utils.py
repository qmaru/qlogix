import re
from datetime import datetime

from qlogix.config import env


def camel_to_snake(name: str):
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)
    return name.lower()


def get_current_date() -> datetime:
    now = datetime.now()

    env_date = env.QLOGIX_FILTER_DATE
    if env_date:
        try:
            override = datetime.strptime(env_date, "%Y-%m-%d")
            now = now.replace(year=override.year, month=override.month, day=override.day)
        except ValueError:
            raise ValueError(
                f"{env.key('QLOGIX_FILTER_DATE')} invalid: {env_date}, expected YYYY-MM-DD"
            ) from None

    return now
