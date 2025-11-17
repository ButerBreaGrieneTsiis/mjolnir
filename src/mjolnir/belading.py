from functools import cache
from pathlib import Path
from typing import Callable, List

from .enums import HalterType
# from .gegevensdrager import BasisType, DatabankLijst
from ._register import BasisType, Register

class Halterschijf(BasisType):
    
    VELDEN: dict[str, type] = {
        "massa": float,
        "diameter": int,
        "aantal": int,
        "breedte": int,
        # "id": str,
        }
    
    def __init__(
        self,
        massa: float,
        diameter: int,
        aantal: int,
        breedte: int,
        # id: str = None,
        ) -> "Halterschijf":
        
        self.massa = massa
        self.diameter = diameter
        self.aantal = aantal
        self.breedte = breedte

class Halterschijven(Register):
    
    BESTANDSNAAM: str = "halterschijven"
    TYPE: type = Halterschijf

# class Halterstang(BasisType):
    
#     def __init__(
#         self,
#         naam: str,
#         halter_type: HalterType,
#         massa: float,
#         diameter: int,
#         opname_breedte: int,
#         ) -> "Halterstang":
        
#         self.naam = naam
#         self.halter_type = halter_type
#         self.massa = massa
#         self.diameter = diameter
#         self.opname_breedte = opname_breedte
    
#     def laden(
#         self,
#         haltermassa: float,
#         halterschijven: List[Halterschijf] = None,
#         ) -> "Halter":
        
#         halterschijven = Halterschijven.openen() if halterschijven is None else halterschijven
#         halterschijven.sort(key = lambda x: x.massa, reverse = True)
        
#         massa_per_kant_nodig = (haltermassa - self.massa)/2
#         ruimte_over = self.opname_breedte
        
#         halterschijven_links = []
#         halterschijven_rechts = []
        
#         for halterschijf in halterschijven:
#             for _ in range(halterschijf.aantal//2):
#                 if halterschijf.massa <= round(massa_per_kant_nodig * 0.8)/0.8 and ruimte_over > halterschijf.breedte:
#                     halterschijven_links.append(halterschijf)
#                     halterschijven_rechts.append(halterschijf)
#                     massa_per_kant_nodig -= halterschijf.massa
#                     ruimte_over -= halterschijf.breedte
#                 else:
#                     continue
        
#         return Halter(
#             self,
#             halterschijven_links,
#             halterschijven_rechts,
#             )

# class Halterstangen(DatabankLijst):
    
#     BESTANDSNAAM: str = "halterstangen"
#     DECODER_FUNCTIE: Callable = Halterstang.van_json
#     ENCODER_FUNCTIE: Callable = Halterstang.naar_json

# class Halter:
    
#     def __init__(
#         self,
#         halterstang: Halterstang,
#         halterschijven_links: List[Halterschijf] = None,
#         halterschijven_rechts: List[Halterschijf] = None,
#         ) -> "Halter":
        
#         self.halterstang = halterstang
#         self.halterschijven_links = halterschijven_links
#         self.halterschijven_rechts = halterschijven_rechts
    
#     @property
#     def massa(self) -> float:
        
#         return self.halterstang.massa + \
#             sum([halterschijf.massa for halterschijf in self.halterschijven_links]) + \
#             sum([halterschijf.massa for halterschijf in self.halterschijven_rechts])
