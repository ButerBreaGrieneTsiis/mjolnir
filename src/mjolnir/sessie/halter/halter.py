"""mjolnir.sessie.halter.halter"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from mjolnir.sessie.halter import Halterschijf, Halterstang


@dataclass
class Halter: 
    
    halterstang: Halterstang
    halterschijven_links: List[Halterschijf] = None
    halterschijven_rechts: List[Halterschijf] = None
    
    def __repr__(self):
        links = "".join([f"[{halterschijf.massa}]" for halterschijf in reversed(self.halterschijven_links)])
        rechts = "".join([f"[{halterschijf.massa}]" for halterschijf in self.halterschijven_rechts])
        return f"{links}---[{self.halterstang.naam}]---{rechts}"
    
    @property
    def massa(self) -> float:
        
        return self.halterstang.massa + \
            sum([halterschijf.massa for halterschijf in self.halterschijven_links]) + \
            sum([halterschijf.massa for halterschijf in self.halterschijven_rechts])