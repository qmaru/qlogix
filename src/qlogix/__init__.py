from importlib.metadata import version

try:
    from qlogix._build import __commit__  # type: ignore
except ImportError:
    __commit__ = ""

VERSION = version("qlogix")
FULL_VERSION = f"{VERSION}+{__commit__}" if __commit__ else VERSION

__all__ = [
    "VERSION",
    "FULL_VERSION",
]
