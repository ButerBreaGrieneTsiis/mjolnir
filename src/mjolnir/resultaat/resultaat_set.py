"""mjolnir.resultaat.resultaat_set"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict,  TYPE_CHECKING

from grienetsiis.json import Ontcijferaar, Vercijferaar

from mjolnir.kern.enums import GewichtType

if TYPE_CHECKING:
    from mjolnir.sessie.sessie import SessieSet


@dataclass
class ResultaatSet:
    
    repetities: int
    repetities_links: int | None = None
    gewicht: float | None = None
    
    ONTCIJFERAAR: ClassVar[Ontcijferaar | None] = None
    VERCIJFERAAR: ClassVar[Vercijferaar | None] = None
    
    # CLASS METHODS
    
    @classmethod
    def van_sessie(
        cls,
        sessie_set: SessieSet,
        ) -> ResultaatSet:
        
        repetities_links = sessie_set.repetitie_links_gedaan if sessie_set.oefening.dextraal else None
        gewicht_gedaan = None if sessie_set.gewicht_type == GewichtType.GEWICHTLOOS else sessie_set.gewicht_gedaan
        
        return cls(
            repetities = sessie_set.repetitie_gedaan,
            repetities_links = repetities_links,
            gewicht = gewicht_gedaan,
            )
    
    @classmethod
    def van_json(
        cls,
        **dict,
        ) -> ResultaatSet:
        
        return cls(**dict)
    
    # INSTANCE METHODS
    
    def naar_json(self) -> Dict[str, Any]:
        return {veld: waarde for veld, waarde in self.__dict__.items() if waarde is not None}
    
    def _tekst(self, links: bool = False) -> str:
        
        repetitie_veld = "repetities_links" if links else "repetities"
        
        if self.gewicht is None:
            return f"{getattr(self, repetitie_veld)}"
        
        gewicht_tekst = f"{self.gewicht:.2f}"
        if gewicht_tekst[-2:] == "00":
            return f"{getattr(self, repetitie_veld)}@{gewicht_tekst[:-3]}"
        if gewicht_tekst[-1] == "0":
            return f"{getattr(self, repetitie_veld)}@{gewicht_tekst[:-1]}"
        return f"{getattr(self, repetitie_veld)}@{gewicht_tekst}"
    
    # PROPERTIES
    
    @property
    def tekst(self) -> str:
        return self._tekst()
    
    @property
    def tekst_links(self) -> str:
        return self._tekst(links = True)
    
    @property
    def volume(self) -> float | None:
        if self.gewicht is None:
            return None
        return self.gewicht * self.repetities
    
    @property
    def volume_links(self) -> float | None:
        if self.gewicht is None:
            return None
        return self.gewicht * self.repetities_links
    
    @property
    def e1rm(self) -> float | None:
        if self.gewicht is None:
            return None
        return round(self.gewicht * (1 + self.repetities/30), 2)
    
    @property
    def e1rm_links(self) -> float | None:
        if self.gewicht is None:
            return None
        return round(self.gewicht * (1 + self.repetities_links/30), 2)

ResultaatSet.ONTCIJFERAAR = Ontcijferaar(
    velden = frozenset((
        "repetities",
        "repetities_links",
        "gewicht",
        )),
    ontcijfer_functie = ResultaatSet.van_json,
    )
ResultaatSet.VERCIJFERAAR = Vercijferaar(
    class_naam = "ResultaatSet",
    vercijfer_functie_naam = "naar_json",
    )