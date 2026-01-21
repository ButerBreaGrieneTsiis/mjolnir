"""
Module mjolnir.kern bevat alle basisfunctionaliteiten voor Mjölnir die in alle submodules gebruikt worden.
"""
from .config import CONFIG
from .register import Register, GeregistreerdObject
from .setcode import Setcode


__all__ = [
    "CONFIG",
    "Register",
    "GeregistreerdObject",
    "Setcode",
    ]