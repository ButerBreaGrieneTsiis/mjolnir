from dataclasses import dataclass
from typing import ClassVar, List

from mjolnir.enums import HalterType
from mjolnir.register import GeregistreerdObject, Register


@dataclass
class Halterschijf(GeregistreerdObject):
    
    massa: float
    diameter: int
    aantal: int
    breedte: int
    
    BESTANDSNAAM: ClassVar[str] = "halterschijven"
    
    def __repr__(self) -> str:
        return f"halterschijf {self.massa} kg Ø{self.diameter}"
    
@dataclass
class Halterstang(GeregistreerdObject):
    
    naam: str
    halter_type: HalterType
    massa: float
    diameter: int
    opname_breedte: int
    
    BESTANDSNAAM: ClassVar[str] = "halterstangen"
    
    def __repr__(self) -> str:
        return f"halterstang \"{self.naam}\" van type \"{self.halter_type.value}\""
    
    def laden(
        self,
        haltermassa: float,
        halterschijven: List[Halterschijf] = None,
        ) -> "Halter":
        
        halterschijven = Halterschijven.openen().lijst if halterschijven is None else halterschijven
        halterschijven.sort(key = lambda x: x.massa, reverse = True)
        
        massa_per_kant_nodig = (haltermassa - self.massa)/2
        ruimte_over = self.opname_breedte
        
        halterschijven_links = []
        halterschijven_rechts = []
        
        for halterschijf in halterschijven:
            for _ in range(halterschijf.aantal//2):
                if halterschijf.massa <= round(massa_per_kant_nodig * 0.8)/0.8 and ruimte_over > halterschijf.breedte:
                    halterschijven_links.append(halterschijf)
                    halterschijven_rechts.append(halterschijf)
                    massa_per_kant_nodig -= halterschijf.massa
                    ruimte_over -= halterschijf.breedte
                else:
                    continue
        
        return Halter(
            self,
            halterschijven_links,
            halterschijven_rechts,
            )

class Halter:
    
    def __init__(
        self,
        halterstang: Halterstang,
        halterschijven_links: List[Halterschijf] = None,
        halterschijven_rechts: List[Halterschijf] = None,
        ) -> "Halter":
        
        self.halterstang = halterstang
        self.halterschijven_links = halterschijven_links
        self.halterschijven_rechts = halterschijven_rechts
    
    def __repr__(self):
        links = "".join([f"[{halterschijf.massa}]" for halterschijf in sorted(self.halterschijven_links, key = lambda x: x.massa)])
        rechts = "".join([f"[{halterschijf.massa}]" for halterschijf in self.halterschijven_rechts])
        return f"{links}---[{self.halterstang.naam}]---{rechts}"
    
    @property
    def massa(self) -> float:
        
        return self.halterstang.massa + \
            sum([halterschijf.massa for halterschijf in self.halterschijven_links]) + \
            sum([halterschijf.massa for halterschijf in self.halterschijven_rechts])

Register.DECODERS["halterstangen"] = {
    "class": Halterstang,
    "decoder_functie": Halterstang.van_json,
    }
Register.ENCODERS["halterstangen"] = {
    "class": Halterstang,
    "encoder_functie": Halterstang.naar_json,
    }
Register.DECODERS["halterschijven"] = {
    "class": Halterschijf,
    "decoder_functie": Halterschijf.van_json,
    }
Register.ENCODERS["halterschijven"] = {
    "class": Halterschijf,
    "encoder_functie": Halterschijf.naar_json,
    }