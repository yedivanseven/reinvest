import time
from typing import Any
from functools import cached_property
import numpy as np
from swak.misc import ArgRepr
from ..config import config

__all__ = [
    'Waiter',
    'wait',
]


class Waiter(ArgRepr):
    """Sleep for a random number of seconds on each instance call.

    The waiting time in seconds is drawn from an exponential distribution.

    Parameters
    ----------
    mean: float
        The mean value of seconds to wait for.
    seed: int, optional
        The random number generator seed. Defaults to ``None``.

    """

    def __init__(self, mean: float, seed: int | None = None) -> None:
        super().__init__(mean, seed)
        self.mean = mean
        self.seed = seed

    @cached_property
    def rng(self) -> np.random.Generator:
        """Reusable instance of a numpy random number generator."""
        return np.random.default_rng(self.seed)

    def __call__(self, *args: Any) -> None:
        """Sleep for a randomly number of seconds, ignoring any args given."""
        seconds = self.rng.exponential(self.mean)
        time.sleep(seconds)


wait = Waiter(config.etl.wait)
