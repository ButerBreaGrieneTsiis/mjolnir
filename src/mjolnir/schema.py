from dataclasses import dataclass
import datetime as dt
from typing import ClassVar, Dict, List

from mjolnir.constantes import *
from mjolnir.enums import OefeningType, RepetitieType, GewichtType, SetType, Oefening, Status, SetGroepType
from mjolnir.register import GeregistreerdObject, Register
from mjolnir.setcode import Setcode

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

@dataclass
class Schema(GeregistreerdObject):
    
    naam: str
    weken: int
    dagen: int
    status: Status = Status.GEPLAND
    datum_begin: dt.date | None = None
    datum_eind: dt.date | None = None
    oefeningen: Dict[str, Dict[str, List[Sjabloon]]] | None = None
    trainingsgewichten: List[Dict[str, Oefening | float]] | None = None
    sessies: Dict[str, Dict[str, dt.date]] | None = None
    
    BESTANDSNAAM: ClassVar[str] = "schema"
    
    def __repr__(self) -> str:
        return f"{self.naam} ({self.status.value})"
    
    @classmethod
    def nieuw(
        cls,
        velden,
        ) -> "Schema":
        
        schema = super().nieuw(velden)
        
        oefeningen = {}
        trainingsgewichten = []
        sessies = {}
        
        for week in range(1, schema.weken + 1):
            sessies[f"week {week}"] = {}
            for dag in range(1, schema.dagen + 1):
                sessies[f"week {week}"][f"dag {dag}"] = {
                    "datum": None,
                    "status": Status.GEPLAND,
                    }
        
        for dag in range(1, schema.dagen + 1):
            
            oefeningen[f"dag {dag}"] = []
            
            print(f"\ntoevoegen oefeningen voor dag {dag}")
            
            while True:
                
                if len(oefeningen[f"dag {dag}"]) > 0:
                    print(f"\nschema voor dag {dag}")
                    for oefening_sjablonen in oefeningen[f"dag {dag}"]:
                        print(f"  oefening \"{oefening_sjablonen["oefening"].naam}\"")
                        for sjabloon_uuid in oefening_sjablonen["sjablonen"]:
                            print(f"    {Register().sjablonen[sjabloon_uuid]}")
                    
                    if invoer_kiezen(
                        beschrijving = "nog een oefening toevoegen?",
                        keuzes = {"ja": False, "nee": True},
                        kies_een = False,
                        ):
                        
                        break
                
                oefening_type = invoer_kiezen(
                    beschrijving = "oefeningstype",
                    keuzes = {oefening_type.naam: oefening_type for oefening_type in OefeningType},
                    )
                
                oefening = invoer_kiezen(
                    beschrijving = "oefening",
                    keuzes = {oefening.naam: oefening for oefening in Oefening if oefening.oefening_type == oefening_type},
                    )
                
                print(f"\n>>> oefening \"{oefening.naam}\" gekozen")
                
                oefening_sjablonen = {
                    "oefening": oefening,
                    "sjablonen": [],
                    }
                
                while True:
                    
                    if len(oefening_sjablonen["sjablonen"]) > 0:
                        print(f"\nsjablonen voor {oefening.naam}")
                        for sjabloon_uuid in oefening_sjablonen["sjablonen"]:
                            print(f"    {Register().sjablonen[sjabloon_uuid]}")
                        
                        if invoer_kiezen(
                            beschrijving = "nog een sjabloon toevoegen?",
                            keuzes = {"ja": False, "nee": True},
                            kies_een = False,
                            ):
                            
                            break
                    
                    setgroep_type = invoer_kiezen(
                        beschrijving = "setgroep",
                        keuzes = {setgroep_type.value: setgroep_type for setgroep_type in SetGroepType},
                        )
                    
                    sjabloon_uuid = Register().sjablonen.filter(
                        weken = [0, schema.weken],
                        setgroep_type = setgroep_type,
                        gewicht_type = oefening_type.gewicht_types,
                        ).kiezen()
                    sjabloon = Register().sjablonen[sjabloon_uuid]
                    
                    oefening_sjablonen["sjablonen"].append(sjabloon_uuid)
                    
                    if sjabloon.gewicht_type == GewichtType.PERCENTAGE:
                        
                        if not any([oefening == trainingsgewicht["oefening"] for trainingsgewicht in trainingsgewichten]):
                        
                            print(f"\ntrainingsgewicht nodig voor oefening \"{oefening.naam}\"")
                            
                            trainingsgewicht = invoer_validatie(
                                beschrijving = "trainingsgewicht",
                                type = float,
                                bereik = (0.0, GEWICHT_AANTAL_MAX),
                                )
                            
                            trainingsgewichten.append({
                                "oefening": oefening,
                                "trainingsgewicht": trainingsgewicht,
                                })
                
                oefeningen[f"dag {dag}"].append(oefening_sjablonen)
        
        schema.oefeningen = oefeningen
        schema.trainingsgewichten = trainingsgewichten
        schema.sessies = sessies
        
        if len(Register().schema.filter(status = Status.HUIDIG)) == 0:
            schema.status = Status.HUIDIG
        
        return schema

Register.TYPES["sjablonen"] = {
    "type": Sjabloon,
    "decoder": Sjabloon.van_json,
    "encoder": Sjabloon.naar_json,
    }
Register.TYPES["schema"] = {
    "type": Schema,
    "decoder": Schema.van_json,
    "encoder": Schema.naar_json,
    }