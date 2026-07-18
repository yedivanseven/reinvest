from typing import Any

__all__ = [
    'universe_cb'
]


def universe_cb(call: str, _: Any, error: Exception) -> str:
    """Format log message for reading the universe with fallbacks."""
    msg = '{} trying to read Universe with {}'
    return msg.format(type(error).__name__, call)
