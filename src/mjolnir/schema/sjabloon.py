from dataclasses import dataclass
from typing import ClassVar, Dict, List

from grienetsiis.opdrachtprompt import invoeren, kiezen
from grienetsiis.register import GeregistreerdObject

from mjolnir.kern import CONFIG, Setcode
from mjolnir.kern.enums import RepetitieType, GewichtType, SetType, SetGroepType


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
                    
                    if kiezen(
                        opties = {"ja": False, "nee": True},
                        tekst_beschrijving = "nog een set toevoegen?",
                        tekst_kies_een = False,
                        ):
                        
                        break
                
                setcode_dict = {
                    "set_type": set_type,
                    "gewicht_type": gewicht_type,
                    }
                
                if set_type == SetType.AANTAL:
                    setcode_dict["set_aantal"] = invoeren(
                        tekst_beschrijving = "aantal sets",
                        invoer_type = int,
                        waardes_bereik = (1, CONFIG["SET_AANTAL_MAX"]),
                        )
                elif set_type == SetType.AMSAP:
                    setcode_dict["set_aantal"] = invoeren(
                        tekst_beschrijving = "minimaal aantal sets",
                        invoer_type = int,
                        waardes_bereik = (1, CONFIG["SET_AANTAL_MAX"]),
                        )
                
                setcode_dict["repetitie_type"] = kiezen(
                    opties = {repetitie_type.value: repetitie_type for repetitie_type in RepetitieType},
                    tekst_beschrijving = "repetitie type",
                    )
                
                if setcode_dict["repetitie_type"] == RepetitieType.AANTAL:
                    setcode_dict["repetitie_aantal"] = invoeren(
                        tekst_beschrijving = "aantal repetities",
                        invoer_type = int,
                        waardes_bereik = (1, CONFIG["REPETITIE_AANTAL_MAX"]),
                        )
                elif setcode_dict["repetitie_type"] == RepetitieType.AMRAP:
                    setcode_dict["repetitie_aantal"] = invoeren(
                        tekst_beschrijving = "minimaal aantal repetities",
                        invoer_type = int,
                        waardes_bereik = (1, CONFIG["REPETITIE_AANTAL_MAX"]),
                        )
                elif setcode_dict["repetitie_type"] in (RepetitieType.BEREIK, RepetitieType.BEREIK_AMRAP):
                    setcode_dict["repetitie_aantal"] = invoeren(
                        tekst_beschrijving = "minimaal aantal repetities",
                        invoer_type = int,
                        waardes_bereik = (1, CONFIG["REPETITIE_AANTAL_MAX"]),
                        )
                    setcode_dict["repetitie_maximaal"] = invoeren(
                        tekst_beschrijving = "maximaal aantal repetities",
                        invoer_type = int,
                        waardes_bereik = (setcode_dict["repetitie_aantal"] + 1, CONFIG["REPETITIE_AANTAL_MAX"]),
                        )
                
                if gewicht_type == GewichtType.GEWICHT:
                    setcode_dict["gewicht_aantal"] = invoeren(
                        tekst_beschrijving = "hoeveel gewicht",
                        invoer_type = float,
                        waardes_bereik = (0.0, CONFIG["GEWICHT_AANTAL_MAX"]),
                        )
                elif gewicht_type == GewichtType.PERCENTAGE:
                    setcode_dict["gewicht_aantal"] = invoeren(
                        tekst_beschrijving = "hoeveel percent",
                        invoer_type = float,
                        waardes_bereik = (0.0, 100.0),
                        )
                
                setcode = Setcode(**setcode_dict)
                setcodes.append(setcode)
                
            return setcodes
        
        weken = kiezen(
            opties = {
                "weekonafhankelijk": 0,
                "1 week": 1,
                "2 weken": 2,
                "3 weken": 3,
                },
            tekst_beschrijving = "hoeveel weken heeft dit sjabloon?",
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