from qlogix.utils.utils import camel_to_snake, get_current_date


class DateFormat:
    FILENAME = "%Y%m%d-%H%M%S"
    REPORT = "%Y-%m-%d"


__all__ = ["camel_to_snake", "get_current_date", "DateFormat"]
