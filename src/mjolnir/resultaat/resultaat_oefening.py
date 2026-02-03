"""mjolnir.resultaat.resultaat_oefening"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, TYPE_CHECKING

from grienetsiis.json import Ontcijferaar, Vercijferaar

from mjolnir.kern.enums import Oefening, Status
from mjolnir.resultaat import ResultaatSet

if TYPE_CHECKING:
    from mjolnir.sessie.sessie import SessieOefening


@dataclass
class ResultaatOefening:
    
    oefening: Oefening
    sets: List[ResultaatSet]
    
    ONTCIJFERAAR: ClassVar[Ontcijferaar | None] = None
    VERCIJFERAAR: ClassVar[Vercijferaar | None] = None
    
    # CLASS METHODS
    
    @classmethod
    def van_sessie(
        cls,
        sessie_oefening: SessieOefening,
        ) -> ResultaatOefening:
        
        sets = []
        
        for sessie_setgroep in sessie_oefening.sets.values():
            for sessie_set in sessie_setgroep:
                if sessie_set.status == Status.AFGEROND and sessie_set.repetitie_gedaan > 0:
                    resultaat_set = ResultaatSet.van_sessie(sessie_set)
                    sets.append(resultaat_set)
        
        return cls(
            oefening = sessie_oefening.oefening,
            sets = sets,
            )
    
    @classmethod
    def van_json(
        cls,
        **dict,
        ) -> ResultaatOefening:
        
        return cls(**dict)
    
    # INSTANCE METHODS
    
    def naar_json(self) -> Dict[str, Any]:
        return {
            "oefening": self.oefening,
            "sets": self.sets,
            }
    
    def _tekst(self, links: bool = False) -> str:
        
        repetitie_veld = "repetities_links" if links else "repetities"
        
        if len(set(resultaat_set.gewicht for resultaat_set in self.sets)) == 1 and len(set(getattr(resultaat_set, repetitie_veld) for resultaat_set in self.sets)) == 1:
            if self.sets[0].gewicht is not None:
                return f"{len(self.sets)}x{getattr(self.sets[0], repetitie_veld)}@{self.sets[0].gewicht}"
            return f"{len(self.sets)}x{getattr(self.sets[0], repetitie_veld)}"
        
        if len(set(resultaat_set.gewicht for resultaat_set in self.sets)) == 1:
            if self.sets[0].gewicht is not None:
                return "(" + ", ".join(f"{getattr(resultaat_set, repetitie_veld)}" for resultaat_set in self.sets) + f")@{self.sets[0].gewicht}"
            return  ", ".join(f"{getattr(resultaat_set, repetitie_veld)}" for resultaat_set in self.sets)
        
        if len(set(getattr(resultaat_set, repetitie_veld) for resultaat_set in self.sets)) == 1:
            return f"{len(self.sets)}x{getattr(self.sets[0], repetitie_veld)}@(" + ", ".join(f"{resultaat_set.gewicht}" for resultaat_set in self.sets) + ")"
        
        return ", ".join(resultaat_set._tekst(links) for resultaat_set in self.sets)
    
    # PROPERTIES
    
    @property
    def tekst(self) -> str:
        return self._tekst()
    
    @property
    def tekst_links(self) -> str:
        return self._tekst(links = True)
    
    @property
    def volume(self) -> float | None:
        if self.oefening.gewichtloos:
            return None
        return sum(set.volume for set in self.sets)
    
    @property
    def volume_links(self) -> float | None:
        if self.oefening.gewichtloos:
            return None
        return sum(set.volume_links for set in self.sets)
    
    @property
    def e1rm(self) -> float | None:
        if self.oefening.gewichtloos:
            return None
        return max(set.e1rm for set in self.sets)
    
    @property
    def e1rm_links(self) -> float | None:
        if self.oefening.gewichtloos:
            return None
        return max(set.e1rm_links for set in self.sets)

ResultaatOefening.ONTCIJFERAAR = Ontcijferaar(
    velden = frozenset((
        "oefening",
        "sets",
        )),
    ontcijfer_functie = ResultaatOefening.van_json,
    )
ResultaatOefening.VERCIJFERAAR = Vercijferaar(
    class_naam = "ResultaatOefening",
    vercijfer_functie_naam = "naar_json",
    )