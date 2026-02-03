"""mjolnir.sessie.halter.halterschijf"""
from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar

from grienetsiis.register import GeregistreerdObject


@dataclass
class Halterschijf(GeregistreerdObject):
    
    massa: float
    diameter: int
    aantal: int
    breedte: int
    
    _SUBREGISTER_NAAM: ClassVar[str] = "halterschijven"
    
    def __repr__(self) -> str:
        return f"halterschijf {self.massa} kg Ø{self.diameter}"