"""
Module mjolnir.kern bevat alle basisfunctionaliteiten voor Mjölnir die in alle submodules gebruikt worden.
"""
from .config import CONFIG
from .setcode import Setcode


__all__ = [
    "CONFIG",
    "Setcode",
    ]