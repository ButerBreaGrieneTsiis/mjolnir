from dataclasses import dataclass
from typing import ClassVar, Dict, List

from mjolnir.basis import GeregistreerdObject, Setcode
from mjolnir.basis.constantes import *
from mjolnir.basis.enums import RepetitieType, GewichtType, SetType, SetGroepType

from grienetsiis import invoer_validatie, invoer_kiezen


@dataclass
class Sjabloon(GeregistreerdObject):
    
    naam: str
    setgroep_type: SetGroepType
    gewicht_type: GewichtType
    set_type: SetType
    weken: int = 0
    setcodes: Dict[str, List[Setcode]] | None = None
    
    BESTANDSNAAM: ClassVar[str] = "sjablonen"
    
    def __repr__(self) -> str:
        return f"{self.naam} (setgroep \"{self.setgroep_type.value}\", gewichttype \"{self.gewicht_type.value}\")"
    
    @classmethod
    def nieuw(
        cls,
        velden,
        ):
        
        sjabloon = super().nieuw(velden)
        
        def setcodes_maken(
            gewicht_type: GewichtType,
            set_type: SetType,
            ) -> List[Setcode]:
            
            setcodes = []
            
            while True:
                
                if len(setcodes) > 0:
                    
                    print("\nde huidige sets:")
                    [print(f"  {setcode}") for setcode in setcodes]
                    
                    if invoer_kiezen(
                        beschrijving = "nog een set toevoegen?",
                        keuzes = {"ja": False, "nee": True},
                        kies_een = False,
                        ):
                        
                        break
                
                setcode_dict = {
                    "set_type": set_type,
                    "gewicht_type": gewicht_type,
                    }
                
                if set_type == SetType.AANTAL:
                    setcode_dict["set_aantal"] = invoer_validatie(
                        beschrijving = "aantal sets",
                        type = int,
                        bereik = (1, SET_AANTAL_MAX),
                        )
                elif set_type == SetType.AMSAP:
                    setcode_dict["set_aantal"] = invoer_validatie(
                        beschrijving = "minimaal aantal sets",
                        type = int,
                        bereik = (1, SET_AANTAL_MAX),
                        )
                
                setcode_dict["repetitie_type"] = invoer_kiezen(
                    beschrijving = "repetitie type",
                    keuzes = {repetitie_type.value: repetitie_type for repetitie_type in RepetitieType},
                    )
                
                if setcode_dict["repetitie_type"] == RepetitieType.AANTAL:
                    setcode_dict["repetitie_aantal"] = invoer_validatie(
                        beschrijving = "aantal repetities",
                        type = int,
                        bereik = (1, REPETITIE_AANTAL_MAX),
                        )
                elif setcode_dict["repetitie_type"] == RepetitieType.AMRAP:
                    setcode_dict["repetitie_aantal"] = invoer_validatie(
                        beschrijving = "minimaal aantal repetities",
                        type = int,
                        bereik = (1, REPETITIE_AANTAL_MAX),
                        )
                elif setcode_dict["repetitie_type"] in (RepetitieType.BEREIK, RepetitieType.BEREIK_AMRAP):
                    setcode_dict["repetitie_aantal"] = invoer_validatie(
                        beschrijving = "minimaal aantal repetities",
                        type = int,
                        bereik = (1, REPETITIE_AANTAL_MAX),
                        )
                    setcode_dict["repetitie_maximaal"] = invoer_validatie(
                        beschrijving = "maximaal aantal repetities",
                        type = int,
                        bereik = (setcode_dict["repetitie_aantal"] + 1, REPETITIE_AANTAL_MAX),
                        )
                
                if gewicht_type == GewichtType.GEWICHT:
                    setcode_dict["gewicht_aantal"] = invoer_validatie(
                        beschrijving = "hoeveel gewicht",
                        type = float,
                        bereik = (0.0, GEWICHT_AANTAL_MAX),
                        )
                elif gewicht_type == GewichtType.PERCENTAGE:
                    setcode_dict["gewicht_aantal"] = invoer_validatie(
                        beschrijving = "hoeveel percent",
                        type = float,
                        bereik = (0.0, 100.0),
                        )
                
                setcode = Setcode(**setcode_dict)
                setcodes.append(setcode)
                
            return setcodes
        
        weken = invoer_kiezen(
            beschrijving = "hoeveel weken heeft dit sjabloon?",
            keuzes = {
                "weekonafhankelijk": 0,
                "1 week": 1,
                "2 weken": 2,
                "3 weken": 3,
                },
            )
        
        setcodes_per_week = {}
        
        if weken == 0:
            print(f"\nkies de sets voor elke week")
            setcodes = setcodes_maken(sjabloon.gewicht_type, sjabloon.set_type)
            setcodes_per_week[f"week {weken}"] = setcodes
        else:
            for week in range(1, weken + 1):
                
                print(f"\nkies de sets voor week {week}")
                setcodes = setcodes_maken(sjabloon.gewicht_type, sjabloon.set_type)
                setcodes_per_week[f"week {week}"] = setcodes
        
        sjabloon.weken = weken
        sjabloon.setcodes = setcodes_per_week
        
        return sjabloon